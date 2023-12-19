from io import BufferedWriter

from data import DATAWORD, INSTRWORD, Data, anon_offset
from isa import Opcode


def binary_transform(instructions, data):
    with open("instructions", "wb") as file:
        file.write(b"\x00" * INSTRWORD * 1024)
        file.seek(0)
        for _, instruction in instructions.items():
            to_dump = instruction[0].value
            mem = instruction[1]
            shift = instruction[2]
            match to_dump[2]:
                case "1":
                    file.write(int(to_dump, 16).to_bytes(INSTRWORD, "big"))
                case "A":
                    dump_load(mem, to_dump, shift, file, data)
                case "B":
                    dump_store(mem, to_dump, shift, file, data)
                case _:
                    file.write((int(to_dump, 16) | mem).to_bytes(INSTRWORD, "big"))

    with open("data", "wb") as file:
        file.write(b"\x00" * DATAWORD * 1024)
        file.seek(0)
        for _, value in data[Data.Named].items():
            file.write(value[2].to_bytes(DATAWORD, "big"))
        file.seek(DATAWORD * anon_offset)
        for _, value in data[Data.Anon].items():
            if isinstance(value, str):
                file.write(ord(value).to_bytes(DATAWORD, "big"))
            else:
                file.write(value.to_bytes(DATAWORD, "big"))


def dump_load(mem, to_dump: str, shift: int, file: BufferedWriter, data):
    if mem == Data.EStack:
        file.write((int(to_dump, 16) | shift | 0x0400).to_bytes(INSTRWORD, "big"))
    elif mem == Data.FStack:
        file.write((int(to_dump, 16) | shift | 0x0800).to_bytes(INSTRWORD, "big"))
    elif mem == Data.Ar:
        file.write((int(to_dump, 16) | shift | 0x0C00).to_bytes(INSTRWORD, "big"))
    elif isinstance(mem, str):
        addr = data[Data.Named].get(mem)[0]
        file.write((int(to_dump, 16) | addr).to_bytes(INSTRWORD, "big"))
    else:
        file.write((int(to_dump, 16) | mem).to_bytes(INSTRWORD, "big"))


def dump_store(mem, to_dump: str, shift: int, file: BufferedWriter, data):
    if mem == Data.EStack:
        file.write((int(to_dump, 16) | shift | 0x0400).to_bytes(INSTRWORD, "big"))
    elif mem == Data.FStack:
        file.write((int(to_dump, 16) | shift | 0x0800).to_bytes(INSTRWORD, "big"))
    elif mem == Data.Ar:
        file.write((int(to_dump, 16) | shift | 0x0C00).to_bytes(INSTRWORD, "big"))
    else:
        addr = data[Data.Named].get(mem)[0]
        file.write((int(to_dump, 16) | addr).to_bytes(INSTRWORD, "big"))


def bin2op_no_arg(bin_code: str):
    return {
        "10": Opcode.NOP,
        "11": Opcode.HALT,
        "12": Opcode.CMP,
        "13": Opcode.FPUSH,
        "14": Opcode.FPOP,
        "15": Opcode.EPUSH,
        "16": Opcode.EPOP,
        "17": Opcode.ZERO,
        "18": Opcode.RET,
        "19": Opcode.CLEAR,
        "1a": Opcode.ADD,
        "1b": Opcode.SUB,
        "1c": Opcode.READ,
        "1d": Opcode.PRINT,
        "1e": Opcode.INCESTACK,
        "1f": Opcode.MOD,
    }.get(bin_code)


def bin2op_with_arg(bin_code: str):
    return {
        "a": Opcode.LOAD,
        "b": Opcode.STORE,
        "c": Opcode.CALL,
        "e": Opcode.JZ,
        "f": Opcode.JMP,
    }.get(bin_code)
