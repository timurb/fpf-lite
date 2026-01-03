import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

import fpf


class TestPF6Assemble(unittest.TestCase):
    def write_parts(self, work_dir: Path, content_by_name: dict[str, str]) -> None:
        work_dir.mkdir(parents=True, exist_ok=True)
        for name, content in content_by_name.items():
            (work_dir / name).write_text(content, encoding="utf-8")

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

    def test_assemble_builds_output_and_stats(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            work_dir = Path(tmp_dir)
            self.write_parts(
                work_dir,
                {
                    "FPF-Part-Preface.md": "Preface line 1\n",
                    "FPF-Part-A.md": "# Part A\nA line 1\n",
                    "FPF-Part-B.md": "# Part B\nB line 1\n",
                },
            )

            baseline_file = work_dir / "baseline.md"
            baseline_file.write_text(
                "Preface line 1\n# Part A\nA line 1\n# Part B\nB line 1\n",
                encoding="utf-8",
            )

            manifest_path = work_dir / "assemble.yaml"
            manifest_path.write_text(
                "\n".join(
                    [
                        "output_file: assembled.md",
                        "parts:",
                        "  - FPF-Part-Preface.md",
                        "  - FPF-Part-A.md",
                        "baseline_file: baseline.md",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            buffer_out = io.StringIO()
            buffer_err = io.StringIO()
            with redirect_stdout(buffer_out), redirect_stderr(buffer_err):
                exit_code = fpf.main(
                    [
                        "assemble",
                        "--manifest",
                        "assemble.yaml",
                        "--work-dir",
                        str(work_dir),
                    ]
                )

            self.assertEqual(exit_code, 0)
            output_path = work_dir / "assembled.md"
            self.assertTrue(output_path.exists())
            expected = (
                (work_dir / "FPF-Part-Preface.md").read_text(encoding="utf-8")
                + (work_dir / "FPF-Part-A.md").read_text(encoding="utf-8")
            )
            self.assertEqual(output_path.read_text(encoding="utf-8"), expected)

            output = buffer_out.getvalue() + buffer_err.getvalue()
            self.assertIn("Stats for", output)
            self.assertIn("Removal statistics:", output)
            self.assertRegex(
                output,
                r"Lines:\s+\d+\s+->\s+\d+\s+\(Reduction:\s+\d+(\.\d+)?%\)",
            )

    def test_assemble_fails_when_part_missing(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            work_dir = Path(tmp_dir)
            self.write_parts(
                work_dir,
                {
                    "FPF-Part-Preface.md": "Preface line 1\n",
                },
            )

            manifest_path = work_dir / "assemble.yaml"
            manifest_path.write_text(
                "\n".join(
                    [
                        "output_file: assembled.md",
                        "parts:",
                        "  - FPF-Part-Preface.md",
                        "  - FPF-Part-A.md",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            buffer_out = io.StringIO()
            buffer_err = io.StringIO()
            with redirect_stdout(buffer_out), redirect_stderr(buffer_err):
                exit_code = fpf.main(
                    [
                        "assemble",
                        "--manifest",
                        "assemble.yaml",
                        "--work-dir",
                        str(work_dir),
                    ]
                )

            self.assertEqual(exit_code, 1)
            self.assertFalse((work_dir / "assembled.md").exists())

    def test_assemble_warns_when_baseline_missing(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            work_dir = Path(tmp_dir)
            self.write_parts(
                work_dir,
                {
                    "FPF-Part-Preface.md": "Preface line 1\n",
                    "FPF-Part-A.md": "# Part A\nA line 1\n",
                },
            )

            manifest_path = work_dir / "assemble.yaml"
            manifest_path.write_text(
                "\n".join(
                    [
                        "output_file: assembled.md",
                        "parts:",
                        "  - FPF-Part-Preface.md",
                        "  - FPF-Part-A.md",
                        "baseline_file: missing-baseline.md",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            buffer_out = io.StringIO()
            buffer_err = io.StringIO()
            with redirect_stdout(buffer_out), redirect_stderr(buffer_err):
                exit_code = fpf.main(
                    [
                        "assemble",
                        "--manifest",
                        "assemble.yaml",
                        "--work-dir",
                        str(work_dir),
                    ]
                )

            self.assertEqual(exit_code, 0)
            output_path = work_dir / "assembled.md"
            self.assertTrue(output_path.exists())
            expected = (
                (work_dir / "FPF-Part-Preface.md").read_text(encoding="utf-8")
                + (work_dir / "FPF-Part-A.md").read_text(encoding="utf-8")
            )
            self.assertEqual(output_path.read_text(encoding="utf-8"), expected)
            output = (buffer_out.getvalue() + buffer_err.getvalue()).lower()
            self.assertIn("warning", output)
            self.assertNotIn("stats for", output)

    @unittest.skipUnless(
        Path("FPF/FPF-Spec.md").exists(),
        "Requires FPF/FPF-Spec.md. Run `./fpf.py download` first.",
    )
    def test_assemble_all_parts_matches_spec(self) -> None:
        input_path = Path("FPF/FPF-Spec.md")

        with TemporaryDirectory() as tmp_dir:
            work_dir = Path(tmp_dir)
            (work_dir / "FPF-Spec.md").write_bytes(input_path.read_bytes())

            buffer_out = io.StringIO()
            buffer_err = io.StringIO()
            with redirect_stdout(buffer_out), redirect_stderr(buffer_err):
                split_exit = fpf.main(
                    [
                        "split",
                        "--work-dir",
                        str(work_dir),
                    ]
                )

            self.assertEqual(split_exit, 0)
            manifest_path = work_dir / "FPF-Parts-Manifest.yaml"
            manifest_lines = self.read_manifest_parts(manifest_path)
            self.assertGreater(len(manifest_lines), 0)

            assemble_manifest = work_dir / "assemble.yaml"
            assemble_manifest.write_text(
                "\n".join(
                    ["output_file: assembled.md", "parts:"]
                    + [f"  - {name}" for name in manifest_lines]
                    + ["baseline_file: FPF-Spec.md"]
                )
                + "\n",
                encoding="utf-8",
            )

            buffer_out = io.StringIO()
            buffer_err = io.StringIO()
            with redirect_stdout(buffer_out), redirect_stderr(buffer_err):
                assemble_exit = fpf.main(
                    [
                        "assemble",
                        "--manifest",
                        "assemble.yaml",
                        "--work-dir",
                        str(work_dir),
                    ]
                )

            self.assertEqual(assemble_exit, 0)
            output_path = work_dir / "assembled.md"
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.read_bytes(), (work_dir / "FPF-Spec.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
