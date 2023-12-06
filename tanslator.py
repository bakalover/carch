from enum import Enum
import sys
from typing import List, Literal
from isa import Opcode
from parsing import convert_to_lists, to_tokens
from pprint import pprint


jmp_stack = []
icounter: int = 0
acounter: int = 0
ncounter: int = 0


class Data(Enum):
    Named = 1,
    Anon = 2,
    StackPtr = 3


word = 16
const_offset = 100 * word
data = {Data.Named: {}, Data.Anon: {}}
instr = {}


class Addr(Enum):
    Direct = 1,
    Indirect = 2,


def add_instr(instruction: Opcode, mem:  Literal[Data.StackPtr] | str | int | None, addr_type: Addr | None):
    global icounter
    instr[icounter] = [instruction, mem, addr_type]
    icounter += 1


def construct(s_exp: List[str] | str) -> bool:  # bool for string control
    global icounter, jmp_stack, acounter, ncounter

    match s_exp[0]:

        case "define":
            assert len(s_exp) == 3, "Invalid var definition!"

            # String def
            if s_exp[2].startswith("\""):
                data[Data.Named][s_exp[1]] = [ncounter, True, acounter]
                ncounter += 1
                for c in s_exp[2][1:-1]:
                    data[Data.Anon][s_exp[1]].append([acounter, c])
                    acounter += 1
                data[Data.Anon][s_exp[1]].append([acounter, 0])
                acounter += 1

            # Number def
            else:
                data[Data.Named][s_exp[1]] = [ncounter, False, int(s_exp[2])]
                ncounter += 1
            return False  # No matter (won't use as s-exp ret)

        case "set":
            assert len(s_exp) == 3, "Invalid var modifying!"
            assert data[Data.Named].get(s_exp[1]) != None, "Non-existing var!"
            is_str = construct(s_exp[2])
            add_instr(Opcode.POP, None, None)
            add_instr(Opcode.STORE, s_exp[1], Addr.Direct)
            # S-exp return already in acc
            return is_str

        case "if":
            construct(s_exp[1])
            add_instr(Opcode.POP, None, None)
            jmp_stack.append(icounter)
            add_instr(Opcode.JZ, None, None)
            is_str1 = construct(s_exp[2])
            instr[jmp_stack.pop()][1] = icounter + 1
            jmp_stack.append(icounter)
            add_instr(Opcode.JMP, None, None)
            is_str2 = construct(s_exp[3])
            instr[jmp_stack.pop()][1] = icounter
            assert is_str1 == is_str2, "Invalid if-branch s-exp ret result!"
            return is_str1

        case "==":
            is_str1 = construct(s_exp[1])
            is_str2 = construct(s_exp[2])
            add_instr(Opcode.POP, None, None)
            add_instr(Opcode.SUB, Data.StackPtr, Addr.Indirect)
            add_instr(Opcode.ZERO, None, None)  # Loads zero flag
            add_instr(Opcode.STORE, Data.StackPtr, Addr.Indirect)
            assert (not is_str1) and (not is_str2), "Can't compare strings!"
            return False

        case "+":
            is_str1 = construct(s_exp[1])
            is_str2 = construct(s_exp[2])
            add_instr(Opcode.POP, None, None)
            add_instr(Opcode.SUB, None, None)  # acc = acc - [stackptr]
            add_instr(Opcode.STORE, Data.StackPtr, Addr.Indirect)
            assert (not is_str1) and (not is_str2), "Can't add to string!"
            return False

        case _:  # Constants or vars to Load
            s_exp = str(s_exp)

            # Number const
            if s_exp.isnumeric():
                data[Data.Anon][acounter] = s_exp
                add_instr(Opcode.LOAD, acounter, Addr.Direct)
                acounter += 1
                add_instr(Opcode.PUSH, None, None)
                return False

            # String const
            elif s_exp.startswith("\""):
                add_instr(Opcode.LOAD, acounter, Addr.Direct)
                data[Data.Anon][acounter] = acounter + 1 #Giga chad pointer to next
                acounter += 1
                for c in s_exp[1:-1]:
                    data[Data.Anon][acounter] = c
                    acounter += 1
                data[Data.Anon][acounter] = 0
                acounter += 1
                return True

            # Var to Load
            else:
                assert data[Data.Named].get(
                    str(s_exp)) != None, "Non-existing var!"
                add_instr(Opcode.LOAD, str(s_exp), Addr.Direct)
                add_instr(Opcode.PUSH, None, None)
                return data[Data.Named][str(s_exp)][1] # returning flag "is it string"


def translate(source: str):
    model = convert_to_lists(to_tokens(source))
    for top_exp in model:
        construct(top_exp)
    add_instr(Opcode.HALT, None, None)


def main(source_path):
    with open(source_path, encoding="utf-8") as file:
        source = file.read()
        source = "(" + source + ")"
        translate(source)
        pprint(instr)
        pprint(data)
        # make_file(target_instr_path, instructions)
        # make_file(target_instr_path, data)


if __name__ == "__main__":
    assert len(sys.argv) == 2
    _, source_path = sys.argv
    main(source_path)
