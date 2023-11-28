from enum import Enum


class Opcode(str, Enum):

    ADD = "add"
    SUB = "sub"
    EQ = "eq"
    PRINT = "print"
    HALT = "halt"
    JZ = "jz"
    JMP = "jmp"
    LOAD = "load"
    STORE = "store"
    CMP = "cmp"

    def __str__(self):
        return str(self.value)


def symbol2opcode(symbol):
    return {
        "-": Opcode.SUB,
        "+": Opcode.ADD,
        "==": Opcode.EQ,
        "print": Opcode.PRINT,
    }.get(symbol)
