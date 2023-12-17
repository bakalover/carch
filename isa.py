from enum import Enum


class Opcode(str, Enum):

    NOP = "0x1000"
    HALT = "0x1100"
    CMP = "0x1200"
    FPUSH = "0x1300"
    FPOP = "0x1400"
    EPUSH = "0x1500"
    EPOP = "0x1600"
    ZERO = "0x1700"
    RET = "0x1800"
    CLEAR = "0x1900"
    ADD = "0x1A00"
    SUB = "0x1B00"
    READ = "0x1C00"
    PRINT = "0x1D00"
    INCESTACK = "0x1E00"
    MOD = "0x1F00"
    LOAD = "0xA000"
    STORE = "0xB000"
    CALL = "0xC000"
    JZ = "0xE000"
    JMP = "0xF000"

    def __str__(self):
        return str(self.value)
    
   

