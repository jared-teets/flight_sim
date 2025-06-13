
def MPD_fallout(data, low, high):
    if data < low or data > high:
        return data
    if data < ((low + high) * 0.5):
        return low
    return high

def MPD_fltlim(data, min_val, max_val):
    if data < min_val:
        return min_val
    if data > max_val:
        return max_val
    return data

def MPD_fltmax2(x1, x2):
    return x1 if x1 > x2 else x2

