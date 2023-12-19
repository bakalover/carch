from __future__ import annotations

import sys

from binary import binary_transform
from data import Data, anon_offset
from isa import Opcode
from parsing import convert_to_lists, to_tokens

jmp_stack = []
breaks = []

# "name" aka ctx: [start_addr, arg: int]
functions = {}

icounter: int = 0x0
acounter: int = anon_offset
ncounter: int = 0x0


data = {Data.Named: {}, Data.Anon: {}}
instr = {}


def add_instr(instruction: Opcode,
              mem:  Data | str | int | None = None,
              shift: int = 0):
    global icounter
    instr[icounter] = [instruction, mem, shift]
    icounter += 1


# bool for string control
def construct(s_exp: list[str] | str, ctx: str | None = None) -> bool | None:
    global icounter, jmp_stack, acounter, ncounter, breaks

    match s_exp[0]:

        case "define":
            return define_var(list[str](s_exp))

        case "set":
            assert len(s_exp) == 3, "Invalid var modifying!"
            assert data[Data.Named].get(
                s_exp[1]) is not None, "Non-existing var!"
            is_str = construct(s_exp[2], ctx)
            add_instr(Opcode.EPOP)
            add_instr(Opcode.STORE, s_exp[1])
            add_instr(Opcode.EPUSH)  # S-exp ret
            return is_str

        case "defun":
            assert len(s_exp) == 4, "Invalid function definition!"
            functions[s_exp[1]] = [icounter, s_exp[2][0]]
            for exp in s_exp[3]:
                construct(exp, s_exp[1])  # Last BOI as ret on top of estack
            add_instr(Opcode.RET)  # Just ret (result on top of estack)
            return None

        case "fucall":
            assert len(s_exp) == 3, "Invalid function calling syntax!"
            assert functions.get(
                s_exp[1]) is not None, "Non-existing/visible funtion!"
            construct(s_exp[2], ctx)
            add_instr(Opcode.EPOP)  # From one stack
            add_instr(Opcode.FPUSH)  # to another

            # Place ret on stack and jump
            # After calling function result on EStack -> fun as s-exp
            add_instr(Opcode.CALL, functions[s_exp[1]][0])
            add_instr(Opcode.FPOP)  # Clearing function argument
            return None

        case "print":
            assert len(s_exp) == 2, "Invalid printing syntax!"
            is_str = construct(s_exp[1])
            if not is_str:
                add_instr(Opcode.EPOP)
                add_instr(Opcode.PRINT)
            else:
                jmp_stack.append(icounter)
                # After fetching => (acc -> ar)
                add_instr(Opcode.LOAD, Data.EStack)
                # Load by addr that already in Ar
                add_instr(Opcode.LOAD, Data.Ar)
                add_instr(Opcode.CMP)
                add_instr(Opcode.JZ, icounter + 4)
                add_instr(Opcode.PRINT)
                add_instr(Opcode.INCESTACK)
                add_instr(Opcode.JMP, jmp_stack.pop())
                add_instr(Opcode.EPOP)  # Clearing dirty estack top
            return None

        case "read":
            assert len(s_exp) == 2, "Invalid read syntax!"
            is_str = construct(s_exp[1])
            assert is_str, "Reading is supported only for strings!"
            jmp_stack.append(icounter)
            # Only for [eptr] -> acc -> ar purpose
            add_instr(Opcode.LOAD, Data.EStack)
            add_instr(Opcode.READ)
            add_instr(Opcode.CMP)
            add_instr(Opcode.JZ, icounter + 4)
            add_instr(Opcode.STORE, Data.Ar)  # Store by addr in addr reg
            add_instr(Opcode.INCESTACK)
            add_instr(Opcode.JMP, jmp_stack.pop())
            add_instr(Opcode.CLEAR)
            add_instr(Opcode.STORE, Data.EStack)
            add_instr(Opcode.EPOP)
            return None

        case "if":
            construct(s_exp[1], ctx)
            add_instr(Opcode.EPOP)
            add_instr(Opcode.CMP)
            jmp_stack.append(icounter)
            add_instr(Opcode.JZ, None)
            is_str1 = construct(s_exp[2], ctx)
            instr[jmp_stack.pop()][1] = icounter + 1
            jmp_stack.append(icounter)
            add_instr(Opcode.JMP, None)
            is_str2 = construct(s_exp[3], ctx)
            instr[jmp_stack.pop()][1] = icounter
            return is_str1

        case "==":
            is_str1 = construct(s_exp[1], ctx)
            is_str2 = construct(s_exp[2], ctx)
            add_instr(Opcode.EPOP)
            add_instr(Opcode.SUB)  # acc = acc - [estack]
            add_instr(Opcode.ZERO)  # Loads zero flag
            add_instr(Opcode.STORE, Data.EStack)
            assert (not is_str1), "Can't compare with strings/Nops!"
            assert (not is_str2), "Can't compare with strings/Nops!"
            return False

        case "loop":
            jmp_stack.append(icounter)
            is_str = False
            for exp in s_exp[1]:
                is_str = construct(exp, ctx)
                # Each poping hense last one will be s-exp ret, otherwise -> estack leak
                add_instr(Opcode.EPOP)
            add_instr(Opcode.JMP, jmp_stack.pop())
            for i in range(len(breaks)):
                instr[breaks[i]][1] = icounter
            breaks = []

            return is_str  # That will be the last one s-exp's return

        case "break":
            is_str = construct(s_exp[1], ctx)  # Break ret on top of stack
            breaks.append(icounter)
            add_instr(Opcode.JMP, None)  # Get out of loop
            return is_str

        case "nop":
            add_instr(Opcode.EPUSH)  # Imitating s-exp
            add_instr(Opcode.NOP)  # Get out of loop
            return None

        case "+":
            is_str1 = construct(s_exp[1], ctx)
            is_str2 = construct(s_exp[2], ctx)
            add_instr(Opcode.EPOP)
            add_instr(Opcode.ADD)  # acc = acc + [estack]
            add_instr(Opcode.STORE, Data.EStack)
            assert (not is_str1), "Can't add to string!"
            assert (not is_str2), "Can't add to string!"
            return False

        case "%":
            # Construction order is important due estack
            is_str2 = construct(s_exp[2], ctx)
            is_str1 = construct(s_exp[1], ctx)
            add_instr(Opcode.EPOP)
            add_instr(Opcode.MOD)  # acc = acc % [estack]
            add_instr(Opcode.STORE, Data.EStack)
            assert (not is_str1), "Strings!"
            assert (not is_str2), "Strings!"
            return False

        case _:  # Constants or vars to Load
            s_exp = str(s_exp)
            return vars_construct(s_exp, ctx)


