from __future__ import annotations

import sys

from binary import bin2op_no_arg, bin2op_with_arg
from data import DATAWORD, INSTRWORD
from isa import Opcode

ADDRMASK: int = 0x0FFF
OFFSETMASK: int = 0x03FF
TYPEMASK: int = 0x0F00
FSTACKMASK: int = 0x0800
ESTACKMASK: int = 0x0400
ARMASK: int = 0x0C00


class DataPath:
    data_memory_size: int
    data: bytearray
    data_address: int
    estack_ptr: int
    fstack_ptr: int
    acc: int
    zero_flag: int
    input_buffer: list[str]
    output_buffer: list[str]

    def __init__(self, data: bytearray, input_buffer: list[str]):
        self.data_memory_size = DATAWORD * 1024
        self.data = data
        self.data_address = 0
        self.estack_ptr = 768  # 1024 - 256
        self.fstack_ptr = 1024
        self.acc = 0
        self.zero_flag = 0
        self.input_buffer = input_buffer
        self.output_buffer = []

    def mem_load(self) -> int:
        assert self.data_address + 1 <= 1024, "Data memory border violation!"
        return int.from_bytes(self.data[self.data_address * DATAWORD : (self.data_address + 1) * DATAWORD], "big")

    def mem_store(self, val: int):
        self.data[self.data_address * DATAWORD : (self.data_address + 1) * DATAWORD] = val.to_bytes(DATAWORD, "big")

    def latch_set_zero(self):
        if self.acc == 0:
            self.zero_flag = 1
        else:
            self.zero_flag = 0

    def latch_addr(self, sel: Opcode, addr: int = 0):
        if sel in {Opcode.FPUSH, Opcode.FPOP, Opcode.EPUSH, Opcode.EPOP}:
            self.stack_addr_latch_logic(sel)
        elif sel in {Opcode.ADD, Opcode.SUB, Opcode.MOD, Opcode.INCESTACK}:
            self.data_address = self.estack_ptr
        elif sel in {Opcode.LOAD, Opcode.STORE}:
            self.load_store_addr_latch_logic(addr)

    def load_store_addr_latch_logic(self, addr: int):
        if addr & TYPEMASK == FSTACKMASK:
            self.data_address = self.fstack_ptr + (addr & OFFSETMASK)
        elif addr & TYPEMASK == ESTACKMASK:
            self.data_address = self.estack_ptr + (addr & OFFSETMASK)
        elif addr & TYPEMASK == ARMASK:
            0  # Nop
        else:
            self.data_address = addr & OFFSETMASK

    def stack_addr_latch_logic(self, sel: Opcode):
        if sel == Opcode.FPUSH:
            self.fstack_ptr -= 1
            self.data_address = self.fstack_ptr
        elif sel == Opcode.FPOP:
            self.data_address = self.fstack_ptr
            self.fstack_ptr += 1
        elif sel == Opcode.EPUSH:
            self.estack_ptr -= 1
            self.data_address = self.estack_ptr
        elif sel == Opcode.EPOP:
            self.data_address = self.estack_ptr
            self.estack_ptr += 1

    def sig_write(self):
        self.mem_store(self.acc)

    def latch_acc(self, sel: Opcode | None = None):  # None == from memory
        if sel == Opcode.ZERO:
            self.acc = self.zero_flag
        else:
            self.acc = self.mem_load()

    def acc_inc(self):
        self.acc += 1

    def clear_acc(self):
        self.acc = 0

    def setup_zero_flag(self):
        if self.acc == 0:
            self.zero_flag = 1
        else:
            self.zero_flag = 0

    def sig_sum(self):
        self.acc += self.mem_load()
        self.setup_zero_flag()

    def sig_sub(self):
        self.acc -= self.mem_load()
        self.setup_zero_flag()

    def sig_mod(self):
        self.acc %= self.mem_load()
        self.setup_zero_flag()

    def sig_out(self):
        if chr(self.acc) == "/":
            self.output_buffer.append(" ")
        else:
            self.output_buffer.append(chr(self.acc))

    def sig_read(self):
        assert len(self.input_buffer) != 0, "EOF!"
        symb = self.input_buffer.pop(0)
        symb_code: int
        if symb == "\n":  # Crutch
            symb_code = ord(str(0)) - 48
        else:
            symb_code = ord(symb)
        assert -128 <= symb_code <= 127, "Not ASCII symbol!"
        self.acc = symb_code

    def sig_acc_to_addr(self):
        self.data_address = self.acc


