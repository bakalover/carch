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


def construct(s_exp, instr, data):
    if isinstance(s_exp, str):
        data.append(['Data Addr', s_exp])
        # instr.append({'Instr Addr', Opcode.LOAD, 'Data Addr'})
    else:
        match s_exp[0]:
            case "if":
                construct(s_exp[1], instr, data)
                instr.append(['Instr Addr', Opcode.LOAD, 'Data Addr'])
                instr.append(['Instr Addr', Opcode.CMP, 'Data Addr'])

                # acc >= 0
                instr.append(['Instr Addr', Opcode.JZ, 'Data Addr'])
                construct(s_exp[2], instr, data)
                construct(s_exp[3], instr, data)
            case "==":
                construct(s_exp[1], instr, data)
                instr.append(['Instr Addr', Opcode.LOAD, 'Data Addr'])
                instr.append(['Instr Addr', Opcode.CMP, 'Data Addr'])
                instr.append(['Instr Addr', Opcode.JZ, 'Data Addr'])
                construct(s_exp[2], instr, data)


def translate(source: str):
    instr = []
    data = []
    source = source.strip().replace('\n', '')
    model = convert_to_lists(to_tokens(source))
    for top_exp in model:
        construct(top_exp, instr, data)
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
