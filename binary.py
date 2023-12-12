from pprint import pprint
from data import Data, word, anon_offset


def binary_transform(instructions, data):

    pprint(data)
    pprint(instructions)

    with open('instructions', 'wb') as file:
        file.write(b'\x00' * 16 * 1024)
        file.seek(0)
        for _, instruction in instructions.items():
            to_dump = instruction[0].value
            mem = instruction[1]
            shift = instruction[2]
            match to_dump[2]:
                case "1":
                    file.write(int(to_dump, 16).to_bytes(16, 'big'))
                case "A":
                    if mem == Data.EStack:
                        to_dump = list(to_dump)
                        to_dump[3] = '4'
                        file.write(
                            (int("".join(to_dump), 16) | shift).to_bytes(16, 'big'))
                    elif mem == Data.FStack:
                        to_dump = list(to_dump)
                        to_dump[3] = '4'
                        file.write((int("".join(to_dump), 16)
                                   | shift).to_bytes(16, 'big'))
                    elif isinstance(mem, str):
                        addr = data[Data.Named].get(mem)[0]
                        file.write(
                            (int(to_dump, 16) | addr).to_bytes(16, 'big'))
                    else:
                        file.write(
                            (int(to_dump, 16) | mem).to_bytes(16, 'big'))

                case "B":
                    if mem == Data.EStack:
                        to_dump = list(to_dump)
                        to_dump[3] = '4'
                        file.write(
                            (int("".join(to_dump), 16) | shift).to_bytes(16, 'big'))
                    elif mem == Data.FStack:
                        to_dump = list(to_dump)
                        to_dump[3] = '8'
                        file.write(
                            (int("".join(to_dump), 16) | shift).to_bytes(16, 'big'))
                    else:
                        addr = data[Data.Named].get(mem)[0]
                        file.write(
                            (int(to_dump, 16) | addr).to_bytes(16, 'big'))
                case _:
                    file.write((int(to_dump, 16) | mem).to_bytes(16, 'big'))
    with open('data', 'wb') as file:
        file.write(b'\x00' * 32 * 1024)
        file.seek(0)
        for _, value in data[Data.Named].items():
            file.write(value[2].to_bytes(32, 'big'))
        file.seek(word * anon_offset)
        for _, value in data[Data.Anon].items():
            if isinstance(value, str):
                file.write(ord(value).to_bytes(32, 'big'))
            else:
                file.write(value.to_bytes(32, 'big'))
