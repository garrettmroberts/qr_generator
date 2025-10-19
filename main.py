from PIL import Image
from random import randint

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
        matrix[i][5] = 1 if i % 2 == 0 else 0
        matrix[5][i] = 1 if i % 2 == 0 else 0

def render_alignment_pattern(matrix, version):
    # V2-V6
    if version > 1 and version < 7:
        for i in range(len(matrix) - 9, len(matrix) - 4):
            matrix[len(matrix) - 5][i] = 1
            matrix[len(matrix) - 9][i] = 1
            matrix[i][len(matrix) - 5] = 1
            matrix[i][len(matrix) - 9] = 1
        matrix[len(matrix) - 7][len(matrix) - 7] = 1

    # V7-V13

    # V14-V20

    # V21-V27

    # V28-V34

    # V35-V40


if __name__ == "__main__":
    version = 2
    txt = "Hello, world."

    # Define initial patterns
    matrix = init_matrix(version)
    render_finder_pattern(matrix)
    render_timing_pattern(matrix)
    if version >= 2:
        render_alignment_pattern(matrix, version)
    
    # Parse data
    txt_stream = ''.join(format(ord(char), '08b') for char in txt)
    print(txt_stream)

    # Draw QR Code
    img = draw_matrix(matrix)
    img.show()

