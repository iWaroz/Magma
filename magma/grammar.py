import magma.ast_header as S
import magma.tokenize as T

"""
Block -> Line|Line Block
CodeBlock -> Delta+ Block Delta-
Line -> Fun|For|While|If|Return|Ass|Expr|Repeat
Args -> (empty)|Id|Id,NonEmptyArgs
NonEmptyArgs -> Id|Id,NonEmptyArgs
For -> for Id in Expr CodeBlock
While -> while Expr CodeBlock
If -> if Expr CodeBlock|if Expr CodeBlock ElseIf
ElseIf -> elif Expr CodeBlock|elif Expr CodeBlock ElseIf|elif Expr CodeBlock else CodeBlock
Ass -> Id = Expr
ArrAss -> Id @ Expr = Expr
Repeat -> repeat Expr CodeBlock
Expr -> !Expr|Expr BinaryOp Expr|Id|[Args]|Int|Bool"""

class Stream:
    def __init__(self, tokenlist):
        self.tokens = tokenlist
        self.depth = 0

    def expect(self, tokentype, exact=False):
        assert self.peek(tokentype, exact)
        return self.consume()
    
    def consume(self):
        self.depth += 1
        return self.tokens.pop(0)
    
    def peek(self, tokentype, exact=False, lookahead=0):
        if not exact:
            val = (self.tokens[lookahead].strn().split(":")[0] == tokentype.strn().split(":")[0])
        else:
            val = (self.tokens[lookahead].strn() == tokentype.strn())
        return val
    
    @property
    def next(self):
        return self.tokens[0]

def GBlock(s):
    lines = []
    lines.append(GLine(s))
    while not (s.peek(T.EOF) or s.peek(T.IndentDelta)):
        lines.append(GLine(s))
    return S.CodeBlock(lines)

def GCodeBlock(s):
    s.expect(T.IndentDelta(1), exact=True)
    block = GBlock(s)
    s.expect(T.IndentDelta(-1), exact=True)
    return block

def GLine(s):
    if s.peek(T.For):
        return GFor(s)
    elif s.peek(T.While):
        return GWhile(s)
    elif s.peek(T.If):
        return GIf(s)
    elif s.peek(T.Repeat):
        return GRepeat(s)
    elif s.peek(T.Print):
        return GPrint(s)
    elif s.peek(T.Operator("="), lookahead=1, exact=True):
        return GAss(s)
    elif s.peek(T.Operator("@"), lookahead=1, exact=True):
        return GArrAss(s)
    elif maybe_expr(s):
        return GExpr(s)

def maybe_expr(s):
    return s.peek(T.Id) or s.peek(T.Operator("!"), exact=True) or s.peek(T.OpenBracket) or s.peek(T.Int) or s.peek(T.Bool) or s.peek(T.OpenParen)

def GFor(s):
    s.expect(T.For)
    varname = s.expect(T.Id)
    s.expect(T.In)
    expr = GExpr(s)
    cb = GCodeBlock(s)
    return S.For(varname.name, expr, cb)

def GWhile(s):
    s.expect(T.While)
    expr = GExpr(s)
    cb = GCodeBlock(s)
    return S.While(expr, cb)

def GIf(s):
    s.expect(T.If)
    expr = GExpr(s)
    cb = GCodeBlock(s)
    if s.peek(T.Elif):
        elseblock = GElseIf(s)
    elif s.peek(T.Else):
        s.consume()
        elseblock = GCodeBlock(s)
    else:
        elseblock = None
    return S.If(expr, cb, elseblock)

def GElseIf(s):
    if s.peek(T.Elif):
        s.consume()
        expr = GExpr(s)
        cb = GCodeBlock(s)
        if s.peek(T.Elif):
            elseblock = GElseIf(s)
        elif s.peek(T.Else):
            s.consume()
            elseblock = GCodeBlock(s)
        else:
            elseblock = None
        return S.If(expr, cb, elseblock)
    else:
        s.expect(T.Else)
        cb = GCodeBlock(s)
        return cb

def GPrint(s):
    s.expect(T.Print)
    return S.Print(GExpr(s))

def GAss(s):
    id_obj = s.expect(T.Id)
    s.expect(T.Operator("="), exact=True)
    expr = GExpr(s)
    return S.VarAssign(id_obj.name, expr)

def GArrAss(s):
    id_obj = s.expect(T.Id)
    s.expect(T.Operator("@"))
    ind = GExpr(s)
    s.expect(T.Operator("="), exact=True)
    expr = GExpr(s)
    return S.ArrAssign(id_obj.name, ind, expr)

def GRepeat(s):
    s.expect(T.Repeat)
    expr = GExpr(s)
    cb = GCodeBlock(s)
    return S.Repeat(expr, cb)

operator_priority = {
    "=": -42,
    "||": 1, "&": 1, ",": 1,
    "<": 2, ">": 2, "<=": 2, ">=": 2, "==": 2, "!=": 2, "..": 2, "@": 2,
    "+": 3, "-": 3,
    "*": 4, "/": 5, "%": 5,
    "!": 5, "**": 5
}

def GExpr(s, prio=0):
    expr = GExprPrefix(s)

    while True:
        if s.peek(T.Operator):
            optype = s.next.op
            if operator_priority[optype] < prio:
                break

            s.consume()
            right = GExpr(s, operator_priority[optype] + 1)
            expr = S.BinaryOperator(expr, optype, right)
        else:
            break
    
    return expr

def GExprPrefix(s):
    if s.peek(T.Operator("!"), exact=True):
        s.consume()
        expr = GExpr(s, operator_priority["!"])
        return S.Not(expr)
    elif s.peek(T.OpenBracket):
        s.consume()
        expr = GExpr(s)
        s.expect(T.CloseBracket)
        elems = []
        while isinstance(expr, S.BinaryOperator) and expr.op == ",":
            elems.append(expr.right)
            expr = expr.left
        elems.append(expr)
        return S.Array(elems[::-1])
    elif s.peek(T.Int):
        return S.IntLiteral(s.consume().num)
    elif s.peek(T.Id):
        return S.Var(s.consume().name)
    elif s.peek(T.Bool):
        return S.BoolLiteral(s.consume().val)
    elif s.peek(T.OpenParen):
        s.consume()
        expr = GExpr(s)
        s.expect(T.CloseParen)
        return expr

def parse_tokens(tokens):
    return GBlock(Stream(tokens))