from __future__ import annotations


def to_tokens(source: str) -> list[str]:
    return source.strip().replace("\n", "").replace("(", " ( ").replace(")", " ) ").split()


def convert_to_lists(tokens: list):
    token = tokens.pop(0)
    if token == "(":
        temp = []
        while tokens[0] != ")":
            temp.append(convert_to_lists(tokens))
        tokens.pop(0)
        return temp
    return token
