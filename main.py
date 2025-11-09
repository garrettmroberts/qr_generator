from PIL import Image

from alignment_pattern_utils import render_alignment_pattern
from constants import QR_CAPACITY_BYTE_MODE, MODE_INDICATORS, ECC_CODEWORDS_PER_BLOCK

# Galois Field (GF(2^8)) Log and Antilog tables
GF_EXP = [0] * 512
GF_LOG = [0] * 256

# Initialize the tables
x = 1
for i in range(255):
    GF_EXP[i] = x
    GF_LOG[x] = i
    x <<= 1
    if x & 0x100:
        x ^= 0x11D  # Primitive polynomial for QR codes: x^8 + x^4 + x^3 + x^2 + 1

# Mirror the EXP table for convenience
for i in range(255, 512):
    GF_EXP[i] = GF_EXP[i - 255]

def gf_multiply(a, b):
    """Multiply two numbers in GF(2^8)"""
    if a == 0 or b == 0:
        return 0
    return GF_EXP[GF_LOG[a] + GF_LOG[b]]

def gf_polynomial_multiply(p1, p2):
    """Multiply two polynomials over GF(2^8)"""
    product = [0] * (len(p1) + len(p2) - 1)
    for i in range(len(p1)):
        for j in range(len(p2)):
            product[i + j] ^= gf_multiply(p1[i], p2[j])
    return product

def gf_polynomial_divide(dividend, divisor):
    """Divide two polynomials over GF(2^8)"""
    result = list(dividend)
    for i in range(len(dividend) - len(divisor) + 1):
        coef = result[i]
        if coef != 0:
            for j in range(1, len(divisor)):
                result[i + j] ^= gf_multiply(divisor[j], coef)
    
    separator = -(len(divisor) - 1)
    return result[separator:]

def reed_solomon_generator(degree):
    """Generate a Reed-Solomon generator polynomial of a given degree"""
    poly = [1]
    for i in range(degree):
        poly = gf_polynomial_multiply(poly, [1, GF_EXP[i]])
    return poly

def reed_solomon_encode(data_bytes, num_ec_bytes):
    """
    Encode data with Reed-Solomon error correction.
    
    Args:
        data_bytes (list[int]): The data codewords
        num_ec_bytes (int): The number of error correction codewords to generate
        
    Returns:
        list[int]: The error correction codewords
    """
    generator = reed_solomon_generator(num_ec_bytes)
    
    # Pad the data with zeros for division
    padded_data = data_bytes + [0] * num_ec_bytes
    
    # Get the remainder (error correction codewords)
    return gf_polynomial_divide(padded_data, generator)


def generate_error_correction(padded_data, version, error_correction):
    """
    Generate and interleave error correction codewords.
    
    Returns:
        str: The final bit string with data and error correction
    """
    # Convert bit string to byte array
    data_bytes = [int(padded_data[i:i+8], 2) for i in range(0, len(padded_data), 8)]
    
    # Get block info
    block_info = ECC_CODEWORDS_PER_BLOCK[version][error_correction]
    num_ec_bytes_per_block = block_info[0]
    
    # Split blocks (Group 1 and Group 2)
    group1_blocks = block_info[1]
    group1_codewords = block_info[2]
    
    if len(block_info) > 3:
        group2_blocks = block_info[3]
        group2_codewords = block_info[4]
    else:
        group2_blocks = 0
        group2_codewords = 0

    total_data_codewords = group1_blocks * group1_codewords + group2_blocks * group2_codewords
    
    # Split data into blocks
    data_blocks = []
    start = 0
    for i in range(group1_blocks):
        end = start + group1_codewords
        data_blocks.append(data_bytes[start:end])
        start = end
    
    for i in range(group2_blocks):
        end = start + group2_codewords
        data_blocks.append(data_bytes[start:end])
        start = end
        
    # Generate error correction for each block
    ec_blocks = []
    for block in data_blocks:
        ec_blocks.append(reed_solomon_encode(block, num_ec_bytes_per_block))
        
    # Interleave data and error correction codewords
    final_codewords = []
    
    # Interleave data
    max_data_len = max(len(b) for b in data_blocks)
    for i in range(max_data_len):
        for block in data_blocks:
            if i < len(block):
                final_codewords.append(block[i])
                
    # Interleave error correction
    max_ec_len = max(len(b) for b in ec_blocks)
    for i in range(max_ec_len):
        for block in ec_blocks:
            if i < len(block):
                final_codewords.append(block[i])

    # Convert back to bit string
    final_bit_string = ''.join(format(byte, '08b') for byte in final_codewords)
    
    # Add remainder bits if necessary
    total_capacity_bits = (
        (group1_blocks * group1_codewords) +
        (group2_blocks * group2_codewords) +
        (group1_blocks + group2_blocks) * num_ec_bytes_per_block
    ) * 8
    
    if len(final_bit_string) < total_capacity_bits:
         final_bit_string += '0' * (total_capacity_bits - len(final_bit_string))
    
    return final_bit_string

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

