from enum import Enum
import sys
import string

from isa import Opcode
import re


def get_tokens(source: str):
    tokens = []
    source.split


def get_top_exps(source: str) -> [str]:
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


def is_nested(exp: str) -> bool:
    return exp[0] == '(' and exp[len(exp) - 1] == ')'


def to_tokens(s_exp: str) -> [str]:
    return s_exp.replace('(', ' ( ').replace(')', ' ) ').split()


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


class Ret(Enum):
    CONST = 1,
    GLOB = 2,
    SPEC = 3


def construct(s_exp: [str]):  # -> [Ret, int | str | None]:
    global icounter, jmp_stack, const_counter
    match s_exp[0]:

        case "define":
            assert len(s_exp) == 3, "Invalid var definition!"
            data['glob'][s_exp[1]] = s_exp[2]  # Name and init value
            # return [False, s_exp[1]]

        case "set":
            assert len(s_exp) == 3, "Invalid var modifying!"
            assert data['glob'].get(s_exp[1]) != None, "Non-existing var!"
            construct(s_exp[2]) # Set res to Acc
            # case Ret.SPEC:
            #     add_inst(Opcode.LOAD, 'spec')
            # case Ret.CONST:
            #     add_inst(Opcode.LOAD, construct(s_exp[2])[1])
            # case Ret.GLOB:
            #     add_inst(Opcode.LOAD, construct(s_exp[2])[1])
            add_inst(Opcode.STORE, s_exp[1])

        case "if":
            construct(s_exp[1])
            jmp_stack.append(icounter)
            add_inst(Opcode.JIL, None)
            construct(s_exp[2])
            instr[jmp_stack.pop()][1] = icounter
            jmp_stack.append(icounter)
            add_inst(Opcode.JMP, None)
            construct(s_exp[3])
            instr[jmp_stack.pop()][1] = icounter

        case "==":
            construct(s_exp[1])
            add_inst(Opcode.STORE, 'spec') # Spec - buffer for 2-op commands
            construct(s_exp[2])
            add_inst(Opcode.SUB, 'spec')

        case _:  # Constants or vars
            if s_exp[0].isnumeric():
                data['const'][const_counter] = s_exp[0]
                add_inst(Opcode.LOAD, const_counter)
                const_counter += 1
                # return [True, const_counter]
            else:
                assert data.get(s_exp[1]) != None, "Non-existing var!"
                add_inst(Opcode.LOAD, s_exp[1])


instr = {}
data = {'glob': {}, 'const': {}, 'spec1': 0}


def translate(source: str):
    source = source.strip().replace('\n', '')
    model = convert_to_lists(to_tokens(source))
    for top_exp in model:
        construct(top_exp)
    return instr, data


def main(source_path, target_instr_path, target_data_path):
    with open(source_path, encoding="utf-8") as file:
        source = file.read()
        source += ")"
        source = "(" + source
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
