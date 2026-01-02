import io
import re
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

import fpf


class TestPF3CompressLite(unittest.TestCase):
    @unittest.skipUnless(
        Path("FPF/FPF-Spec.md").exists(),
        "Requires FPF/FPF-Spec.md. Run `./fpf.py download` first.",
    )
    def test_compress_lite_real_spec(self) -> None:
        input_path = Path("FPF/FPF-Spec.md")

        with TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "FPF-Spec-Lite.md"

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = fpf.main(
                    [
                        "compress-lite",
                        "--input",
                        str(input_path),
                        "--output",
                        str(output_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            output = buffer.getvalue()
            self.assertIn("Stats for", output)
            self.assertIn("Removal statistics:", output)
            self.assertRegex(
                output,
                r"Lines:\s+\d+\s+->\s+\d+\s+\(Reduction:\s+\d+(\.\d+)?%\)",
            )

            result = output_path.read_text(encoding="utf-8")
            self.assertRegex(result, r"(?m)^#+\s+Part A", "Missing Part A header")
            headers = [line for line in result.splitlines() if line.lstrip().startswith("#")]
            header_text = "\n".join(headers)

            for keyword in [
                "SoTA-Echoing",
                "SOTA-Echoing",
                "SoTA Echoing",
                "SOTA Echoing",
                "State-of-the-Art alignment",
            ]:
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                self.assertIsNone(
                    pattern.search(header_text),
                    f"Found removed header keyword: {keyword}",
                )


if __name__ == "__main__":
    unittest.main()
