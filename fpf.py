#!/usr/bin/env python3

import argparse
import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_SPEC_URL = "https://raw.githubusercontent.com/ailev/FPF/refs/heads/main/FPF-Spec.md"
DEFAULT_WORK_DIR = Path("FPF")
DEFAULT_SPEC_NAME = "FPF-Spec.md"
DEFAULT_LITE_NAME = "FPF-Spec-Lite.md"
DEFAULT_AGGRESSIVE_NAME = "FPF-Spec-Aggressive.md"
DEFAULT_PARTS_MANIFEST = "FPF-Parts-Manifest.yaml"
DEFAULT_PROFILES_DIR = Path("profiles")


@dataclass(frozen=True)
class CompressionStats:
    removed_counts: dict[str, int]
    original_lines: int
    new_lines: int

    @property
    def reduction_percent(self) -> float:
        if self.original_lines == 0:
            return 0.0
        return round((1 - self.new_lines / self.original_lines) * 100, 1)


def normalize_text(text: str) -> str:
    text = text.replace("\u2011", "-")
    text = text.replace("\u2013", "-")
    text = text.replace("\u2014", "-")
    text = text.replace("\u00A0", " ")
    return text


def compress_fpf(input_path: Path, output_path: Path, aggressive: bool) -> CompressionStats:
    remove_keywords = [
        "SoTA-Echoing",
        "SOTA-Echoing",
        "SoTA Echoing",
        "SOTA Echoing",
        "State-of-the-Art alignment",
    ]

    if aggressive:
        remove_keywords.extend(
            [
                "Problem frame",
                "Problem",
                "Forces",
                "Rationale",
                "Anti-patterns",
            ]
        )

    header_pattern = re.compile(r"^(#+)\s+(.*)")
    start_marker_pattern = re.compile(r"^#+\s+(Part A|A\.0)", re.IGNORECASE)

    try:
        input_file = input_path.open("r", encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"Input file not found: {input_path}") from exc

    is_content_started = False
    skipping_section = False
    skip_level = 0
    removed_counts = {keyword: 0 for keyword in remove_keywords}
    original_lines = 0
    new_lines = 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with input_file, output_path.open("w", encoding="utf-8") as output_file:
        for line in input_file:
            original_lines += 1
            if not is_content_started:
                if start_marker_pattern.match(line):
                    is_content_started = True
                    output_file.write(line)
                    new_lines += 1
                continue

            match = header_pattern.match(line)
            if match:
                level = len(match.group(1))
                raw_title = match.group(2).strip()
                clean_title = normalize_text(raw_title)

                if skipping_section:
                    if level <= skip_level:
                        skipping_section = False
                    else:
                        continue

                found_keyword = None
                for keyword in remove_keywords:
                    if keyword.lower() in clean_title.lower():
                        found_keyword = keyword
                        break

                if found_keyword and not skipping_section:
                    skipping_section = True
                    skip_level = level
                    removed_counts[found_keyword] += 1
                    continue

            if not skipping_section:
                output_file.write(line)
                new_lines += 1

    return CompressionStats(
        removed_counts=removed_counts,
        original_lines=original_lines,
        new_lines=new_lines,
    )


def print_compression_stats(stats: CompressionStats, output_path: Path) -> None:
    print(f"Stats for {output_path}:")
    print("Removal statistics:")
    for keyword, count in stats.removed_counts.items():
        if count:
            print(f"  - {keyword}: {count} sections")
    print(
        f"Lines: {stats.original_lines} -> {stats.new_lines} "
        f"(Reduction: {stats.reduction_percent:.1f}%)"
    )


