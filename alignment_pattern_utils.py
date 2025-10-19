def render_alignment_pattern_row(matrix, row_height, num_of_patterns, version, skip_right=False):
    shift = 6
    shift_change = version * 2 + 2
    if skip_right:
        shift += shift_change
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
        shift += shift_change

def render_alignment_pattern(matrix, version):
    if version > 1 and version < 7:
        for i in range(len(matrix) - 9, len(matrix) - 4):
            matrix[len(matrix) - 5][i] = 1
            matrix[len(matrix) - 9][i] = 1
            matrix[i][len(matrix) - 5] = 1
            matrix[i][len(matrix) - 9] = 1
        matrix[len(matrix) - 7][len(matrix) - 7] = 1
    elif version == 7:        
        render_alignment_pattern_row(matrix, 6, 2, 7)
        render_alignment_pattern_row(matrix, 22, 3, 7)
        render_alignment_pattern_row(matrix, 38, 1, 7, True)
    elif version == 8:
        render_alignment_pattern_row(matrix, 6, 2, 8)
        render_alignment_pattern_row(matrix, 24, 3, 8)
        render_alignment_pattern_row(matrix, 42, 1, 8, True)
    elif version == 9:
        render_alignment_pattern_row(matrix, 6, 2, 9)
        render_alignment_pattern_row(matrix, 26, 3, 9)
        render_alignment_pattern_row(matrix, 46, 1, 9, True)
    elif version == 10:
        render_alignment_pattern_row(matrix, 6, 2, 10)
        render_alignment_pattern_row(matrix, 28, 3, 10)
        render_alignment_pattern_row(matrix, 50, 1, 10, True)
    elif version == 11:
        render_alignment_pattern_row(matrix, 6, 2, 11)
        render_alignment_pattern_row(matrix, 30, 3, 11)
        render_alignment_pattern_row(matrix, 54, 1, 11, True)
    elif version == 12:
        render_alignment_pattern_row(matrix, 6, 2, 12)
        render_alignment_pattern_row(matrix, 32, 3, 12)
        render_alignment_pattern_row(matrix, 58, 1, 12, True)
    elif version == 13:
        render_alignment_pattern_row(matrix, 6, 2, 13)
        render_alignment_pattern_row(matrix, 34, 3, 13)
        render_alignment_pattern_row(matrix, 62, 1, 13, True)


