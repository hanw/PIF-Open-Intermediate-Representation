
def ipv4(ipv4_header):
    ipv4_header.set_value("chksum", 0)

    shift = False
    tot = 0
    tmp = 0
    for b in ipv4_header.serialize():
        if shift:
            tmp = (tmp << 8) + b
            tot += tmp
            shift = False
        else:
            tmp = b
            shift = True

    while (tot > 0xFFFF):
        rhs = tot & 0x000FFFF
        lhs = tot >> 16
        tot = lhs + rhs

    ipv4_header.set_value("chksum", ~tot)
