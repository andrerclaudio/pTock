# All characters are stored in the lower 15 bits of u16 integers.
# After the most significant dummy bit, the bitmaps are layed
# out as 5x3 grids, starting from the top left and running across
# in rows until the least significant bit at the bottom right.

# Height of a single character in bits.
H: int = 5

# Width of a single character in bits.
W: int = 3

# ...
# .x.
# ...
# .x.
# ...
# Bitmap ':' character.
COLON: str = "0000010000010000"

# ...
# ...
# ...
# ...
# ...
# Bitmap ' ' character.
SPACE: int = 0b0000000000000000

# .x.
# x.x
# xxx
# x.x
# x.x
# Bitmap 'A' character.
A: int = 0b0010101111101101

# xxx
# x.x
# xxx
# x..
# x..
# Bitmap 'P' character.
P: int = 0b0111101111100100

# x.x
# xxx
# x.x
# x.x
# x.x
# Bitmap 'M' character.
M: int = 0b0101111101101101

# Bitmap digits from '0' - '9'.
DIGIT: str = [
    # xxx
    # x.x
    # x.x
    # x.x
    # xxx
    "0111101101101111",
    # .x.
    # xx.
    # .x.
    # .x.
    # xxx
    "0010110010010111",
    # xxx
    # ..x
    # xxx
    # x..
    # xxx
    "0111001111100111",
    # xxx
    # ..x
    # xxx
    # ..x
    # xxx
    "0111001111001111",
    # x.x
    # x.x
    # xxx
    # ..x
    # ..x
    "0101101111001001",
    # xxx
    # x..
    # xxx
    # ..x
    # xxx
    "0111100111001111",
    # xxx
    # x..
    # xxx
    # x.x
    # xxx
    "0111100111101111",
    # xxx
    # ..x
    # ..x
    # ..x
    # ..x
    "0111001001001001",
    # xxx
    # x.x
    # xxx
    # x.x
    # xxx
    "0111101111101111",
    # xxx
    # x.x
    # xxx
    # ..x
    # xxx
    "0111101111001111",
]
