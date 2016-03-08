def bytearray_to_int(buf, bit_width, bit_offset=0):
    BYTE_MASK = [0x00, 0x01, 0x03, 0x07, 0x0f, 0x1f, 0x3f, 0x7f, 0xff]
    base = bit_offset / 8
    last = (bit_offset + bit_width + 7) / 8

    offset = bit_offset % 8
    if last - base == 1:
        shift = 8 - (offset + bit_width)
        return (buf[base] >> shift) & BYTE_MASK[bit_width]

    value = 0
    remain = bit_width
    for byte in buf[base:last]:
        if remain == bit_width: # first byte
            take = 8 - offset
            value = byte & BYTE_MASK[take]
        else:
            take = min(8, remain)
            value = (value << take) + (byte >> (8 - take))
        remain -= take
    return value

def int_to_bytearray(bit_offset, value, bit_width):
    BYTE_MASK = [0x00, 0x01, 0x03, 0x07, 0x0f, 0x1f, 0x3f, 0x7f, 0xff]
    RBYTE_MASK = [0x00, 0x80, 0xc0, 0xe0, 0xf0, 0xf8, 0xfc, 0xfe, 0xff]
    ret_vals = []
    ret_mask = []

    # pad the value so it's byte aligned
    padding = (8 - ((bit_offset + bit_width) % 8)) % 8
    value <<= padding

    remain = bit_width + padding
    while remain > 0:
        if remain == bit_width + padding:
            ret_vals.append(value & 0xFF)
            ret_mask.append(BYTE_MASK[padding])
        else:
            ret_vals.append(value & 0xFF)
            ret_mask.append(0x00)
        value >>= 8
        remain -= 8

    ret_vals[-1] &= BYTE_MASK[8-bit_offset]
    ret_mask[-1] |= RBYTE_MASK[bit_offset]
    return ret_vals[::-1], ret_mask[::-1]

