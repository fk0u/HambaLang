"""Lexer & parser: precedence, dialek, dan pesan error."""
import pytest

from hambalang import InputBelumLengkap, SalahKetik, nodes as N, parse
from hambalang.lexer import tokenize


def expr_of(src: str):
    stmt = parse(f"x = {src}").body[0]
    assert isinstance(stmt, N.Assign)
    return stmt.value


def test_precedence_mul_over_add():
    e = expr_of("1 + 2 * 3")
    assert isinstance(e, N.Binary) and e.op == "+"
    assert isinstance(e.right, N.Binary) and e.right.op == "*"


def test_left_associative_subtraction():
    e = expr_of("10 - 2 - 3")
    assert e.op == "-" and isinstance(e.left, N.Binary) and e.left.op == "-"


def test_power_is_right_associative():
    e = expr_of("2 ** 3 ** 2")
    assert e.op == "**" and isinstance(e.right, N.Binary) and e.right.op == "**"


def test_negative_literal_folded():
    assert expr_of("-5").value == -5


def test_atau_is_both_else_and_logical_or():
    prog = parse("jika a atau b\n  lapor 1\natau\n  lapor 2\nakhir")
    stmt = prog.body[0]
    assert isinstance(stmt, N.If)
    assert isinstance(stmt.branches[0][0], N.Logical)
    assert stmt.else_body is not None


def test_atau_jika_two_words_is_elif():
    stmt = parse("jika a\n lapor 1\natau jika b\n lapor 2\nakhir").body[0]
    assert len(stmt.branches) == 2


def test_korupsi_adjacent_paren_is_call_spaced_is_print():
    call, printed = parse('Korupsi(10)\nKorupsi "halo"').body
    assert isinstance(call, N.ExprStmt) and isinstance(call.expr, N.Call)
    assert isinstance(printed, N.Print)


def test_rapat_loop_vs_program_block():
    loop, block = parse("Rapat(3)\n lapor 1\nselesaiRapat\nRapat\n lapor 2\nBubarkan").body
    assert isinstance(loop, N.Repeat)
    assert isinstance(block, N.Seq)


def test_inline_jika_maka():
    stmt = parse('jika x > 1 maka lapor "ok"').body[0]
    assert isinstance(stmt, N.If) and isinstance(stmt.branches[0][1][0], N.Print)


def test_multiline_list_and_dict():
    prog = parse('x = [\n 1,\n 2,\n]\ny = {\n a: 1,\n "b": 2\n}')
    assert len(prog.body) == 2


def test_string_escapes_and_comments():
    toks = tokenize('lapor "a\\tb\\n\\"c\\"" // komentar\n# juga komentar\n/* blok */')
    assert toks[1].value == 'a\tb\n"c"'


def test_url_in_string_is_not_comment():
    toks = tokenize('x = "https://contoh.id"')
    assert toks[2].value == "https://contoh.id"


def test_number_underscores_and_exponent():
    assert expr_of("1_000_000").value == 1_000_000
    assert expr_of("1.5e3").value == 1500.0


@pytest.mark.parametrize("src,msg", [
    ("x = (1 + 2", "belum ditutup"),
    ("akhir", "tanpa pasangan"),
    ("jika = 3", "Ekspresi tidak valid"),
    ("x = 1 +", "Ekspresi tidak valid"),
    ("lapor \"abc", "String tidak ditutup"),
    ("hentikan", "di luar loop"),
    ("fungsi f(a, a)\nakhir", "duplikat"),
    ("x = 1 2", "Token tidak terduga"),
    ("5 = x", "Sisi kiri"),
])
def test_syntax_errors(src, msg):
    with pytest.raises(SalahKetik) as exc:
        parse(src)
    assert msg in str(exc.value)


def test_break_inside_function_inside_loop_is_rejected():
    with pytest.raises(SalahKetik):
        parse("selama benar\n fungsi f()\n  hentikan\n akhir\nakhir")


def test_unclosed_block_is_incomplete_input():
    with pytest.raises(InputBelumLengkap) as exc:
        parse("jika benar\n  lapor 1\n")
    assert "baris 1" in str(exc.value)


def test_error_reports_line_number():
    with pytest.raises(SalahKetik) as exc:
        parse("lapor 1\nlapor 2\nx = = 3")
    assert exc.value.line == 3


@pytest.mark.parametrize("src,msg", [
    ('lapor "\\q"', "Escape tidak dikenal"),
    ("café = 1", "Karakter tidak dikenal"),
    ("fungsi Rapat()\nakhir", "nama khusus"),
    ("x = " + "9" * 5000, "terlalu panjang"),
])
def test_strict_lexing(src, msg):
    with pytest.raises(SalahKetik, match=msg):
        parse(src)


def test_leading_dot_number():
    assert expr_of(".5").value == 0.5
