from enum import Enum


class Opcode(str, Enum):

    ADD = "add"
    SUB = "sub" #Working with stack
    EQ = "eq"
    PRINT = "print"
    HALT = "halt"
    JZ = "jz"
    JIL = "jil"
    JMP = "jmp"
    LOAD = "load"
    STORE = "store"
    PUSH = "push"
    POP = "pop"

    def __str__(self):
        return str(self.value)


def symbol2opcode(symbol):
    return {
        "-": Opcode.SUB,
        "+": Opcode.ADD,
        "==": Opcode.EQ,
        "print": Opcode.PRINT,
    }.get(symbol)
