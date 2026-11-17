"""Unit-тесты шаблона и консольного интерфейса."""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from float_numbers import find_floats, is_float
from main import main


class FloatPatternTests(unittest.TestCase):
    def test_accepts_supported_forms(self):
        for value in (
            "3.14", "-0.5", "+2.0", ".5", "-.5", "5.", "0.0",
            "1e3", "-1E-3", "1.2E+4", ".5e2", "5.e1", "1e9999",
        ):
            with self.subTest(value=value):
                self.assertTrue(is_float(value))

    def test_rejects_other_forms(self):
        for value in (
            "", "42", "-42", ".", "+.", "1e", "1e+", "e2", "NaN",
            "inf", "2,5", "1.2.3", "--1.5", "x1.5", "1.5x", " 1.5",
            "1.5 ", "1.5\n", "1_000.5", "１.５",
        ):
            with self.subTest(value=value):
                self.assertFalse(is_float(value))

    def test_search_preserves_order_and_repeated_values(self):
        text = "-12.5\nпоправка=(+.5), масштаб: 1e-3; 5.\n-12.5"
        self.assertEqual(
            find_floats(text), ["-12.5", "+.5", "1e-3", "5.", "-12.5"]
        )

    def test_search_accepts_delimiters(self):
        self.assertEqual(
            find_floats("[.5],(3.2); 1E+3!"), [".5", "3.2", "1E+3"]
        )

    def test_search_skips_parts_of_invalid_tokens(self):
        for value in (
            "abc1.5", "1.5кг", "_1.5", "1.2.3", "--.5", "+-1.5",
            "12.5e+", "1.2,3", "1,2.3", "１.5", "3.14.", "1_000.5",
        ):
            with self.subTest(value=value):
                self.assertEqual(find_floats(f"({value})"), [])

    def test_search_returns_empty_list_without_matches(self):
        for text in ("", "Здесь только 42 и 7,25."):
            with self.subTest(text=text):
                self.assertEqual(find_floats(text), [])


class ConsoleTests(unittest.TestCase):
    def test_interactive_accepts_number(self):
        with patch("builtins.input", return_value="1e-3"):
            with redirect_stdout(io.StringIO()) as output:
                main([])
        self.assertEqual(output.getvalue(), "Корректная запись.\n")

    def test_interactive_rejects_number(self):
        with patch("builtins.input", return_value="42"):
            with redirect_stdout(io.StringIO()) as output:
                main([])
        self.assertEqual(output.getvalue(), "Некорректная запись.\n")

    def test_file_mode_reads_utf8_with_bom(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "данные.txt"
            file.write_text("Ответ: -3.5 и .25", encoding="utf-8-sig")
            with redirect_stdout(io.StringIO()) as output:
                main(["--file", str(file)])
        self.assertEqual(output.getvalue(), "Найдено: 2\n-3.5\n.25\n")

    def test_file_mode_reports_no_matches(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "empty.txt"
            file.write_text("", encoding="utf-8")
            with redirect_stdout(io.StringIO()) as output:
                main(["--file", str(file)])
        self.assertEqual(
            output.getvalue(), "Числа с плавающей запятой не найдены.\n"
        )

    def test_file_mode_reports_missing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "missing.txt"
            with redirect_stderr(io.StringIO()) as output:
                with self.assertRaises(SystemExit) as error:
                    main(["--file", str(file)])
        self.assertEqual(error.exception.code, 2)
        self.assertIn("Не удалось прочитать файл", output.getvalue())

    def test_file_mode_reports_invalid_utf8(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "invalid.txt"
            file.write_bytes(b"\xff")
            with redirect_stderr(io.StringIO()) as output:
                with self.assertRaises(SystemExit) as error:
                    main(["--file", str(file)])
        self.assertEqual(error.exception.code, 2)
        self.assertIn("Не удалось прочитать файл", output.getvalue())


if __name__ == "__main__":
    unittest.main()
