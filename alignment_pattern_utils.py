def get_shift_change(version):
    shift_change = None

    if version <= 13:
        shift_change = version * 2 + 2
    elif version == 14:
        shift_change = 20
    elif version == 15:
        shift_change = 22
    elif version == 16 or version == 17:
        shift_change = 24
    elif version == 18:
        shift_change = 26
    elif version == 19 or version == 20:
        shift_change = 28
    elif version == 21:
        shift_change = 22
    elif version == 22 or version == 23:
        shift_change = 24
    elif version == 24 or version == 25:
        shift_change = 26
    elif version == 26 or version == 27:
        shift_change = 28
    elif version == 28 or version == 29:
        shift_change = 24
    elif version == 30 or version == 31 or version == 32:
        shift_change = 26
    elif version == 33 or version == 34:
        shift_change = 28
    elif version == 35:
        shift_change = 24
    elif version >= 36 and version <= 38:
        shift_change = 26
    elif version == 39 or version == 40:
        shift_change = 28


    return shift_change

def get_first_step(version):
    first_step = None

    if version >= 14 and version <= 16:
        first_step = 20
    elif version >= 17 and version <= 19:
        first_step = 24
    elif version == 20:
        first_step = 28
    elif version == 21:
        first_step = 22
    elif version == 22:
        first_step = 20
    elif version == 23:
        first_step = 24
    elif version == 24:
        first_step = 22
    elif version == 25:
        first_step = 26
    elif version == 26:
        first_step = 24
    elif version == 27:
        first_step = 28
    elif version == 28:
        first_step = 20
    elif version == 29:
        first_step = 24
    elif version == 30:
        first_step = 20
    elif version == 31:
        first_step = 24
    elif version == 32:
        first_step = 28
    elif version == 33:
        first_step = 24
    elif version == 34:
        first_step = 28
    elif version == 35:
        first_step = 24
    elif version == 36:
        first_step = 18
    elif version == 37:
        first_step = 22
    elif version == 38:
        first_step = 26
    elif version == 39:
        first_step = 20
    elif version == 40:
        first_step = 24

    return first_step

def render_alignment_pattern_row(matrix, row_height, num_of_patterns, version, skip_right=False):
    shift = 6
    shift_change = get_shift_change(version)
    first_step = True

    if skip_right:
        if version >= 14 and first_step:
            shift += get_first_step(version)
        else:
            shift += shift_change
        first_step = False

    for i in range(num_of_patterns):
        matrix[len(matrix) - row_height - 1][len(matrix) - shift - 1] = 1

        i = 1
        while i >= -3:
            matrix[len(matrix) - row_height - 3][len(matrix) - shift + i] = 1
            matrix[len(matrix) - row_height + 1][len(matrix) - shift + i] = 1
            if i == 1 or i == -3:
                j = -2
                while j <= 1:
                    matrix[len(matrix) - row_height + j][len(matrix) - shift + 1] = 1
                    matrix[len(matrix) - row_height + j][len(matrix) - shift - 3] = 1
                    j += 1
            i -= 1
        
        if version >= 14 and first_step:
            shift += get_first_step(version)
            first_step = False
        else:
            shift += shift_change

def render_alignment_pattern(matrix, version):
    if version > 1 and version < 7:
        render_alignment_pattern_row(matrix, 6, 1, version)
    elif version >= 7 and version <= 13:
        i = 6
        shift = 2 * version + 2
        while i < len(matrix):
            if i + shift > len(matrix):
                render_alignment_pattern_row(matrix, i, 1, version, True)
            elif i == 6:
                render_alignment_pattern_row(matrix, i, 2, version)
            else:
                render_alignment_pattern_row(matrix, i, 3, version)
            i += shift
    elif version >= 14:
        i = 6
        shift = get_shift_change(version)
        first_step = True

        lowest_num_in_row = None
        if version <= 20:
            lowest_num_in_row = 2
        elif version <= 27:
            lowest_num_in_row = 3
        elif version <= 34:
            lowest_num_in_row = 4
        else:
            lowest_num_in_row = 5

        while i < len(matrix):
            if i + shift > len(matrix):
                render_alignment_pattern_row(matrix, i, lowest_num_in_row, version, True)
            elif i == 6:
                render_alignment_pattern_row(matrix, i, lowest_num_in_row + 1, version)
            else:
                render_alignment_pattern_row(matrix, i, lowest_num_in_row + 2, version)
            
            if first_step:
                i += get_first_step(version)
                first_step = False
            else:
                i += shift

