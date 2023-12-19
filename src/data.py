# Data word size
from enum import Enum

# In bytes
DATAWORD: int = 4 
INSTRWORD: int = 2

# Offset by 256 words
anon_offset: int = 0x100


class Data(Enum):
    Named = 1,
    Anon = 2,
    FStack = 3,
    EStack = 4,
    Ar = 5
