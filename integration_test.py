import contextlib
import io
import logging
import os
import tempfile

import machine
import pytest
import translator


@pytest.mark.golden_test("golden/*.yml")
def test_user(golden, caplog, tmp_path):
    # Установим уровень отладочного вывода на DEBUG
    caplog.set_level(logging.DEBUG)

    # Создаём временную папку для тестирования приложения.
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Готовим имена файлов для входных и выходных данных.
        source = os.path.join(tmpdirname, "source.txt")
        input_stream = os.path.join(tmpdirname, "input.txt")
        target_instructions = os.path.join(tmpdirname, "instructions")
        target_data = os.path.join(tmpdirname, "data")
        target_mnemonics = os.path.join(tmpdirname, "mnemonics.txt")

        # Записываем входные данные в файлы. Данные берутся из теста.
        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["in_source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["in_stdin"])

        # Запускаем транслятор и собираем весь стандартный вывод в переменную
        # stdout
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main(source, target_instructions, target_mnemonics, target_data)
            machine.main(target_instructions, target_data, input_stream)

        # Выходные данные также считываем в переменные.
        with open(target_mnemonics, encoding="utf-8") as file:
            mnemonics = file.read()

        # Проверяем, что ожидания соответствуют реальности.
        assert mnemonics == golden.out["out_mnemonics"]
        assert stdout.getvalue() == golden.out["out_stdout"]
