from enum import Enum
import sys
from typing import List, Literal
from isa import Opcode
from parsing import convert_to_lists, to_tokens
from pprint import pprint


icounter = 0

jmp_stack = []

const_counter: int = 0
global_counter: int = 0

# Data =
# | Global vars
# | Anon Constants (enumed during translation)
# | Data.Spec (buff-reg for 2-op commands)
#
# Global entry -> (name, value)
# Const -> (number, value)
# Data.Spec -> (value)
#
# Mapping to memory:
# Global -> From beggining
# Const -> Magic offset + number
# Data.Spec -> End
# Stack ???


class Data(Enum):
    Global = 1,
    Const = 2,
    Spec = 3
    Acc = 4


word = 16
const_offset = 100 * word
data = {Data.Global: {}, Data.Const: {}, Data.Spec: 0}


class Addr(Enum):
    Direct = 1,
    Indirect = 2,
    Ptr = 3,


def add_inst(instruction: Opcode, mem: Literal[Data.Spec] | Literal[Data.Acc] | str | int | None, addr_type: Addr | None):
    global icounter
    instr[icounter] = [instruction, mem, addr_type]
    icounter += 1


# def add_str(where: Data, var_name: str | None, val: str):
#     global const_counter
#     to_add = val[1:-1]
#     if where == Data.Global:
#         data[where][var_name] = to_add
#     else:
#         data[where][const_counter] = to_add   # for-loop for string
#         add_inst(Opcode.LOAD, const_counter)  # for-loop for string
#         const_counter += 1


def construct(s_exp: List[str] | str):
    global icounter, jmp_stack, const_counter, global_counter
    match s_exp[0]:

        case "define":
            assert len(s_exp) == 3, "Invalid var definition!"

            data[Data.Global][s_exp[1]] = []

            # String def
            if s_exp[2].startswith("\""):
                for c in s_exp[2][1:-1]:
                    data[Data.Global][s_exp[1]].append([global_counter, c])
                    global_counter += 1
                data[Data.Global][s_exp[1]].append([global_counter, 0])
                global_counter += 1

            # Number def
            else:
                data[Data.Global][s_exp[1]] = [global_counter, int(s_exp[2])]
                global_counter += 1

        case "set":
            assert len(s_exp) == 3, "Invalid var modifying!"
            assert data[Data.Global].get(s_exp[1]) != None, "Non-existing var!"
            construct(s_exp[2])
            # Value's addr to set in ACC after constructing
            add_inst(Opcode.STORE, s_exp[1], Addr.Direct)

        case "if":
            construct(s_exp[1])
            jmp_stack.append(icounter)
            add_inst(Opcode.JIL, None, None)
            construct(s_exp[2])
            instr[jmp_stack.pop()][1] = icounter + 1
            jmp_stack.append(icounter)
            add_inst(Opcode.JMP, None, None)
            construct(s_exp[3])
            instr[jmp_stack.pop()][1] = icounter

        case "==":
            construct(s_exp[1])
            add_inst(Opcode.STORE, Data.Spec, Addr.Direct)
            construct(s_exp[2])
            add_inst(Opcode.LOAD, Data.Acc, Addr.Indirect)
            add_inst(Opcode.SUB, Data.Spec, Addr.Indirect)

        case "+":
            construct(s_exp[1])
            add_inst(Opcode.STORE, Data.Spec, Addr.Direct)
            construct(s_exp[2])
            add_inst(Opcode.LOAD, Data.Acc, Addr.Indirect)
            add_inst(Opcode.ADD, Data.Spec, Addr.Indirect)

        case _:  # Constants or vars to Load
            s_exp = str(s_exp)
            # Number const
            if s_exp.isnumeric():
                data[Data.Const][const_counter] = s_exp
                add_inst(Opcode.LOAD, const_counter, Addr.Ptr)
                const_counter += 1

            # String const
            elif s_exp.startswith("\""):
                add_inst(Opcode.LOAD, const_counter, Addr.Ptr)
                for c in s_exp[1:-1]:
                    data[Data.Const][const_counter] = c
                    const_counter += 1
                data[Data.Const][const_counter] = 0
                const_counter += 1

            # Var to Load
            else:
                assert data[Data.Global].get(
                    str(s_exp)) != None, "Non-existing var!"
                add_inst(Opcode.LOAD, str(s_exp), Addr.Ptr)


# Instructions -> (number, opcode, operand's addr | None)
instr = {}


def translate(source: str):
    model = convert_to_lists(to_tokens(source))
    for top_exp in model:
        construct(top_exp)
    add_inst(Opcode.HALT, None, None)


def main(source_path, target_instr_path, target_data_path):
    with open(source_path, encoding="utf-8") as file:
        source = file.read()
        source = "(" + source + ")"
        translate(source)
        pprint(instr)
        pprint(data)
        # make_file(target_instr_path, instructions)
        # make_file(target_instr_path, data)


if __name__ == "__main__":
    assert len(sys.argv) == 4
    _, source_path, target_instr_path, target_data_path = sys.argv
    main(source_path, target_instr_path, target_data_path)
