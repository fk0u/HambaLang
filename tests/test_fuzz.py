"""
Fuzz differential test: program acak (deterministik per seed) harus
menghasilkan output dan error yang sama persis di interpreter dan HambaVM.
"""
import random

import pytest

from hambalang import HambaError, run_source

VARS = ["a", "b", "c", "xs", "obj"]
LITERALS = ["0", "1", "2", "-3", "7", "2.5", '"t"', '""', "benar", "salah", "kosong", "[1, 2]", "{k: 1}"]
INDEXABLE = ["xs", "obj", "[5, 6, 7]", '"abc"']
ITERABLES = ["xs", "[1, 2, 3]", "obj", '"ab"']
BINOPS = ["+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", "dan", "atau", "**"]


def gen_num(rng: random.Random, depth: int = 0) -> str:
    """Ekspresi yang (hampir) selalu bertipe angka, supaya program berjalan jauh."""
    roll = rng.random()
    if depth > 3 or roll < 0.35:
        return rng.choice(["0", "1", "2", "-3", "7", "2.5", "a", "b", "panjang(xs)", "i0", "jumlah([1, 2])"])
    if roll < 0.75:
        return f"({gen_num(rng, depth + 1)} {rng.choice(['+', '-', '*'])} {gen_num(rng, depth + 1)})"
    if roll < 0.85:
        return f"({gen_num(rng, depth + 1)} % {rng.choice(['2', '3', '7'])})"
    if roll < 0.92:
        return f"xs[{rng.choice(['0', '-1', '1'])}]"
    return f"-{gen_num(rng, depth + 1)}"


def gen_cond(rng: random.Random) -> str:
    if rng.random() < 0.8:
        return f"{gen_num(rng)} {rng.choice(['==', '!=', '<', '>', '<=', '>='])} {gen_num(rng)}"
    return gen_expr(rng)


def gen_expr(rng: random.Random, depth: int = 0) -> str:
    if depth == 0 and rng.random() < 0.6:
        return gen_num(rng)
    roll = rng.random()
    if depth > 3 or roll < 0.3:
        return rng.choice(LITERALS + VARS)
    if roll < 0.55:
        return f"({gen_expr(rng, depth + 1)} {rng.choice(BINOPS)} {gen_expr(rng, depth + 1)})"
    if roll < 0.65:
        op = rng.choice(["-", "!", "bukan "])
        inner = f"{op}{gen_expr(rng, depth + 1)}"
        return f"({inner})" if op == "bukan " else inner
    if roll < 0.75:
        target = rng.choice(INDEXABLE)
        return f"{target}[{gen_expr(rng, depth + 1)}]"
    if roll < 0.85:
        fn = rng.choice(["panjang", "teks", "tipe", "f", "g", "mutlak", "angka", "boolean"])
        return f"{fn}({gen_expr(rng, depth + 1)})"
    if roll < 0.92:
        return f"[{gen_expr(rng, depth + 1)}, {gen_expr(rng, depth + 1)}]"
    return f"{{k: {gen_expr(rng, depth + 1)}}}"


def gen_block(rng: random.Random, depth: int, in_loop: bool, indent: str) -> list:
    lines = []
    for _ in range(rng.randint(1, 4)):
        roll = rng.random()
        e = gen_expr(rng)
        if roll < 0.25 or depth > 2:
            lines.append(f"{indent}lapor {e}")
        elif roll < 0.4:
            if rng.random() < 0.7:
                lines.append(f"{indent}{rng.choice(['a', 'b'])} {rng.choice(['=', '+=', '-='])} {gen_num(rng)}")
            else:
                lines.append(f"{indent}{rng.choice(['a', 'b', 'c'])} {rng.choice(['=', '+=', '*='])} {e}")
        elif roll < 0.5:
            lines.append(f"{indent}jika {gen_cond(rng)}")
            lines += gen_block(rng, depth + 1, in_loop, indent + "  ")
            if rng.random() < 0.5:
                lines.append(f"{indent}atau")
                lines += gen_block(rng, depth + 1, in_loop, indent + "  ")
            lines.append(f"{indent}akhir")
        elif roll < 0.6:
            lines.append(f"{indent}untuk i{depth} dari 0 sampai {rng.randint(0, 3)}")
            lines += gen_block(rng, depth + 1, True, indent + "  ")
            lines.append(f"{indent}akhir")
        elif roll < 0.68:
            iterable = rng.choice(ITERABLES)
            lines.append(f"{indent}untuk el{depth} dalam {iterable}")
            lines += gen_block(rng, depth + 1, True, indent + "  ")
            lines.append(f"{indent}akhir")
        elif roll < 0.76:
            lines.append(f"{indent}coba")
            lines += gen_block(rng, depth + 1, in_loop, indent + "  ")
            lines.append(f"{indent}jikaGagal err{depth}")
            lines.append(f"{indent}  lapor \"E:\" + err{depth}")
            lines.append(f"{indent}akhirCoba")
        elif roll < 0.82:
            lines.append(f"{indent}mulai")
            lines += gen_block(rng, depth + 1, in_loop, indent + "  ")
            lines.append(f"{indent}akhir")
        elif roll < 0.88 and in_loop:
            lines.append(f"{indent}jika {gen_cond(rng)}")
            lines.append(f"{indent}  {rng.choice(['hentikan', 'lanjut'])}")
            lines.append(f"{indent}akhir")
        elif roll < 0.93:
            lines.append(f"{indent}tambahArray(xs, {e})")
        else:
            lines.append(f"{indent}obj[\"k\"] = {e}")
    return lines


PRELUDE = """i0 = 0
a = 1
b = 2
c = "c"
xs = [1, 2, 3]
obj = {k: 0}
fungsi f(x)
  jika x == kosong
    kembalikan 0
  akhir
  kembalikan [x, a]
akhir
fungsi g(x)
  a = x
  kembalikan teks(x) + "!"
akhir
"""


def outcome(src: str, engine: str):
    lines = []
    try:
        run_source(src, engine=engine, seed=1, step_limit=5000, output=lines.append)
        return lines, None
    except HambaError as e:
        return lines, (type(e).__name__, e.message, e.line)


@pytest.mark.parametrize("seed", range(400))
def test_random_programs_agree(seed):
    rng = random.Random(seed)
    src = PRELUDE + "\n".join(gen_block(rng, 0, False, "")) + "\nlapor [a, b, c, xs, obj]\n"
    interp = outcome(src, "interpreter")
    vm = outcome(src, "vm")
    assert interp == vm, src
