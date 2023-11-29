import sys

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


dcounter = 0
icounter = 0


def add_inst(instruction, additional):
    global icounter
    instr[icounter] = [instruction, additional]
    icounter += 1


jmp_stack = []


def construct(s_exp):
    global dcounter, icounter
    match s_exp[0]:
        case "define":
            assert len(s_exp) == 3, "Invalid var definition!"
            data[s_exp[1]] = [s_exp[2]]  # Name and init value
        case "set":
            assert len(s_exp) == 3, "Invalid var modifying!"
            assert data.get(s_exp[1]) != None, "Non-existing var!"
            construct(s_exp[2])
            # Value already in ACC store to var in memory
            add_inst(Opcode.STORE, s_exp[1])
        case "if":
            construct(s_exp[1])
            jmp_stack.append(icounter)
            add_inst(Opcode.JIL, None)
            construct(s_exp[2])
            instr[jmp_stack.pop()][1] = icounter
            construct(s_exp[3])
        case "==":
            construct(s_exp[1])
            add_inst(Opcode.PUSH, None)
            construct(s_exp[2])
            add_inst(Opcode.SUB, None)


instr = {}
data = {}


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
