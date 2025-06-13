def MPD_fallout(data: float, low: float, high: float) -> float:
    """
    Snap a value to the nearest bound if within [low, high], or return the value unchanged if outside.

    If data is outside [low, high], return data.
    If data is within [low, high]:
        - Return low if data is less than the midpoint.
        - Return high otherwise.

    :param data: The value to process.
    :param low: The lower bound.
    :param high: The upper bound.
    :return: The processed value.
    """
    if data < low or data > high:
        return data
    return low if data < ((low + high) * 0.5) else high


def MPD_fltlim(data: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value to the range [min_val, max_val].

    :param data: The value to clamp.
    :param min_val: The minimum allowed value.
    :param max_val: The maximum allowed value.
    :return: The clamped value.
    """
    return max(min_val, min(data, max_val))


def MPD_fltmax2(x1: float, x2: float) -> float:
    """
    Return the maximum of two values.

    :param x1: First value.
    :param x2: Second value.
    :return: The greater of x1 and x2.
    """
    return max(x1, x2)
