"""Консольный интерфейс лабораторной работы."""

import argparse
from pathlib import Path

from float_numbers import find_floats, is_float


def main(args: list[str] | None = None) -> None:
    """Проверить ввод с клавиатуры или найти числа в файле."""
    parser = argparse.ArgumentParser(
        description="Проверка и поиск чисел с плавающей запятой."
    )
    parser.add_argument(
        "--file", type=Path, metavar="ПУТЬ", help="текстовый файл UTF-8"
    )
    options = parser.parse_args(args)

    if options.file is None:
        value = input("Введите число: ")
        if is_float(value):
            print("Корректная запись.")
        else:
            print("Некорректная запись.")
        return

    try:
        # utf-8-sig читает UTF-8 с BOM и без него.
        text = options.file.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        parser.exit(2, f"Не удалось прочитать файл: {error}\n")

    matches = find_floats(text)
    if matches:
        print(f"Найдено: {len(matches)}")
        for value in matches:
            print(value)
    else:
        print("Числа с плавающей запятой не найдены.")


if __name__ == "__main__":
    main()
