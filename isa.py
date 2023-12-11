from enum import Enum


class Opcode(str, Enum):

    INC = "inc"
    ADD = "add"
    SUB = "sub"
    READ = "read"
    PRINT = "print"
    HALT = "halt"
    CMP = "cmp"
    JZ = "jz"
    JMP = "jmp"
    LOAD = "load"
    STORE = "store"
    FPUSH = "fpush"
    FPOP = "fpop"
    EPUSH = "epush"
    EPOP = "epop"
    NOP = "nop"
    ZERO = "zero"
    CALL = "call"
    RET = "ret"
    CLEAR = "clear"
    INCESTACK = "incestack"

    def __str__(self):
        return str(self.value)
