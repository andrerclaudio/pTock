# All characters are stored in a 15 bits string variable each.
# The bitmaps are layed out as 5x3 grids, starting from the
# top left and running across in rows until the least significant
# bit at the bottom right.

# Height of a single character in bits.
SHAPE_HEIGHT: int = 5

# Width of a single character in bits.
SHAPE_WIDTH: int = 3

# ...
# .x.
# ...
# .x.
# ...
# Bitmap ':' character.
COLON: str = "000010000010000"

# ...
# ...
# ...
# ...
# ...
# Bitmap ' ' character.
SPACE: str = "000000000000000"

# .x.
# x.x
# xxx
# x.x
# x.x
# Bitmap 'A' character.
LETTER_A: str = "010101111101101"

# xxx
# x.x
# xxx
# x..
# x..
# Bitmap 'P' character.
LETTER_P: str = "111101111100100"

# x.x
# xxx
# x.x
# x.x
# x.x
# Bitmap 'M' character.
LETTER_M: str = "101111101101101"

# Bitmap digits from '0' - '9'.
DIGIT: list = [
    # xxx
    # x.x
    # x.x
    # x.x
    # xxx
    "111101101101111",
    # .x.
    # xx.
    # .x.
    # .x.
    # xxx
    "010110010010111",
    # xxx
    # ..x
    # xxx
    # x..
    # xxx
    "111001111100111",
    # xxx
    # ..x
    # xxx
    # ..x
    # xxx
    "111001111001111",
    # x.x
    # x.x
    # xxx
    # ..x
    # ..x
    "101101111001001",
    # xxx
    # x..
    # xxx
    # ..x
    # xxx
    "111100111001111",
    # xxx
    # x..
    # xxx
    # x.x
    # xxx
    "111100111101111",
    # xxx
    # ..x
    # ..x
    # ..x
    # ..x
    "111001001001001",
    # xxx
    # x.x
    # xxx
    # x.x
    # xxx
    "111101111101111",
    # xxx
    # x.x
    # xxx
    # ..x
    # xxx
    "111101111001111",
]
