import sys
from typing import List


class DataPath:

    data_memory_size = None

    data: bytearray

    data_address: int

    estack_ptr: int

    fstack_ptr: int

    acc: int

    zero_flag = 0

    input_buffer = None

    output_buffer = None

    def __init__(self, data: bytearray, input_buffer: List[str]):
        self.data_memory_size = 32 * 1024
        self.data = data
        self.data_address = 0
        self.estack_ptr = 768  # 1024 - 256
        self.fstack_ptr = 1024
        self.acc = 0
        self.zero_flag = 0
        self.input_buffer = input_buffer
        self.output_buffer = []

    def latch_set_zero(self):
        if self.acc == 0:
            self.zero_flag = 1
        else:
            self.zero_flag = 0

    def latch_addr(self, sel: str):
        if sel in {"3", "4"}:  # Fstack
            self.data_address = self.fstack_ptr
        elif sel in {"5", "6"}:  # EStack
            self.data_address = self.estack_ptr

    def sig_write(self):
        self.data[self.data_address] = self.acc

    def latch_acc(self, sel: str | None = None): # None == from memory
        if sel == "7":
            self.acc = self.zero_flag
        else:
            self.acc = self.data[self.data_address]


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
        assert (self.icounter+1)*16 <= 1024, "Memory border!"
        return self.instr_memory[self.icounter *
                                 16:(self.icounter+1)*16][14:16].hex()

    def execute_instruction(self):
        instr: str = self.acquire_next_instruction()

        if instr[0] == "1":
            self.execute_non_arg_instruction(instr)
        else:
            self.execute_arg_instruction(instr)

        self.tick()

    def execute_arg_instruction(self, instr: str):
        # Fetch address or offset
        0

    def execute_non_arg_instruction(self, instr: str):
        concrete: str = instr[1]
        if concrete == "1":  # Halt
            raise StopIteration
        elif concrete == "2":  # CMP
            self.data_path.latch_set_zero()
        elif concrete in {"3", "4", "5", "6", "E"}:  # Stacks
            self.execute_stack_instruction(instr)
        elif concrete == "7":  # Load Zero flag
            self.data_path.latch_acc(concrete)
        elif concrete == "8":  # Return
            0
        elif concrete == "9":  # Clear Acc
            self.data_path.clear_acc()
        elif concrete in {"A", "B", "F"}:  # Arith
            self.execute_arith_instruction(instr)
        elif concrete in {"C", "D"}:  # IO
            self.execute_io_instruction(instr)

    def execute_stack_instruction(self, instr: str):
        if instr == "3":
            self.data_path.latch_addr(instr)
            self.data_path.sig_write()
            self.data_path.fstack_ptr -= 1
        elif instr == "4":
            self.data_path.latch_addr(instr)
            self.data_path.latch_acc()
            self.data_path.fstack_ptr += 1
        elif instr == "5":
            self.data_path.latch_addr(instr)
            self.data_path.sig_write()
            self.data_path.estack_ptr -= 1
        elif instr == "6":
            self.data_path.latch_addr(instr)
            self.data_path.latch_acc()
            self.data_path.estack_ptr += 1

    def execute_arith_instruction(self, instr: str):
        0

    def execute_io_instruction(self, instr: str):
        0

    # def execute_instruction(self):
    #     instruction = self.decode_instruction()


def simulation(instr: bytes, data: bytearray, input_buf: List[str]):

    data_path = DataPath(data, input_buf)
    control_unit = ControlUnit(instr, data_path)

    try:
        while True:
            control_unit.execute_instruction()
    except StopIteration:
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
    # logging.getLogger().setLevel(logging.DEBUG)
    _, code_file, data_file, input_file = sys.argv
    main(code_file, data_file, input_file)
