from PIL import Image

from alignment_pattern_utils import render_alignment_pattern

# QR Code data capacity table for Byte mode (characters)
# Format: version -> {error_correction_level -> capacity}
QR_CAPACITY_BYTE_MODE = {
    1: {'L': 17, 'M': 14, 'Q': 11, 'H': 7},
    2: {'L': 32, 'M': 26, 'Q': 20, 'H': 14},
    3: {'L': 53, 'M': 42, 'Q': 32, 'H': 24},
    4: {'L': 78, 'M': 62, 'Q': 46, 'H': 34},
    5: {'L': 106, 'M': 84, 'Q': 60, 'H': 44},
    6: {'L': 134, 'M': 106, 'Q': 74, 'H': 58},
    7: {'L': 154, 'M': 122, 'Q': 86, 'H': 64},
    8: {'L': 192, 'M': 152, 'Q': 108, 'H': 84},
    9: {'L': 230, 'M': 180, 'Q': 130, 'H': 98},
    10: {'L': 271, 'M': 213, 'Q': 151, 'H': 119},
    11: {'L': 321, 'M': 251, 'Q': 177, 'H': 137},
    12: {'L': 367, 'M': 287, 'Q': 203, 'H': 155},
    13: {'L': 425, 'M': 331, 'Q': 241, 'H': 177},
    14: {'L': 458, 'M': 362, 'Q': 258, 'H': 194},
    15: {'L': 520, 'M': 412, 'Q': 292, 'H': 220},
    16: {'L': 586, 'M': 450, 'Q': 322, 'H': 250},
    17: {'L': 644, 'M': 504, 'Q': 364, 'H': 280},
    18: {'L': 718, 'M': 560, 'Q': 394, 'H': 310},
    19: {'L': 792, 'M': 624, 'Q': 442, 'H': 338},
    20: {'L': 858, 'M': 666, 'Q': 482, 'H': 382},
    21: {'L': 929, 'M': 711, 'Q': 509, 'H': 403},
    22: {'L': 1003, 'M': 779, 'Q': 565, 'H': 439},
    23: {'L': 1091, 'M': 857, 'Q': 611, 'H': 461},
    24: {'L': 1171, 'M': 911, 'Q': 661, 'H': 511},
    25: {'L': 1273, 'M': 997, 'Q': 715, 'H': 535},
    26: {'L': 1367, 'M': 1059, 'Q': 751, 'H': 593},
    27: {'L': 1465, 'M': 1125, 'Q': 805, 'H': 625},
    28: {'L': 1528, 'M': 1190, 'Q': 868, 'H': 658},
    29: {'L': 1628, 'M': 1264, 'Q': 908, 'H': 698},
    30: {'L': 1732, 'M': 1370, 'Q': 982, 'H': 742},
    31: {'L': 1840, 'M': 1452, 'Q': 1030, 'H': 790},
    32: {'L': 1952, 'M': 1538, 'Q': 1112, 'H': 842},
    33: {'L': 2068, 'M': 1628, 'Q': 1168, 'H': 898},
    34: {'L': 2188, 'M': 1722, 'Q': 1228, 'H': 958},
    35: {'L': 2303, 'M': 1809, 'Q': 1283, 'H': 983},
    36: {'L': 2431, 'M': 1911, 'Q': 1351, 'H': 1051},
    37: {'L': 2563, 'M': 1989, 'Q': 1423, 'H': 1093},
    38: {'L': 2699, 'M': 2099, 'Q': 1499, 'H': 1139},
    39: {'L': 2809, 'M': 2213, 'Q': 1579, 'H': 1219},
    40: {'L': 2953, 'M': 2331, 'Q': 1663, 'H': 1273},
}

def get_minimum_version(txt, error_correction='L'):
    text_length = len(txt)
    
    for version in range(1, 41):
        capacity = QR_CAPACITY_BYTE_MODE[version][error_correction]
        if text_length <= capacity:
            return version
    
    raise ValueError(f"Text is too long ({text_length} bytes). Maximum capacity is {QR_CAPACITY_BYTE_MODE[40][error_correction]} bytes for error correction level {error_correction}.")

def get_module_count(matrix):
    return len(matrix)

def init_matrix(version):
    number_of_modules = 17 + 4 * version
    matrix = [i for i in range(number_of_modules)]
    for i in range(number_of_modules):
        matrix[i] = [0 for i in range(number_of_modules)]
    return matrix

def draw_matrix(matrix, pixel_size = 10):
    rows = len(matrix)
    cols = len(matrix)
    border = 4

    img_size = (
        (cols + border * 2) * pixel_size,
        (rows + border * 2) * pixel_size
    )

    img = Image.new("RGB", img_size, "white")
    pixels = img.load()


    for y in range(rows):
        for x in range(cols):
            color = 0 if matrix[y][x] == 1 else 255
            for dy in range(pixel_size):
                for dx in range(pixel_size):
                    pixels[
                        (x + border) * pixel_size + dx,
                        (y + border) * pixel_size + dy
                    ] = (color, color, color)
    return img

def render_finder_pattern(matrix):
    # Top left finder pattern
    for i in range(7):
        matrix[0][i] = 1
        matrix[i][0] = 1
        matrix[6][i] = 1
        matrix[i][6] = 1
    for i in range(2,5):
        for j in range(2,5):
            matrix[i][j] = 1
    
    # Top right finder pattern
    for i in range(len(matrix) - 7, len(matrix)):
        matrix[0][i] = 1
        matrix[6][i] = 1
        matrix[len(matrix) - i - 1][len(matrix) - 1] = 1
        matrix[len(matrix) - i - 1][len(matrix) - 7] = 1
    for i in range(2,5):
        for j in range(len(matrix) - 5, len(matrix) - 2):
            matrix[i][j] = 1
    
    # Bottom left finder pattern
    for i in range(len(matrix) - 7, len(matrix)):
        matrix[i][0] = 1
        matrix[i][6] = 1
        matrix[len(matrix) - 7][len(matrix)  - i - 1] = 1
        matrix[len(matrix) - 1][len(matrix) - i - 1] = 1
    for i in range(len(matrix) - 5, len(matrix) - 2):
        for j in range(2,5):
            matrix[i][j] = 1

def render_timing_pattern(matrix):
    for i in range(8, len(matrix) - 8):
        matrix[i][6] = 1 if i % 2 == 0 else 0
        matrix[6][i] = 1 if i % 2 == 0 else 0

if __name__ == "__main__":
    txt = "Hello, world."
    error_correction = 'L'  # Options: 'L', 'M', 'Q', 'H'
    
    # Automatically determine the minimum version needed for the text
    version = get_minimum_version(txt, error_correction)

    # Define initial patterns
    matrix = init_matrix(version)
    print('module_count', get_module_count(matrix))
    render_finder_pattern(matrix)
    render_timing_pattern(matrix)
    if version >= 2:
        render_alignment_pattern(matrix, version)
    
    # Parse data
    txt_stream = ''.join(format(ord(char), '08b') for char in txt)

    # Draw QR Code
    img = draw_matrix(matrix)
    img.show()

