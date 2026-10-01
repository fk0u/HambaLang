"""
Parser HambaLang: recursive descent untuk statement + precedence climbing
untuk ekspresi.

Satu parser menerima semua dialek yang pernah ada di repo ini:

=====================  =======================================================
Dialek                 Contoh
=====================  =======================================================
v2 (klasik)            ``x = 1``, ``jika .. ataujika .. atau .. akhir``,
                       ``selama``, ``untuk i dari 1 sampai 10``, ``fungsi f(a)``
advanced (v3)          ``set x = 1``, ``mulai .. akhir``, ``coba .. jikaGagal ..
                       akhirCoba``, ``Rapat(3) .. selesaiRapat``, ``prosedur``
formal (v5)            ``Rapat .. Bubarkan``, ``Anggaran x = 1``, ``Sita c { }
                       Pengadilan { }``, ``Proyek c { }``, ``Tagih x``,
                       ``BagiRata f(a) { }``, ``Janji f(x)``, ``Wacana "..."``
=====================  =======================================================

Dua kata kunci punya arti ganda dan dibedakan dari token sesudahnya:

* ``Korupsi(20)`` (kurung menempel) memanggil builtin korupsi anggaran,
  sedangkan ``Korupsi "teks"`` / ``Korupsi x`` adalah print gaya v5.
* ``Rapat(3)`` adalah loop, ``Rapat`` sendirian di satu baris membuka blok
  program v5 yang ditutup ``Bubarkan``.
"""
from typing import Callable, List, Optional, Set

from hambalang import nodes as N
from hambalang.errors import InputBelumLengkap, SalahKetik
from hambalang.lexer import EOF, KEYWORDS, NAME, NEWLINE, NUMBER, OP, STRING, Token, tokenize

COMPARISON_OPS = {"==", "!=", "<", ">", "<=", ">="}
COMPOUND_OPS = {"+=": "+", "-=": "-", "*=": "*", "/=": "/", "%=": "%"}