def is_reserved(matrix, row, col):
    """Check if a module position is reserved (already used by patterns)"""
    size = len(matrix)
    
    # Top-left
    if row < 9 and col < 9:
        return True
    # Top-right
    if row < 9 and col >= size - 8:
        return True
    # Bottom-left
    if row >= size - 8 and col < 9:
        return True
    
    # Timing patterns (row 6 and column 6)
    if row == 6 or col == 6:
        return True
    
    return False

def embed_data(matrix, bit_string):
    """
    Embed the data bit string into the QR code matrix.
    Data is placed in a zigzag pattern starting from bottom-right.
    """
    size = len(matrix)
    bit_index = 0
    
    # Start from the rightmost column
    col = size - 1
    direction = -1  # -1 for going up, 1 for going down
    
    while col > 0 and bit_index < len(bit_string):
        # Skip the vertical timing column (column 6)
        if col == 6:
            col -= 1
        
        # Process two columns at a time (right column, then left column)
        for row in range(size):
            # Calculate actual row based on direction
            if direction == -1:
                actual_row = size - 1 - row
            else:
                actual_row = row
            
            # Process right column of the pair
            if not is_reserved(matrix, actual_row, col):
                if bit_index < len(bit_string):
                    matrix[actual_row][col] = int(bit_string[bit_index])
                    bit_index += 1
            
            # Process left column of the pair
            if not is_reserved(matrix, actual_row, col - 1):
                if bit_index < len(bit_string):
                    matrix[actual_row][col - 1] = int(bit_string[bit_index])
                    bit_index += 1
        
        # Move to the next pair of columns (2 columns to the left)
        col -= 2
        # Reverse direction for zigzag pattern
        direction *= -1
    
    return matrix

