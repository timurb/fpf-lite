import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

import fpf


class TestPF5Split(unittest.TestCase):
    def read_manifest_parts(self, manifest_path: Path) -> list[str]:
        parts = []
        in_parts = False
        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped == "parts:":
                in_parts = True
                continue
            if in_parts:
                if stripped.startswith("- "):
                    parts.append(stripped[2:].strip())
                elif stripped and not stripped.startswith("-"):
                    break
        return parts

    def read_manifest_baseline(self, manifest_path: Path) -> str | None:
        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("baseline_file:"):
                return stripped.split(":", 1)[1].strip()
        return None

    def test_split_writes_parts_and_manifest(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            work_dir = Path(tmp_dir)
            input_path = work_dir / "FPF-Spec.md"
            sample = (
                "Preface line 1\n"
                "Preface line 2\n"
                "# Part A\n"
                "A line 1\n"
                "A line 2\n"
                "## Part B\n"
                "B line 1\n"
            )
            input_path.write_text(sample, encoding="utf-8")

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = fpf.main(
                    [
                        "split",
                        "--work-dir",
                        str(work_dir),
                    ]
                )

            self.assertEqual(exit_code, 0)
            manifest_path = work_dir / "FPF-Parts-Manifest.yaml"
            self.assertTrue(manifest_path.exists())
            manifest_lines = self.read_manifest_parts(manifest_path)
            baseline_name = self.read_manifest_baseline(manifest_path)
            self.assertEqual(
                manifest_lines,
                ["FPF-Part-Preface.md", "FPF-Part-A.md", "FPF-Part-B.md"],
            )
            self.assertEqual(baseline_name, "FPF-Spec.md")

            for name in manifest_lines:
                self.assertTrue((work_dir / name).exists())

            reassembled = b"".join(
                (work_dir / name).read_bytes() for name in manifest_lines
            )
            self.assertEqual(reassembled, input_path.read_bytes())

    @unittest.skipUnless(
        Path("FPF/FPF-Spec.md").exists(),
        "Requires FPF/FPF-Spec.md. Run `./fpf-cli download` first.",
    )
    def test_split_real_spec_reassembles(self) -> None:
        input_path = Path("FPF/FPF-Spec.md")

        with TemporaryDirectory() as tmp_dir:
            work_dir = Path(tmp_dir)
            (work_dir / "FPF-Spec.md").write_bytes(input_path.read_bytes())

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = fpf.main(
                    [
                        "split",
                        "--work-dir",
                        str(work_dir),
                    ]
                )

            self.assertEqual(exit_code, 0)
            manifest_path = work_dir / "FPF-Parts-Manifest.yaml"
            self.assertTrue(manifest_path.exists())
            manifest_lines = self.read_manifest_parts(manifest_path)
            baseline_name = self.read_manifest_baseline(manifest_path)
            self.assertGreater(len(manifest_lines), 0)
            self.assertEqual(manifest_lines[0], "FPF-Part-Preface.md")
            for letter in "ABCDEFGHIJK":
                self.assertIn(f"FPF-Part-{letter}.md", manifest_lines)
            self.assertEqual(baseline_name, "FPF-Spec.md")

            reassembled = b"".join(
                (work_dir / name).read_bytes() for name in manifest_lines
            )
            self.assertEqual(reassembled, (work_dir / "FPF-Spec.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
