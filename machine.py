import sys
from typing import List


class DataPath:

    data_memory_size = None

    data = None

    estack_ptr = None

    fstack_ptr = None

    acc = None

    input_buffer = None

    output_buffer = None

    def __init__(self, data: bytearray, input_buffer: List[str]):
        self.data_memory_size = 32 * 1024
        self.data = data
        self.data_address = 0
        self.estack_ptr = 768  # 1024 - 256
        self.fstack_ptr = 1024
        self.acc = 0
        self.input_buffer = input_buffer
        self.output_buffer = []


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

    def decode_instruction(self):
        instr = self.instr_memory[self.icounter * 16:(self.icounter+1)*16][14:16].hex()
        self.tick()
        print(instr)

    def execute_instruction(self):
        instruction = self.decode_instruction()


def simulation(instr: bytes, data: bytearray, input_buf: List[str]):

    data_path = DataPath(data, input_buf)
    control_unit = ControlUnit(instr, data_path)

    try:
        while True:
            control_unit.execute_instruction()
    except StopIteration:
        pass


def main(instr_file, data_file, input_file):
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
