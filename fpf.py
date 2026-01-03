#!/usr/bin/env python3

import argparse
import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import yaml
DEFAULT_SPEC_URL = "https://raw.githubusercontent.com/ailev/FPF/refs/heads/main/FPF-Spec.md"
DEFAULT_OUTPUT = Path("FPF") / "FPF-Spec.md"
DEFAULT_INPUT = Path("FPF") / "FPF-Spec.md"
DEFAULT_COMPRESSED_DIR = Path("FPF")
DEFAULT_PARTS_DIR = Path("FPF") / "parts"


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

    manifest_path = output_dir / "FPF-Parts-Manifest.yaml"
    try:
        manifest_text = yaml.safe_dump({"parts": manifest}, sort_keys=False)
        manifest_path.write_text(manifest_text, encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Failed to write output file: {manifest_path}") from exc

    return manifest


def resolve_manifest_path(base_dir: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve(strict=False)


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


def load_baseline_parts(baseline_manifest_path: Path) -> list[tuple[str, Path]]:
    data = load_yaml_manifest(baseline_manifest_path)
    parts = data.get("parts")
    if not isinstance(parts, list):
        raise RuntimeError(f"Baseline manifest missing parts list: {baseline_manifest_path}")
    base_dir = baseline_manifest_path.parent
    entries: list[tuple[str, Path]] = []
    for raw in parts:
        if not isinstance(raw, str) or not raw:
            raise RuntimeError(f"Invalid part entry in baseline manifest: {baseline_manifest_path}")
        entries.append((raw, resolve_manifest_path(base_dir, raw)))
    return entries


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


def assemble_fpf(manifest_path: Path) -> tuple[Path, CompressionStats]:
    data = load_yaml_manifest(manifest_path)
    output_value = data.get("output")
    parts_value = data.get("parts")
    baseline_value = data.get("baseline_manifest")

    if not isinstance(output_value, str) or not output_value:
        raise RuntimeError(f"Manifest missing output path: {manifest_path}")
    if not isinstance(parts_value, list):
        raise RuntimeError(f"Manifest missing parts list: {manifest_path}")
    if not isinstance(baseline_value, str) or not baseline_value:
        raise RuntimeError(f"Manifest missing baseline_manifest: {manifest_path}")

    base_dir = manifest_path.parent
    output_path = resolve_manifest_path(base_dir, output_value)
    part_paths = []
    for raw in parts_value:
        if not isinstance(raw, str) or not raw:
            raise RuntimeError(f"Invalid part entry in manifest: {manifest_path}")
        part_paths.append(resolve_manifest_path(base_dir, raw))
    baseline_manifest_path = resolve_manifest_path(base_dir, baseline_value)

    baseline_entries: list[tuple[str, Path]] | None = None
    try:
        baseline_entries = load_baseline_parts(baseline_manifest_path)
    except RuntimeError as exc:
        print(f"Warning: {exc}", file=sys.stderr)

    if baseline_entries is not None:
        baseline_paths = {path for _, path in baseline_entries}
        for part_path in part_paths:
            if part_path not in baseline_paths:
                raise RuntimeError(f"Part not in baseline manifest: {part_path}")

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

    removed_counts: dict[str, int] = {}
    if baseline_entries is not None:
        baseline_lines = 0
        for raw, path in baseline_entries:
            baseline_lines += count_lines(path)
            if path not in part_paths:
                removed_counts[raw] = removed_counts.get(raw, 0) + 1
    else:
        baseline_lines = output_lines

    stats = CompressionStats(
        removed_counts=removed_counts,
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
        prog="fpf",
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
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Destination path for the downloaded spec.",
    )

    strip_lite_parser = subparsers.add_parser(
        "strip-lite",
        help="Generate the lite compressed spec.",
    )
    strip_lite_parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Source path for the FPF-Spec.md file.",
    )
    strip_lite_parser.add_argument(
        "--output",
        default=str(DEFAULT_COMPRESSED_DIR / "FPF-Spec-Lite.md"),
        help="Output path for the lite compressed spec.",
    )

    strip_parser = subparsers.add_parser(
        "strip",
        help="Generate compressed spec files (lite and aggressive).",
    )
    strip_parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Source path for the FPF-Spec.md file.",
    )
    strip_parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_COMPRESSED_DIR),
        help="Directory for compressed outputs.",
    )

    strip_aggressive_parser = subparsers.add_parser(
        "strip-aggressive",
        help="Generate the aggressive compressed spec.",
    )
    strip_aggressive_parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Source path for the FPF-Spec.md file.",
    )
    strip_aggressive_parser.add_argument(
        "--output",
        default=str(DEFAULT_COMPRESSED_DIR / "FPF-Spec-Aggressive.md"),
        help="Output path for the aggressive compressed spec.",
    )

    split_parser = subparsers.add_parser(
        "split",
        help="Split the spec into per-part files.",
    )
    split_parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Source path for the FPF-Spec.md file.",
    )
    split_parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_PARTS_DIR),
        help="Directory for part outputs.",
    )

    assemble_parser = subparsers.add_parser(
        "assemble",
        help="Assemble a spec from a YAML manifest.",
    )
    assemble_parser.add_argument(
        "--manifest",
        required=True,
        help="Path to the YAML manifest file.",
    )

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "download":
        output_path = Path(args.output)
        try:
            download_spec(args.url, output_path)
        except Exception as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Downloaded FPF spec to {output_path}")
        return 0

    if args.command == "split":
        input_path = Path(args.input)
        output_dir = Path(args.output_dir)
        try:
            split_fpf(input_path, output_dir)
        except Exception as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Wrote {output_dir / 'FPF-Parts-Manifest.yaml'}")
        return 0

    if args.command == "assemble":
        manifest_path = Path(args.manifest)
        try:
            output_path, stats = assemble_fpf(manifest_path)
        except Exception as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print_compression_stats(stats, output_path)
        return 0

    if args.command in {"strip", "strip-lite", "strip-aggressive"}:
        input_path = Path(args.input)

        if args.command == "strip":
            output_dir = Path(args.output_dir)
            lite_path = output_dir / "FPF-Spec-Lite.md"
            aggressive_path = output_dir / "FPF-Spec-Aggressive.md"
            lite_stats = compress_fpf(input_path, lite_path, aggressive=False)
            aggressive_stats = compress_fpf(input_path, aggressive_path, aggressive=True)
            print_compression_stats(lite_stats, lite_path)
            print(f"Wrote {lite_path}")
            print_compression_stats(aggressive_stats, aggressive_path)
            print(f"Wrote {aggressive_path}")
            return 0

        if args.command == "strip-lite":
            output_path = Path(args.output)
            stats = compress_fpf(input_path, output_path, aggressive=False)
            print_compression_stats(stats, output_path)
            print(f"Wrote {output_path}")
            return 0

        if args.command == "strip-aggressive":
            output_path = Path(args.output)
            stats = compress_fpf(input_path, output_path, aggressive=True)
            print_compression_stats(stats, output_path)
            print(f"Wrote {output_path}")
            return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
