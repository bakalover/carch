from typing import List


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


# def get_top_exps(source: str) -> List[str]:
#     top_exps = []
#     l, r = 0, 0
#     counter = 0
#     for c in source:
#         if c == '(':
#             counter += 1
#         if c == ")":
#             counter -= 1
#             if counter == 0:
#                 # Slice that contains  s-exp with brackets
#                 top_exps.append(source[l: r+1])
#                 l = r + 1
#         r += 1
#         assert counter >= 0, "Brackets!"
#     assert counter == 0, "Brackets!"
#     return top_exps
