"""
AST HambaLang. Satu AST untuk semua dialek: parser yang menerjemahkan
sintaks v2 (``jika/akhir``), advanced (``set``, ``coba``, ``Rapat(n)``), dan
formal v5 (``Sita {}``, ``Proyek {}``) ke node yang sama.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union


@dataclass
class Node:
    line: int


# ---------------------------------------------------------------- expressions

@dataclass
class Literal(Node):
    value: Union[int, float, str, bool, None]


@dataclass
class Name(Node):
    name: str


@dataclass
class ListLit(Node):
    items: List["Expr"]


@dataclass
class DictLit(Node):
    pairs: List[Tuple["Expr", "Expr"]]


@dataclass
class Index(Node):
    obj: "Expr"
    index: "Expr"


@dataclass
class Attr(Node):
    obj: "Expr"
    name: str


@dataclass
class Call(Node):
    callee: "Expr"
    args: List["Expr"]


@dataclass
class Unary(Node):
    op: str  # '-', 'bukan'
    operand: "Expr"


@dataclass
class Binary(Node):
    op: str  # + - * / % ** == != < > <= >=
    left: "Expr"
    right: "Expr"


@dataclass
class Logical(Node):
    op: str  # 'dan' | 'atau' (short-circuit)
    left: "Expr"
    right: "Expr"


Expr = Union[Literal, Name, ListLit, DictLit, Index, Attr, Call, Unary, Binary, Logical]


# ----------------------------------------------------------------- statements

@dataclass
class Print(Node):
    expr: Expr


@dataclass
class Assign(Node):
    target: Expr  # Name | Index | Attr
    value: Expr
    op: Optional[str] = None  # untuk +=, -=, dst: '+', '-', ...


@dataclass
class ExprStmt(Node):
    expr: Expr


@dataclass
class If(Node):
    branches: List[Tuple[Expr, List["Stmt"]]]
    else_body: Optional[List["Stmt"]] = None


@dataclass
class While(Node):
    cond: Expr
    body: List["Stmt"]


@dataclass
class ForRange(Node):
    var: str
    start: Expr
    end: Expr  # inklusif
    step: Optional[Expr]
    body: List["Stmt"]


@dataclass
class ForEach(Node):
    var: str
    iterable: Expr
    body: List["Stmt"]


@dataclass
class Repeat(Node):
    """``Rapat(n) ... selesaiRapat``: ulangi body sebanyak n kali."""

    count: Expr
    body: List["Stmt"]


@dataclass
class FuncDef(Node):
    name: str
    params: List[str]
    body: List["Stmt"]
    # 'fungsi': scope fungsi (tulis = lokal). 'prosedur': scope blok (tulis tembus ke luar).
    kind: str = "fungsi"


@dataclass
class Return(Node):
    value: Optional[Expr]


@dataclass
class Break(Node):
    pass


@dataclass
class Continue(Node):
    pass


@dataclass
class Block(Node):
    """``mulai ... akhir``: blok dengan scope sendiri."""

    body: List["Stmt"]


@dataclass
class Seq(Node):
    """``Rapat ... Bubarkan``: deretan statement tanpa scope baru."""

    body: List["Stmt"]


@dataclass
class Try(Node):
    body: List["Stmt"]
    err_var: Optional[str]
    handler: List["Stmt"]


@dataclass
class Raise(Node):
    """``Mangkrak "pesan"`` (dialek v5): lempar ProyekMangkrak."""

    value: Optional[Expr]


@dataclass
class Input(Node):
    """``Tagih x``: baca input user ke variabel x."""

    name: str
    prompt: Optional[Expr] = None


@dataclass
class Global(Node):
    names: List[str]


@dataclass
class Halt(Node):
    """``selesai``: akhiri program (proyek selesai di atas kertas)."""


Stmt = Union[Print, Assign, ExprStmt, If, While, ForRange, ForEach, Repeat, FuncDef, Return,
             Break, Continue, Block, Seq, Try, Raise, Input, Global, Halt]


@dataclass
class Program(Node):
    body: List[Stmt] = field(default_factory=list)