def split_fpf(input_path: Path, output_dir: Path) -> list[str]:
    try:
        input_file = input_path.open("r", encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"Input file not found: {input_path}") from exc

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise RuntimeError(f"Failed to write output directory: {output_dir}") from exc
    manifest = []

    def open_output(path: Path):
        try:
            return path.open("w", encoding="utf-8")
        except OSError as exc:
            raise RuntimeError(f"Failed to write output file: {path}") from exc

    part_header_pattern = re.compile(r"^#+\s\**Part\s+([A-Z])", re.IGNORECASE)
    current_name = "FPF-Part-Preface.md"
    manifest.append(current_name)
    current_path = output_dir / current_name
    with input_file:
        current_file = open_output(current_path)
        try:
            for line in input_file:
                normalized_line = normalize_text(line)
                match = part_header_pattern.match(normalized_line)
                if match:
                    part_id = match.group(1).upper()
                    current_file.close()
                    current_name = f"FPF-Part-{part_id}.md"
                    manifest.append(current_name)
                    current_path = output_dir / current_name
                    current_file = open_output(current_path)
                current_file.write(line)
        finally:
            current_file.close()

    manifest_path = output_dir / DEFAULT_PARTS_MANIFEST
    try:
        manifest_text = yaml.safe_dump(
            {"parts": manifest, "baseline_file": input_path.name},
            sort_keys=False,
        )
        manifest_path.write_text(manifest_text, encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Failed to write output file: {manifest_path}") from exc

    return manifest


def resolve_workdir_path(work_dir: Path, value: str, label: str) -> Path:
    path = Path(value)
    if value in {".", ".."} or path.is_absolute() or path.name != value:
        raise RuntimeError(f"{label} must be a filename: {value}")
    return (work_dir / path).resolve(strict=False)


def resolve_profile_path(profile_value: str, profiles_dir: Path) -> Path:
    path = Path(profile_value)
    if path.is_absolute() or path.name != profile_value:
        return path
    if path.suffix:
        return profiles_dir / path
    return profiles_dir / f"{profile_value}.yaml"


def load_yaml_manifest(manifest_path: Path) -> dict[str, object]:
    try:
        text = manifest_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"Manifest file not found: {manifest_path}") from exc
    except OSError as exc:
        raise RuntimeError(f"Failed to read manifest: {manifest_path}") from exc

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise RuntimeError(f"Failed to parse manifest: {manifest_path}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"Manifest must be a mapping: {manifest_path}")

    return data


def count_lines(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return sum(1 for _ in handle)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Part file not found: {path}") from exc
    except OSError as exc:
        raise RuntimeError(f"Failed to read part file: {path}") from exc


def validate_part_paths(part_paths: list[Path]) -> None:
    for part_path in part_paths:
        try:
            with part_path.open("r", encoding="utf-8"):
                pass
        except FileNotFoundError as exc:
            raise RuntimeError(f"Part file not found: {part_path}") from exc
        except OSError as exc:
            raise RuntimeError(f"Failed to read part file: {part_path}") from exc


def assemble_fpf(manifest_path: Path, work_dir: Path) -> tuple[Path, CompressionStats | None]:
    data = load_yaml_manifest(manifest_path)
    output_value = data.get("output_file")
    parts_value = data.get("parts")
    baseline_value = data.get("baseline_file")

    if not isinstance(output_value, str) or not output_value:
        raise RuntimeError(
            f"Manifest file {manifest_path} is missing required field: output_file"
        )
    if not isinstance(parts_value, list):
        raise RuntimeError(
            f"Manifest file {manifest_path} is missing required field: parts"
        )

    output_path = resolve_workdir_path(work_dir, output_value, "Output file")
    part_paths = []
    for raw in parts_value:
        if not isinstance(raw, str) or not raw:
            raise RuntimeError(f"Invalid part entry in manifest: {manifest_path}")
        part_paths.append(resolve_workdir_path(work_dir, raw, "Part filename"))

    validate_part_paths(part_paths)

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise RuntimeError(f"Failed to write output file: {output_path}") from exc

    output_lines = 0
    try:
        with output_path.open("w", encoding="utf-8") as output_file:
            for part_path in part_paths:
                try:
                    with part_path.open("r", encoding="utf-8") as part_file:
                        for line in part_file:
                            output_file.write(line)
                            output_lines += 1
                except FileNotFoundError as exc:
                    raise RuntimeError(f"Part file not found: {part_path}") from exc
                except OSError as exc:
                    raise RuntimeError(f"Failed to read part file: {part_path}") from exc
    except OSError as exc:
        raise RuntimeError(f"Failed to write output file: {output_path}") from exc

    if baseline_value is None:
        print(f"Warning: baseline_file missing in manifest: {manifest_path}", file=sys.stderr)
        return output_path, None

    if not isinstance(baseline_value, str) or not baseline_value:
        raise RuntimeError(f"Invalid baseline_file entry: {manifest_path}")

    try:
        baseline_path = resolve_workdir_path(work_dir, baseline_value, "Baseline file")
        baseline_lines = count_lines(baseline_path)
    except RuntimeError as exc:
        print(f"Warning: {exc}", file=sys.stderr)
        return output_path, None

    stats = CompressionStats(
        removed_counts={},
        original_lines=baseline_lines,
        new_lines=output_lines,
    )
    return output_path, stats


def download_spec(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status} while downloading {url}")
            data = response.read()
    except Exception as exc:
        raise RuntimeError(f"Failed to download spec from {url}: {exc}") from exc

    output_path.write_bytes(data)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fpf-cli",
        description="FPF specification tooling CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    download_parser = subparsers.add_parser(
        "download",
        help="Download the canonical FPF-Spec.md into the local FPF directory.",
    )
    download_parser.add_argument(
        "--url",
        default=DEFAULT_SPEC_URL,
        help="Source URL for FPF-Spec.md.",
    )
    download_parser.add_argument(
        "--work-dir",
        default=None,
        help="Directory for the downloaded spec.",
    )

    strip_lite_parser = subparsers.add_parser(
        "strip-lite",
        help="Generate the lite compressed spec.",
    )
    strip_lite_parser.add_argument(
        "--work-dir",
        default=None,
        help="Working directory for inputs and outputs.",
    )

    strip_parser = subparsers.add_parser(
        "strip",
        help="Generate compressed spec files (lite and aggressive).",
    )
    strip_parser.add_argument(
        "--work-dir",
        default=None,
        help="Working directory for inputs and outputs.",
    )

    strip_aggressive_parser = subparsers.add_parser(
        "strip-aggressive",
        help="Generate the aggressive compressed spec.",
    )
    strip_aggressive_parser.add_argument(
        "--work-dir",
        default=None,
        help="Working directory for inputs and outputs.",
    )

    split_parser = subparsers.add_parser(
        "split",
        help="Split the spec into per-part files.",
    )
    split_parser.add_argument(
        "--work-dir",
        default=None,
        help="Working directory for inputs and outputs.",
    )

    assemble_parser = subparsers.add_parser(
        "assemble",
        help="Assemble a spec from a YAML manifest.",
    )
    assemble_manifest_group = assemble_parser.add_mutually_exclusive_group(required=True)
    assemble_manifest_group.add_argument(
        "--manifest",
        help="Manifest filename in the working directory or a path to the manifest.",
    )
    assemble_manifest_group.add_argument(
        "--profile",
        help="Profile name, filename, or path to the profile manifest. (Experimental). See profiles/ for available profiles.",
    )
    assemble_parser.add_argument(
        "--work-dir",
        default=None,
        help="Working directory for inputs and outputs.",
    )
    assemble_parser.add_argument(
        "--profiles-dir",
        default=None,
        help="Directory for profile manifests.",
    )

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "download":
        work_dir = Path(args.work_dir) if args.work_dir else DEFAULT_WORK_DIR
        output_path = work_dir / DEFAULT_SPEC_NAME
        try:
            download_spec(args.url, output_path)
        except Exception as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Downloaded FPF spec to {output_path}")
        return 0

    if args.command == "split":
        work_dir = Path(args.work_dir) if args.work_dir else DEFAULT_WORK_DIR
        input_path = work_dir / DEFAULT_SPEC_NAME
        output_dir = work_dir
        try:
            split_fpf(input_path, output_dir)
        except Exception as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Wrote {output_dir / DEFAULT_PARTS_MANIFEST}")
        return 0

    if args.command == "assemble":
        work_dir = Path(args.work_dir) if args.work_dir else DEFAULT_WORK_DIR
        if args.profile:
            profiles_dir = Path(args.profiles_dir) if args.profiles_dir else DEFAULT_PROFILES_DIR
            manifest_path = resolve_profile_path(args.profile, profiles_dir)
        else:
            manifest_value = Path(args.manifest)
            manifest_has_path = (
                manifest_value.is_absolute() or manifest_value.name != args.manifest
            )
            if manifest_has_path:
                if args.work_dir:
                    print(
                        f"Warning: manifest path provided; using CLI work-dir {work_dir}",
                        file=sys.stderr,
                    )
                    print(
                        f"Warning: manifest read from path {manifest_value}",
                        file=sys.stderr,
                    )
                else:
                    work_dir = manifest_value.parent
                    print(
                        f"Warning: manifest path provided; using manifest directory {work_dir}",
                        file=sys.stderr,
                    )
                manifest_path = manifest_value
            else:
                manifest_path = work_dir / manifest_value
        try:
            output_path, stats = assemble_fpf(manifest_path, work_dir)
        except Exception as exc:
            print(str(exc), file=sys.stderr)
            return 1
        if stats is not None:
            print_compression_stats(stats, output_path)
        return 0

    if args.command in {"strip", "strip-lite", "strip-aggressive"}:
        work_dir = Path(args.work_dir) if args.work_dir else DEFAULT_WORK_DIR
        input_path = work_dir / DEFAULT_SPEC_NAME

        if args.command == "strip":
            lite_path = work_dir / DEFAULT_LITE_NAME
            aggressive_path = work_dir / DEFAULT_AGGRESSIVE_NAME
            lite_stats = compress_fpf(input_path, lite_path, aggressive=False)
            aggressive_stats = compress_fpf(input_path, aggressive_path, aggressive=True)
            print_compression_stats(lite_stats, lite_path)
            print(f"Wrote {lite_path}")
            print_compression_stats(aggressive_stats, aggressive_path)
            print(f"Wrote {aggressive_path}")
            return 0

        if args.command == "strip-lite":
            output_path = work_dir / DEFAULT_LITE_NAME
            stats = compress_fpf(input_path, output_path, aggressive=False)
            print_compression_stats(stats, output_path)
            print(f"Wrote {output_path}")
            return 0

        if args.command == "strip-aggressive":
            output_path = work_dir / DEFAULT_AGGRESSIVE_NAME
            stats = compress_fpf(input_path, output_path, aggressive=True)
            print_compression_stats(stats, output_path)
            print(f"Wrote {output_path}")
            return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