def get_mask_pattern(pattern_number, row, col):
    if pattern_number == 0:
        return (row + col) % 2 == 0
    elif pattern_number == 1:
        return row % 2 == 0
    elif pattern_number == 2:
        return col % 3 == 0
    elif pattern_number == 3:
        return (row + col) % 3 == 0
    elif pattern_number == 4:
        return (row // 2 + col // 3) % 2 == 0
    elif pattern_number == 5:
        return ((row * col) % 2) + ((row * col) % 3) == 0
    elif pattern_number == 6:
        return (((row * col) % 2) + ((row * col) % 3)) % 2 == 0
    elif pattern_number == 7:
        return (((row + col) % 2) + ((row * col) % 3)) % 2 == 0
    else:
        raise ValueError(f"Invalid mask pattern number: {pattern_number}. Must be 0-7.")

def is_data_module(matrix, row, col):
    size = len(matrix)
    
    # Finder patterns with separators (8x8 areas)
    # Top-left
    if row < 9 and col < 9:
        return False
    # Top-right
    if row < 9 and col >= size - 8:
        return False
    # Bottom-left
    if row >= size - 8 and col < 9:
        return False
    
    # Timing patterns (row 6 and column 6)
    if row == 6 or col == 6:
        return False
    
    # Format information areas (will be added later)
    # These are around the finder patterns
    
    # Alignment patterns (for version 2+, will need to check specific positions)
    # For now, we'll handle this simply
    
    return True

def apply_mask(matrix, pattern_number):
    import copy
    size = len(matrix)
    masked_matrix = copy.deepcopy(matrix)
    
    for row in range(size):
        for col in range(size):
            # Only apply mask to data modules
            if is_data_module(masked_matrix, row, col):
                if get_mask_pattern(pattern_number, row, col):
                    # XOR operation: flip the bit
                    masked_matrix[row][col] = 1 - masked_matrix[row][col]
    
    return masked_matrix

def evaluate_mask_penalty(matrix):
    size = len(matrix)
    penalty = 0
    
    # Rule 1: Adjacent modules in same row/column
    # Penalty for runs of 5+ same-color modules
    for row in range(size):
        # Check horizontal runs
        count = 1
        prev = matrix[row][0]
        for col in range(1, size):
            if matrix[row][col] == prev:
                count += 1
            else:
                if count >= 5:
                    penalty += (count - 5) + 3
                count = 1
                prev = matrix[row][col]
        if count >= 5:
            penalty += (count - 5) + 3
    
    for col in range(size):
        # Check vertical runs
        count = 1
        prev = matrix[0][col]
        for row in range(1, size):
            if matrix[row][col] == prev:
                count += 1
            else:
                if count >= 5:
                    penalty += (count - 5) + 3
                count = 1
                prev = matrix[row][col]
        if count >= 5:
            penalty += (count - 5) + 3
    
    # Rule 2: 2x2 blocks of same color
    for row in range(size - 1):
        for col in range(size - 1):
            color = matrix[row][col]
            if (matrix[row][col + 1] == color and
                matrix[row + 1][col] == color and
                matrix[row + 1][col + 1] == color):
                penalty += 3
    
    # Rule 3: Patterns similar to finder patterns (1:1:3:1:1 ratio)
    # Simplified version - checking for specific pattern
    finder_pattern_dark = [1, 0, 1, 1, 1, 0, 1]
    finder_pattern_light = [0, 1, 0, 0, 0, 1, 0]
    
    # Check horizontal
    for row in range(size):
        for col in range(size - 6):
            segment = [matrix[row][col + i] for i in range(7)]
            if segment == finder_pattern_dark or segment == finder_pattern_light:
                penalty += 40
    
    # Check vertical
    for col in range(size):
        for row in range(size - 6):
            segment = [matrix[row + i][col] for i in range(7)]
            if segment == finder_pattern_dark or segment == finder_pattern_light:
                penalty += 40
    
    # Rule 4: Balance of dark and light modules
    dark_count = sum(sum(row) for row in matrix)
    total_modules = size * size
    dark_ratio = (dark_count / total_modules) * 100
    deviation = abs(dark_ratio - 50)
    penalty += int(deviation / 5) * 10
    
    return penalty

def choose_best_mask(matrix):
    best_penalty = float('inf')
    best_matrix = None
    best_pattern = 0
    
    for pattern in range(8):
        masked = apply_mask(matrix, pattern)
        penalty = evaluate_mask_penalty(masked)
        
        if penalty < best_penalty:
            best_penalty = penalty
            best_matrix = masked
            best_pattern = pattern
    
    print(f"Best mask pattern: {best_pattern} (penalty: {best_penalty})")
    return best_matrix, best_pattern

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
    
    # Generate error correction and interleave
    final_data = generate_error_correction(padded_data, version, error_correction)
    
    print(f"Final bit string length: {len(final_data)} bits")
    
    # Embed the data into the QR code matrix
    embed_data(matrix, final_data)
    
    # Choose and apply the best mask pattern
    masked_matrix, mask_pattern = choose_best_mask(matrix)

    # Draw QR Code
    img = draw_matrix(masked_matrix)
    img.show()

