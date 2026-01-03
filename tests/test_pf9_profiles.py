import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

import fpf


class TestPF9Profiles(unittest.TestCase):
    def write_parts(self, work_dir: Path, content_by_name: dict[str, str]) -> None:
        work_dir.mkdir(parents=True, exist_ok=True)
        for name, content in content_by_name.items():
            (work_dir / name).write_text(content, encoding="utf-8")

    def test_profile_name_resolves_in_profiles_dir(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            profiles_dir = base_dir / "profiles"
            work_dir = base_dir / "work"

            self.write_parts(
                work_dir,
                {
                    "FPF-Part-Preface.md": "Preface line 1\n",
                    "FPF-Part-A.md": "# Part A\nA line 1\n",
                },
            )
            (work_dir / "baseline.md").write_text(
                "Preface line 1\n# Part A\nA line 1\n",
                encoding="utf-8",
            )

            profiles_dir.mkdir(parents=True, exist_ok=True)
            (profiles_dir / "lite.yaml").write_text(
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
                        "--profile",
                        "lite",
                        "--profiles-dir",
                        str(profiles_dir),
                        "--work-dir",
                        str(work_dir),
                    ]
                )

            self.assertEqual(exit_code, 0)
            output_path = work_dir / "assembled.md"
            self.assertTrue(output_path.exists())
            self.assertIn("Stats for", buffer_out.getvalue())
            self.assertNotIn("warning", (buffer_out.getvalue() + buffer_err.getvalue()).lower())

    def test_profile_filename_resolves_in_profiles_dir(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            profiles_dir = base_dir / "profiles"
            work_dir = base_dir / "work"

            self.write_parts(
                work_dir,
                {
                    "FPF-Part-Preface.md": "Preface line 1\n",
                    "FPF-Part-A.md": "# Part A\nA line 1\n",
                },
            )
            (work_dir / "baseline.md").write_text(
                "Preface line 1\n# Part A\nA line 1\n",
                encoding="utf-8",
            )

            profiles_dir.mkdir(parents=True, exist_ok=True)
            (profiles_dir / "full.yaml").write_text(
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
                        "--profile",
                        "full.yaml",
                        "--profiles-dir",
                        str(profiles_dir),
                        "--work-dir",
                        str(work_dir),
                    ]
                )

            self.assertEqual(exit_code, 0)
            output_path = work_dir / "assembled.md"
            self.assertTrue(output_path.exists())

    def test_profile_path_uses_path_before_profiles_dir(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            profiles_dir = base_dir / "profiles"
            work_dir = base_dir / "work"
            custom_dir = base_dir / "custom"

            self.write_parts(
                work_dir,
                {
                    "FPF-Part-Preface.md": "Preface line 1\n",
                    "FPF-Part-A.md": "# Part A\nA line 1\n",
                },
            )
            (work_dir / "baseline.md").write_text(
                "Preface line 1\n# Part A\nA line 1\n",
                encoding="utf-8",
            )

            profiles_dir.mkdir(parents=True, exist_ok=True)
            (profiles_dir / "custom.yaml").write_text(
                "\n".join(
                    [
                        "output_file: wrong.md",
                        "parts:",
                        "  - FPF-Part-Preface.md",
                        "baseline_file: baseline.md",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            custom_dir.mkdir(parents=True, exist_ok=True)
            profile_path = custom_dir / "custom.yaml"
            profile_path.write_text(
                "\n".join(
                    [
                        "output_file: right.md",
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
                        "--profile",
                        str(profile_path),
                        "--profiles-dir",
                        str(profiles_dir),
                        "--work-dir",
                        str(work_dir),
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue((work_dir / "right.md").exists())
            self.assertFalse((work_dir / "wrong.md").exists())


if __name__ == "__main__":
    unittest.main()
