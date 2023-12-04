def b_to_kb(b: int):
    return b / 1024


def b_to_mb(b: int):
    return b / 1024 / 1024


def b_to_gb(b: int):
    return b / 1024 / 1024 / 1024


def gb_to_b(gb: int):
    return gb * 1024 * 1024 * 1024


def mb_to_b(mb: int):
    return mb * 1024 * 1024


def kb_to_b(kb: int):
    return kb * 1024
