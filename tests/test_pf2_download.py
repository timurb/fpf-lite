import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import fpf


class FakeResponse:
    def __init__(self, status: int, data: bytes) -> None:
        self.status = status
        self._data = data

    def read(self) -> bytes:
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class TestPF2Download(unittest.TestCase):
    def test_download_spec_writes_file_and_creates_dir(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "FPF" / "FPF-Spec.md"
            data = b"spec contents"

            with patch(
                "fpf.urllib.request.urlopen",
                return_value=FakeResponse(200, data),
            ) as mock_urlopen:
                fpf.download_spec("https://example.test/spec.md", output_path)

            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.read_bytes(), data)
            mock_urlopen.assert_called_once()

    def test_download_spec_http_error_raises(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "FPF" / "FPF-Spec.md"

            with patch(
                "fpf.urllib.request.urlopen",
                return_value=FakeResponse(404, b""),
            ):
                with self.assertRaises(RuntimeError) as ctx:
                    fpf.download_spec("https://example.test/spec.md", output_path)

            self.assertIn("HTTP 404", str(ctx.exception))

    def test_main_download_command_reports_success(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "FPF" / "FPF-Spec.md"
            data = b"spec contents"

            with patch(
                "fpf.urllib.request.urlopen",
                return_value=FakeResponse(200, data),
            ):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    exit_code = fpf.main(
                        [
                            "download",
                            "--url",
                            "https://example.test/spec.md",
                            "--output",
                            str(output_path),
                        ]
                    )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            self.assertIn("Downloaded FPF spec to", buffer.getvalue())

    def test_main_download_command_reports_error(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "FPF" / "FPF-Spec.md"

            with patch(
                "fpf.urllib.request.urlopen",
                return_value=FakeResponse(404, b""),
            ):
                buffer_out = io.StringIO()
                buffer_err = io.StringIO()
                with redirect_stdout(buffer_out), redirect_stderr(buffer_err):
                    exit_code = fpf.main(
                        [
                            "download",
                            "--url",
                            "https://example.test/spec.md",
                            "--output",
                            str(output_path),
                        ]
                    )

            self.assertEqual(exit_code, 1)
            self.assertIn("HTTP 404", buffer_err.getvalue())
            self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
