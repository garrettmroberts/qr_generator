from PIL import Image

from alignment_pattern_utils import render_alignment_pattern
from constants import QR_CAPACITY_BYTE_MODE, MODE_INDICATORS


def get_minimum_version(txt, error_correction='L'):
    text_length = len(txt)
    
    for version in range(1, 41):
        capacity = QR_CAPACITY_BYTE_MODE[version][error_correction]
        if text_length <= capacity:
            return version
    
    raise ValueError(f"Text is too long ({text_length} bytes). Maximum capacity is {QR_CAPACITY_BYTE_MODE[40][error_correction]} bytes for error correction level {error_correction}.")

def add_padding(bit_string, version, error_correction='L'):
    # Calculate total capacity in bits (capacity in bytes * 8 bits per byte)
    capacity_bytes = QR_CAPACITY_BYTE_MODE[version][error_correction]
    capacity_bits = capacity_bytes * 8
    
    current_length = len(bit_string)
    
    # Check if data already fits
    if current_length > capacity_bits:
        raise ValueError(f"Data length ({current_length} bits) exceeds capacity ({capacity_bits} bits)")
    
    # Step 1: Add up to 4 terminator bits (already included in bit_string usually)
    # Step 2: Add 0s to make the length a multiple of 8
    remainder = current_length % 8
    if remainder != 0:
        padding_bits = 8 - remainder
        bit_string += '0' * padding_bits
        current_length += padding_bits
    
    # Step 3: Add padding bytes (alternating 11101100 and 00010001)
    padding_byte_1 = '11101100'  # 0xEC (236)
    padding_byte_2 = '00010001'  # 0x11 (17)
    
    bytes_needed = (capacity_bits - current_length) // 8
    
    for i in range(bytes_needed):
        if i % 2 == 0:
            bit_string += padding_byte_1
        else:
            bit_string += padding_byte_2
    
    return bit_string

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
    mode = MODE_INDICATORS['byte']
    count = format(len(txt), '08b')
    txt_stream = ''.join(format(ord(char), '08b') for char in txt)
    terminator = MODE_INDICATORS['terminator']
    
    # Build the encoded data
    encoded_data = mode + count + txt_stream + terminator
    
    # Add padding to fill the QR code capacity
    padded_data = add_padding(encoded_data, version, error_correction)
    
    print(f"Padded bit string: {padded_data}")



    # Draw QR Code
    img = draw_matrix(matrix)
    img.show()

