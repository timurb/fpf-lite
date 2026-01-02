#!/usr/bin/env python3

import argparse
import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SPEC_URL = "https://raw.githubusercontent.com/ailev/FPF/refs/heads/main/FPF-Spec.md"
DEFAULT_OUTPUT = Path("FPF") / "FPF-Spec.md"
DEFAULT_INPUT = Path("FPF") / "FPF-Spec.md"
DEFAULT_COMPRESSED_DIR = Path("FPF")


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
