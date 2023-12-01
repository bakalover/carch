from ast import Global
from enum import Enum
import sys
from typing import List
from isa import Opcode


def get_top_exps(source: str) -> List[str]:
    top_exps = []
    l, r = 0, 0
    counter = 0
    for c in source:
        if c == '(':
            counter += 1
        if c == ")":
            counter -= 1
            if counter == 0:
                # Slice that contains  s-exp with brackets
                top_exps.append(source[l: r+1])
                l = r + 1
        r += 1
        assert counter >= 0, "Brackets!"
    assert counter == 0, "Brackets!"
    return top_exps


def to_tokens(source: str) -> List[str]:
    return source.strip().replace('\n', '').replace('(', ' ( ').replace(')', ' ) ').split()


def convert_to_lists(tokens: list):
    token = tokens.pop(0)
    if token == '(':
        temp = []
        while tokens[0] != ')':
            temp.append(convert_to_lists(tokens))
        tokens.pop(0)
        return temp
    else:
        return token


icounter = 0


def add_inst(instruction, additional):
    global icounter
    instr[icounter] = [instruction, additional]
    icounter += 1


jmp_stack = []

const_counter: int = 0

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


word = 16
const_offset = 100 * word
data = {Data.Global: {}, Data.Const: {}, Data.Spec: 0}


def add_str(where: Data, var_name: str | None, val: str):
    global const_counter
    to_add = val[1:-1]
    if where == Data.Global:
        data[where][var_name] = to_add
    else:
        data[where][const_counter] = to_add   # for-loop for string
        add_inst(Opcode.LOAD, const_counter)  # for-loop for string
        const_counter += 1


def construct(s_exp: List[str] | str):
    global icounter, jmp_stack, const_counter
    match s_exp[0]:

        case "define":
            assert len(s_exp) == 3, "Invalid var definition!"

            # String def
            if s_exp[2].startswith("\""):
                add_str(Data.Global, s_exp[1], s_exp[2])

            # Number def
            else:
                data[Data.Global][s_exp[1]] = s_exp[2]

        case "set":
            assert len(s_exp) == 3, "Invalid var modifying!"
            assert data[Data.Global].get(s_exp[1]) != None, "Non-existing var!"
            construct(s_exp[2])
            # "Value to set" in ACC after constructing
            add_inst(Opcode.STORE, s_exp[1])

        case "if":
            construct(s_exp[1])
            jmp_stack.append(icounter)
            add_inst(Opcode.JIL, None)
            construct(s_exp[2])
            instr[jmp_stack.pop()][1] = icounter + 1
            jmp_stack.append(icounter)
            # Avoiding "Else"
            add_inst(Opcode.JMP, None)
            construct(s_exp[3])
            instr[jmp_stack.pop()][1] = icounter

        case "==":
            construct(s_exp[1])
            add_inst(Opcode.STORE, Data.Spec)
            construct(s_exp[2])
            add_inst(Opcode.SUB, Data.Spec)

        case _:  # Constants or vars to Load

            # Number const
            if str(s_exp).isnumeric():
                data[Data.Const][const_counter] = s_exp
                add_inst(Opcode.LOAD, const_counter)
                const_counter += 1

            # String const
            elif str(s_exp)[0].startswith("\""):
                add_str(Data.Const, None, str(s_exp))

            # Var to Load
            else:
                assert data[Data.Global].get(
                    str(s_exp)) != None, "Non-existing var!"
                add_inst(Opcode.LOAD, s_exp)


# Instructions -> (number, opcode, operand's addr | None)
instr = {}


def translate(source: str):
    model = convert_to_lists(to_tokens(source))
    for top_exp in model:
        construct(top_exp)
    add_inst(Opcode.HALT, None)
    return instr, data


def main(source_path, target_instr_path, target_data_path):
    with open(source_path, encoding="utf-8") as file:
        source = file.read()
        source = "(" + source + ")"
        instr, data = translate(source)

        from pprint import pprint
        pprint(instr)
        pprint(data)
        # make_file(target_instr_path, instructions)
        # make_file(target_instr_path, data)


if __name__ == "__main__":
    assert len(sys.argv) == 4
    _, source_path, target_instr_path, target_data_path = sys.argv
    main(source_path, target_instr_path, target_data_path)