def define_var(s_exp: list[str]) -> None:
    global acounter, ncounter
    assert len(s_exp) == 3, "Invalid var definition!"

    # String def
    if s_exp[2].startswith('"') and s_exp[2].endswith('"'):
        data[Data.Named][s_exp[1]] = [ncounter, True, acounter]
        ncounter += 1
        for c in s_exp[2][1:-1]:
            data[Data.Anon][acounter] = c
            acounter += 1
        data[Data.Anon][acounter] = 0
        acounter += 1

    # Number def
    else:
        data[Data.Named][s_exp[1]] = [ncounter, False, int(s_exp[2])]
        ncounter += 1
    return


def vars_construct(s_exp: str, ctx):
    global acounter
    # Number const
    if s_exp.isnumeric():
        data[Data.Anon][acounter] = int(s_exp)
        add_instr(Opcode.LOAD, acounter)
        acounter += 1
        add_instr(Opcode.EPUSH)
        return False

    # String const
    if s_exp.startswith('"') and s_exp.endswith('"'):
        add_instr(Opcode.LOAD, acounter)
        add_instr(Opcode.EPUSH)
        # Giga chad pointer to next
        data[Data.Anon][acounter] = acounter + 1
        acounter += 1
        for c in s_exp[1:-1]:
            data[Data.Anon][acounter] = c
            acounter += 1
        data[Data.Anon][acounter] = 0
        acounter += 1
        return True

    # Var to Load
    if ctx is None:
        assert data[Data.Named].get(
            s_exp) is not None, 'Non-existing var: "{}"!'.format(s_exp)
        add_instr(Opcode.LOAD, s_exp)
        add_instr(Opcode.EPUSH)
        # returning flag "is it string"
        return data[Data.Named][s_exp][1]
    if data[Data.Named].get(s_exp) is not None:
        add_instr(Opcode.LOAD, s_exp)
        add_instr(Opcode.EPUSH)
        return data[Data.Named][s_exp][1]
    if functions[ctx][1] == s_exp:
        add_instr(Opcode.LOAD, Data.FStack, 1)
        add_instr(Opcode.EPUSH)
        return False  # Functions currently support only numbers (
    return None


def translate(source: str):
    model = convert_to_lists(to_tokens(source))
    add_instr(Opcode.JMP, None)
    is_main = False
    for top_exp in model:
        if top_exp[0] != "defun" and top_exp[0] != "define" and not is_main:
            is_main = True
            instr[0][1] = icounter
            construct(top_exp, None)
        else:
            construct(top_exp, None)
    add_instr(Opcode.HALT)


def main(source_path):
    with open(source_path, encoding="utf-8") as file:
        source = file.read()
        source = "(" + source + ")"
        translate(source)
        binary_transform(instr, data)


if __name__ == "__main__":
    assert len(sys.argv) == 2
    _, source_path = sys.argv
    main(source_path)