class ControlUnit:
    instr_memory: bytes
    icounter: int
    data_path: DataPath

    def __init__(self, instr_memory: bytes, data_path: DataPath):
        self.instr_memory = instr_memory
        self.icounter = 0
        self.data_path = data_path

    def tick(self):
        self.icounter += 1

    def acquire_next_instruction(self) -> str:
        assert self.icounter + 1 <= 1024, "Instruction memory border violation!"
        return self.instr_memory[self.icounter * INSTRWORD : (self.icounter + 1) * INSTRWORD].hex()

    def execute_instruction(self):
        instr: str = self.acquire_next_instruction()

        if instr[0] == "1":
            self.execute_non_arg_instruction(instr)
            self.tick()  # No internal changing of icounter
        else:
            self.execute_arg_instruction(instr)

    def execute_arg_instruction(self, instr: str):
        specific = bin2op_with_arg(instr[:1])
        match specific:
            case Opcode.LOAD:
                self.data_path.latch_addr(Opcode.LOAD, int(instr, 16) & ADDRMASK)
                self.data_path.latch_acc()
                self.data_path.sig_acc_to_addr()
                self.tick()
            case Opcode.STORE:
                self.data_path.latch_addr(Opcode.STORE, int(instr, 16) & ADDRMASK)
                self.data_path.sig_write()
                self.tick()
            case Opcode.CALL:
                self.data_path.acc = self.icounter  # direct wire on scheme
                # Pushing icounter on FStack
                self.execute_stack_instruction(Opcode.FPUSH)
                self.icounter = int(instr[1:], 16)  # Actual Jump
            case Opcode.JZ:
                if self.data_path.zero_flag == 1:
                    self.icounter = int(instr[1:], 16)
                else:
                    self.tick()
            case Opcode.JMP:
                self.icounter = int(instr[1:], 16)

    def execute_non_arg_instruction(self, instr: str):
        specific = bin2op_no_arg(instr[:2])
        if specific in {Opcode.CMP, Opcode.ZERO}:
            self.execute_flag_instruction(specific)
        elif specific in {Opcode.FPUSH, Opcode.FPOP, Opcode.EPUSH, Opcode.EPOP, Opcode.INCESTACK, Opcode.RET}:
            self.execute_stack_instruction(specific)
        elif specific == Opcode.CLEAR:
            self.data_path.clear_acc()
        elif specific in {Opcode.ADD, Opcode.SUB, Opcode.MOD}:  # Arith
            self.execute_arith_instruction(specific)
        elif specific in {Opcode.READ, Opcode.PRINT}:  # IO
            self.execute_io_instruction(specific)
        if specific == Opcode.HALT:
            raise StopIteration  # Actually Opcode.HALT

    def execute_flag_instruction(self, specific: Opcode):
        if specific == Opcode.CMP:
            self.data_path.latch_set_zero()
        elif specific == Opcode.ZERO:
            self.data_path.latch_acc(specific)

    def execute_stack_instruction(self, instr: Opcode):
        self.data_path.latch_addr(instr)
        if instr in {Opcode.FPUSH, Opcode.EPUSH}:
            self.data_path.sig_write()
        elif instr in {Opcode.EPOP, Opcode.FPOP}:
            self.data_path.latch_acc()
        elif instr == Opcode.INCESTACK:
            self.data_path.latch_acc()
            self.data_path.acc_inc()
            self.data_path.sig_write()
        elif instr == Opcode.RET:
            self.execute_stack_instruction(Opcode.FPOP)  # Ret addr -> Acc
            self.icounter = self.data_path.acc  # wire to controlunit from acc

    def execute_arith_instruction(self, instr: Opcode):
        self.data_path.latch_addr(instr)  # Getting estack_ptr as addr
        if instr == Opcode.ADD:
            # Sig dirrectly to acc (apply opp with 2-args: acc and [estack_ptr])
            self.data_path.sig_sum()
        elif instr == Opcode.SUB:
            self.data_path.sig_sub()
        elif instr == Opcode.MOD:
            self.data_path.sig_mod()

    def execute_io_instruction(self, instr: Opcode):
        if instr == Opcode.PRINT:
            self.data_path.sig_out()
        else:
            self.data_path.sig_read()
            self.data_path.sig_write()


def simulation(instr: bytes, data: bytearray, input_buf: list[str]):
    data_path = DataPath(data, input_buf)
    control_unit = ControlUnit(instr, data_path)

    try:
        while True:
            control_unit.execute_instruction()
    except StopIteration:
        print(data_path.output_buffer)
        pass


def main(instr_file: str, data_file: str, input_file: str):
    with open(instr_file, "br") as instr_f:
        code: bytes = instr_f.read()  # Instructions not mutable
    with open(data_file, "br") as data_f:
        data: bytearray = bytearray(data_f.read())  # Memory is mutable
    with open(input_file, encoding="utf-8") as file:
        input_text = file.read()
        input_buf = []
        for char in input_text:
            input_buf.append(char)

    simulation(code, data, input_buf)


if __name__ == "__main__":
    _, code_file, data_file, input_file = sys.argv
    main(code_file, data_file, input_file)
