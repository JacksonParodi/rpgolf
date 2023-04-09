def clamp_to_int(input, min_value, max_value):
    input = int(max(min_value, min(input, max_value)))
    return input