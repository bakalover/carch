from enum import Enum


class Opcode(str, Enum):

    NOP = "0x0000"
    HALT = "0x0100"
    CMP = "0x0200"
    FPUSH = "0x0300"
    FPOP = "0x0400"
    EPUSH = "0x0500"
    EPOP = "0x0600"
    ZERO = "0x0700"
    RET = "0x0800"
    CLEAR = "0x0900"
    ADD = "0x0A00"
    SUB = "0x0B00"
    READ = "0x0C00"
    PRINT = "0x0D00"
    INCESTACK = "0x0E00"
    LOAD = "0xA000"
    STORE = "0xB000"
    CALL = "0xC000"
    JZ = "0xE000"
    JMP = "0xF000"

    def __str__(self):
        return str(self.value)