# Nama blok untuk pesan error "belum ditutup".
CLOSERS = {
    "jika": "akhir", "selama": "akhir", "untuk": "akhir", "fungsi": "akhir", "mulai": "akhir",
    "coba": "akhirCoba", "prosedur": "akhirProsedur", "Rapat": "selesaiRapat",
}


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.loop_depth = 0  # untuk validasi hentikan/lanjut

    # ------------------------------------------------------------ helpers
    @property
    def tok(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset: int = 1) -> Token:
        i = min(self.pos + offset, len(self.tokens) - 1)
        return self.tokens[i]

    def advance(self) -> Token:
        t = self.tokens[self.pos]
        if t.type != EOF:
            self.pos += 1
        return t

    def error(self, msg: str, tok: Optional[Token] = None) -> SalahKetik:
        t = tok or self.tok
        if t.type == EOF:
            return InputBelumLengkap(msg, t.line, t.col)
        return SalahKetik(msg, t.line, t.col)

    def describe(self, t: Token) -> str:
        if t.type == EOF:
            return "akhir file"
        if t.type == NEWLINE:
            return "akhir baris"
        if t.type == STRING:
            return f'"{t.value}"'
        return repr(t.value)

    def expect_op(self, value: str) -> Token:
        if not self.tok.is_op(value):
            raise self.error(f"Diharapkan '{value}', ditemukan {self.describe(self.tok)}")
        return self.advance()

    def expect_name(self, value: str) -> Token:
        if not self.tok.is_name(value):
            raise self.error(f"Diharapkan '{value}', ditemukan {self.describe(self.tok)}")
        return self.advance()

    def expect_ident(self, what: str = "nama") -> str:
        t = self.tok
        if t.type != NAME:
            raise self.error(f"Diharapkan {what}, ditemukan {self.describe(t)}")
        if t.value in KEYWORDS:
            raise self.error(f"'{t.value}' adalah kata kunci, tidak bisa dipakai sebagai {what}")
        self.advance()
        return t.value

    def skip_newlines(self):
        while self.tok.type == NEWLINE:
            self.advance()

    def end_statement(self):
        if self.tok.type in (NEWLINE, EOF) or self.tok.is_op("}"):
            if self.tok.type == NEWLINE:
                self.advance()
            return
        raise self.error(f"Token tidak terduga {self.describe(self.tok)} setelah statement")

    def at_line_end(self) -> bool:
        return self.tok.type in (NEWLINE, EOF) or self.tok.is_op("}")

    def adjacent_paren(self) -> bool:
        """``Nama(`` tanpa spasi: dipakai untuk membedakan Korupsi(20) vs Korupsi "x"."""
        nxt = self.peek()
        return nxt.is_op("(") and not nxt.spaced

    # ------------------------------------------------------------ program
    def parse_program(self) -> N.Program:
        body = self.parse_block(set(), opener=None)
        if self.tok.type != EOF:
            raise self.error(f"'{self.tok.value}' tanpa pasangan blok pembuka")
        return N.Program(line=1, body=body)

    def loop_body(self, parse: Callable[[], List[N.Node]]) -> List[N.Node]:
        self.loop_depth += 1
        try:
            return parse()
        finally:
            self.loop_depth -= 1

    def function_body(self, parse: Callable[[], List[N.Node]]) -> List[N.Node]:
        saved, self.loop_depth = self.loop_depth, 0
        try:
            return parse()
        finally:
            self.loop_depth = saved

    def parse_block(self, terminators: Set[str], opener: Optional[Token], brace: bool = False) -> List[N.Node]:
        """Parse statement sampai ketemu salah satu ``terminators`` (tidak dikonsumsi)."""
        body: List[N.Node] = []
        while True:
            self.skip_newlines()
            t = self.tok
            if t.type == EOF:
                if opener is None:
                    return body
                closer = "}" if brace else "/".join(sorted(terminators))
                raise InputBelumLengkap(
                    f"Blok '{opener.value}' (baris {opener.line}) belum ditutup dengan '{closer}'",
                    t.line, t.col)
            if brace and t.is_op("}"):
                return body
            if t.type == NAME and t.value in terminators:
                return body
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)

    def parse_brace_block(self, opener: Token) -> List[N.Node]:
        self.skip_newlines()
        self.expect_op("{")
        body = self.parse_block(set(), opener=opener, brace=True)
        self.expect_op("}")
        return body

    # ------------------------------------------------------------ statements
    def parse_statement(self) -> Optional[N.Node]:
        t = self.tok
        if t.type == NAME:
            handler = self.STATEMENTS.get(t.value)
            if handler is not None:
                return handler(self)
            if t.value in ("atau", "ataujika", "akhir", "jikaGagal", "akhirCoba", "akhirProsedur",
                           "selesaiRapat", "Bubarkan", "Pengadilan"):
                raise self.error(f"'{t.value}' tanpa pasangan blok pembuka")
        return self.parse_simple_statement()

    def parse_simple_statement(self) -> N.Node:
        """Assignment atau expression statement."""
        start = self.tok
        expr = self.parse_expression()
        if self.tok.is_op("=") or (self.tok.type == OP and self.tok.value in COMPOUND_OPS):
            op_tok = self.advance()
            self.check_target(expr, start)
            value = self.parse_expression()
            self.end_statement()
            return N.Assign(line=start.line, target=expr, value=value,
                            op=COMPOUND_OPS.get(op_tok.value))
        self.end_statement()
        return N.ExprStmt(line=start.line, expr=expr)

    def check_target(self, expr: N.Node, tok: Token):
        if not isinstance(expr, (N.Name, N.Index, N.Attr)):
            raise self.error("Sisi kiri '=' harus variabel, elemen daftar, atau properti objek", tok)

    def parse_assign_after_keyword(self) -> N.Node:
        """``set x = ..`` dan ``Anggaran x = ..``."""
        kw = self.advance()
        start = self.tok
        target = self.parse_postfix(self.parse_primary())
        self.check_target(target, start)
        if self.tok.is_op("="):
            self.advance()
            op = None
        elif self.tok.type == OP and self.tok.value in COMPOUND_OPS:
            op = COMPOUND_OPS[self.advance().value]
        else:
            raise self.error(f"Diharapkan '=' setelah '{kw.value} {start.value}'")
        value = self.parse_expression()
        self.end_statement()
        return N.Assign(line=kw.line, target=target, value=value, op=op)

    def parse_print(self) -> N.Node:
        kw = self.advance()
        if self.at_line_end():
            expr: N.Node = N.Literal(line=kw.line, value="")
        else:
            expr = self.parse_expression()
        self.end_statement()
        return N.Print(line=kw.line, expr=expr)

    def parse_korupsi(self) -> N.Node:
        # Korupsi(20) -> builtin; Korupsi "teks" -> print (dialek v5)
        if self.adjacent_paren():
            return self.parse_simple_statement()
        return self.parse_print()

    def parse_mangkrak(self) -> N.Node:
        if self.adjacent_paren():
            return self.parse_simple_statement()
        kw = self.advance()
        value = None if self.at_line_end() else self.parse_expression()
        self.end_statement()
        return N.Raise(line=kw.line, value=value)

    def parse_wacana(self) -> Optional[N.Node]:
        # Wacana = komentar resmi. Diparse (harus valid) lalu dibuang.
        self.advance()
        if not self.at_line_end():
            self.parse_expression()
        self.end_statement()
        return None

    def parse_rapat(self) -> N.Node:
        kw = self.tok
        if self.adjacent_paren():
            self.advance()
            self.expect_op("(")
            count = self.parse_expression()
            self.expect_op(")")
            self.end_statement()
            body = self.loop_body(lambda: self.parse_block({"selesaiRapat", "akhir"}, kw))
            self.advance()
            self.end_statement()
            return N.Repeat(line=kw.line, count=count, body=body)
        # Blok program formal: Rapat ... Bubarkan
        self.advance()
        self.end_statement()
        body = self.parse_block({"Bubarkan"}, kw)
        self.advance()
        self.end_statement()
        return N.Seq(line=kw.line, body=body)

    def parse_if(self) -> N.Node:
        kw = self.advance()
        cond = self.parse_expression()
        if self.tok.is_name("maka"):
            self.advance()
            if not self.at_line_end():
                # Inline: jika c maka lapor "x"
                stmt = self.parse_statement()
                return N.If(line=kw.line, branches=[(cond, [stmt] if stmt else [])])
        self.end_statement()
        branches = [(cond, self.parse_block({"ataujika", "atau", "akhir"}, kw))]
        else_body = None
        while True:
            t = self.tok
            if t.is_name("ataujika") or (t.is_name("atau") and self.peek().is_name("jika")):
                self.advance()
                if t.value == "atau":
                    self.advance()
                c = self.parse_expression()
                if self.tok.is_name("maka"):
                    self.advance()
                self.end_statement()
                branches.append((c, self.parse_block({"ataujika", "atau", "akhir"}, kw)))
            elif t.is_name("atau"):
                self.advance()
                self.end_statement()
                else_body = self.parse_block({"akhir"}, kw)
            else:
                self.expect_name("akhir")
                self.end_statement()
                return N.If(line=kw.line, branches=branches, else_body=else_body)

    def parse_sita(self) -> N.Node:
        kw = self.advance()
        branches = [(self.parse_expression(), self.parse_brace_block(kw))]
        else_body = None
        while True:
            # Pengadilan boleh di baris yang sama dengan '}' atau baris berikutnya.
            save = self.pos
            self.skip_newlines()
            if not self.tok.is_name("Pengadilan"):
                self.pos = save
                break
            self.advance()
            if self.tok.is_name("Sita"):
                self.advance()
                branches.append((self.parse_expression(), self.parse_brace_block(kw)))
                continue
            else_body = self.parse_brace_block(kw)
            break
        self.end_statement()
        return N.If(line=kw.line, branches=branches, else_body=else_body)

    def parse_while(self) -> N.Node:
        kw = self.advance()
        cond = self.parse_expression()
        self.end_statement()
        body = self.loop_body(lambda: self.parse_block({"akhir"}, kw))
        self.advance()
        self.end_statement()
        return N.While(line=kw.line, cond=cond, body=body)

    def parse_proyek(self) -> N.Node:
        kw = self.advance()
        cond = self.parse_expression()
        body = self.loop_body(lambda: self.parse_brace_block(kw))
        self.end_statement()
        return N.While(line=kw.line, cond=cond, body=body)

    def parse_for(self) -> N.Node:
        kw = self.advance()
        var = self.expect_ident("nama variabel loop")
        if self.tok.is_name("dalam"):
            self.advance()
            iterable = self.parse_expression()
            self.end_statement()
            body = self.loop_body(lambda: self.parse_block({"akhir"}, kw))
            self.advance()
            self.end_statement()
            return N.ForEach(line=kw.line, var=var, iterable=iterable, body=body)
        self.expect_name("dari")
        start = self.parse_expression()
        self.expect_name("sampai")
        end = self.parse_expression()
        step = None
        if self.tok.is_name("langkah"):
            self.advance()
            step = self.parse_expression()
        self.end_statement()
        body = self.loop_body(lambda: self.parse_block({"akhir"}, kw))
        self.advance()
        self.end_statement()
        return N.ForRange(line=kw.line, var=var, start=start, end=end, step=step, body=body)

    def parse_params(self) -> List[str]:
        self.expect_op("(")
        params: List[str] = []
        while not self.tok.is_op(")"):
            name = self.expect_ident("nama parameter")
            if name in params:
                raise self.error(f"Parameter '{name}' duplikat")
            params.append(name)
            if not self.tok.is_op(")"):
                self.expect_op(",")
        self.advance()
        return params

    def parse_fungsi(self) -> N.Node:
        kw = self.advance()
        name = self.expect_ident("nama fungsi")
        params = self.parse_params()
        self.end_statement()
        body = self.function_body(lambda: self.parse_block({"akhir"}, kw))
        self.advance()
        self.end_statement()
        return N.FuncDef(line=kw.line, name=name, params=params, body=body, kind="fungsi")

    def parse_bagirata(self) -> N.Node:
        kw = self.advance()
        name = self.expect_ident("nama fungsi")
        params = self.parse_params()
        body = self.function_body(lambda: self.parse_brace_block(kw))
        self.end_statement()
        return N.FuncDef(line=kw.line, name=name, params=params, body=body, kind="fungsi")

    def parse_prosedur(self) -> N.Node:
        kw = self.advance()
        name = self.expect_ident("nama prosedur")
        params = self.parse_params() if self.tok.is_op("(") else []
        self.end_statement()
        body = self.function_body(lambda: self.parse_block({"akhirProsedur", "akhir"}, kw))
        self.advance()
        self.end_statement()
        return N.FuncDef(line=kw.line, name=name, params=params, body=body, kind="prosedur")

    def parse_return(self) -> N.Node:
        kw = self.advance()
        value = None if self.at_line_end() else self.parse_expression()
        self.end_statement()
        return N.Return(line=kw.line, value=value)

    def parse_break(self) -> N.Node:
        if self.loop_depth == 0:
            raise self.error("'hentikan' di luar loop")
        kw = self.advance()
        self.end_statement()
        return N.Break(line=kw.line)

    def parse_continue(self) -> N.Node:
        if self.loop_depth == 0:
            raise self.error("'lanjut' di luar loop")
        kw = self.advance()
        self.end_statement()
        return N.Continue(line=kw.line)

    def parse_mulai(self) -> N.Node:
        kw = self.advance()
        self.end_statement()
        body = self.parse_block({"akhir"}, kw)
        self.advance()
        self.end_statement()
        return N.Block(line=kw.line, body=body)

    def parse_coba(self) -> N.Node:
        kw = self.advance()
        self.end_statement()
        body = self.parse_block({"jikaGagal"}, kw)
        self.advance()
        err_var = None
        if self.tok.type == NAME and not self.at_line_end():
            err_var = self.expect_ident("nama variabel error")
        self.end_statement()
        handler = self.parse_block({"akhirCoba", "akhir"}, kw)
        self.advance()
        self.end_statement()
        return N.Try(line=kw.line, body=body, err_var=err_var, handler=handler)

    def parse_tagih(self) -> N.Node:
        kw = self.advance()
        name = self.expect_ident("nama variabel")
        prompt = None
        if self.tok.is_op(","):
            self.advance()
            prompt = self.parse_expression()
        self.end_statement()
        return N.Input(line=kw.line, name=name, prompt=prompt)

    def parse_global(self) -> N.Node:
        kw = self.advance()
        names = [self.expect_ident()]
        while self.tok.is_op(","):
            self.advance()
            names.append(self.expect_ident())
        self.end_statement()
        return N.Global(line=kw.line, names=names)

    def parse_janji_stmt(self) -> N.Node:
        return self.parse_simple_statement()

    def parse_selesai(self) -> N.Node:
        if self.adjacent_paren():
            return self.parse_simple_statement()
        kw = self.advance()
        self.end_statement()
        return N.Halt(line=kw.line)

    STATEMENTS = {
        "lapor": parse_print, "print": parse_print, "Korupsi": parse_korupsi,
        "Mangkrak": parse_mangkrak, "Wacana": parse_wacana, "Rapat": parse_rapat,
        "set": parse_assign_after_keyword, "Anggaran": parse_assign_after_keyword,
        "jika": parse_if, "Sita": parse_sita, "selama": parse_while, "Proyek": parse_proyek,
        "untuk": parse_for, "fungsi": parse_fungsi, "BagiRata": parse_bagirata,
        "prosedur": parse_prosedur, "kembalikan": parse_return, "hentikan": parse_break,
        "lanjut": parse_continue, "mulai": parse_mulai, "coba": parse_coba, "Tagih": parse_tagih,
        "global": parse_global, "Janji": parse_janji_stmt, "selesai": parse_selesai,
    }

    # ------------------------------------------------------------ expressions
    def parse_expression(self) -> N.Node:
        return self.parse_or()

    def parse_or(self) -> N.Node:
        left = self.parse_and()
        while self.tok.is_name("atau", "ATAU"):
            t = self.advance()
            left = N.Logical(line=t.line, op="atau", left=left, right=self.parse_and())
        return left

    def parse_and(self) -> N.Node:
        left = self.parse_not()
        while self.tok.is_name("dan", "DAN"):
            t = self.advance()
            left = N.Logical(line=t.line, op="dan", left=left, right=self.parse_not())
        return left

    def parse_not(self) -> N.Node:
        if self.tok.is_name("bukan", "BUKAN"):
            t = self.advance()
            return N.Unary(line=t.line, op="bukan", operand=self.parse_not())
        return self.parse_comparison()

    def parse_comparison(self) -> N.Node:
        left = self.parse_additive()
        while self.tok.type == OP and self.tok.value in COMPARISON_OPS:
            t = self.advance()
            left = N.Binary(line=t.line, op=t.value, left=left, right=self.parse_additive())
        return left

    def _binary_level(self, ops: Set[str], next_level: Callable[[], N.Node]) -> N.Node:
        left = next_level()
        while self.tok.type == OP and self.tok.value in ops:
            t = self.advance()
            left = N.Binary(line=t.line, op=t.value, left=left, right=next_level())
        return left

    def parse_additive(self) -> N.Node:
        return self._binary_level({"+", "-"}, self.parse_multiplicative)

    def parse_multiplicative(self) -> N.Node:
        return self._binary_level({"*", "/", "%"}, self.parse_unary)

    def parse_unary(self) -> N.Node:
        t = self.tok
        if t.is_op("-"):
            self.advance()
            operand = self.parse_unary()
            if isinstance(operand, N.Literal) and type(operand.value) in (int, float):
                return N.Literal(line=t.line, value=-operand.value)
            return N.Unary(line=t.line, op="-", operand=operand)
        if t.is_op("+"):
            self.advance()
            return self.parse_unary()
        if t.is_op("!"):
            self.advance()
            return N.Unary(line=t.line, op="bukan", operand=self.parse_unary())
        return self.parse_power()

    def parse_power(self) -> N.Node:
        base = self.parse_postfix(self.parse_primary())
        if self.tok.is_op("**"):
            t = self.advance()
            # Asosiatif kanan, dan eksponen boleh negatif: 2 ** -1
            return N.Binary(line=t.line, op="**", left=base, right=self.parse_unary())
        return base

    def parse_postfix(self, expr: N.Node) -> N.Node:
        while True:
            t = self.tok
            if t.is_op("("):
                self.advance()
                args = self.parse_items(")")
                expr = N.Call(line=t.line, callee=expr, args=args)
            elif t.is_op("["):
                self.advance()
                index = self.parse_expression()
                self.expect_op("]")
                expr = N.Index(line=t.line, obj=expr, index=index)
            elif t.is_op(".") and self.peek().type == NAME:
                self.advance()
                expr = N.Attr(line=t.line, obj=expr, name=self.advance().value)
            else:
                return expr

    def parse_items(self, closer: str) -> List[N.Node]:
        items: List[N.Node] = []
        self.skip_newlines()
        while not self.tok.is_op(closer):
            items.append(self.parse_expression())
            self.skip_newlines()
            if not self.tok.is_op(closer):
                self.expect_op(",")
                self.skip_newlines()
        self.advance()
        return items

    def parse_primary(self) -> N.Node:
        t = self.tok
        if t.type == NUMBER or t.type == STRING:
            self.advance()
            return N.Literal(line=t.line, value=t.value)
        if t.type == NAME:
            if t.value in ("benar", "BENAR"):
                self.advance()
                return N.Literal(line=t.line, value=True)
            if t.value in ("salah", "SALAH"):
                self.advance()
                return N.Literal(line=t.line, value=False)
            if t.value in ("kosong", "KOSONG"):
                self.advance()
                return N.Literal(line=t.line, value=None)
            if t.value == "Janji":
                # Janji f(x): panggilan fungsi gaya v5. 'Janji' hanya hiasan.
                self.advance()
                callee = N.Name(line=t.line, name=self.expect_ident("nama fungsi"))
                if not self.tok.is_op("("):
                    raise self.error("Diharapkan '(' setelah 'Janji nama'")
                return callee
            if t.value in ("bukan", "BUKAN"):
                raise self.error(f"'{t.value}' di posisi ini harus diberi kurung, mis. ({t.value} x)")
            if t.value in KEYWORDS:
                raise self.error(f"Kata kunci '{t.value}' tidak bisa dipakai di dalam ekspresi")
            self.advance()
            return N.Name(line=t.line, name=t.value)
        if t.is_op("("):
            self.advance()
            expr = self.parse_expression()
            self.expect_op(")")
            return expr
        if t.is_op("["):
            self.advance()
            return N.ListLit(line=t.line, items=self.parse_items("]"))
        if t.is_op("{"):
            return self.parse_dict()
        raise self.error(f"Ekspresi tidak valid: {self.describe(t)}")

    def parse_dict(self) -> N.Node:
        t = self.advance()
        pairs = []
        self.skip_newlines()
        while not self.tok.is_op("}"):
            k = self.tok
            # Kunci tanpa kutip ala JS: {nama: "x"}
            if k.type == NAME and self.peek().is_op(":"):
                self.advance()
                key: N.Node = N.Literal(line=k.line, value=k.value)
            else:
                key = self.parse_expression()
            self.expect_op(":")
            self.skip_newlines()
            pairs.append((key, self.parse_expression()))
            self.skip_newlines()
            if not self.tok.is_op("}"):
                self.expect_op(",")
                self.skip_newlines()
        self.advance()
        return N.DictLit(line=t.line, pairs=pairs)


def parse(source: str) -> N.Program:
    return Parser(tokenize(source)).parse_program()
