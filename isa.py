from enum import Enum


class Opcode(str, Enum):

    ADD = "add"
    SUB = "sub"
    PRINT = "print"
    HALT = "halt"
    CMP = "cmp"
    JZ = "jz"
    JMP = "jmp"
    LOAD = "load"
    STORE = "store"
    PUSH = "push"
    POP = "pop"
    NOP = "nop"
    ZERO = "zero"
    CALL = "call"
    RET = "ret"

    def __str__(self):
        return str(self.value)
