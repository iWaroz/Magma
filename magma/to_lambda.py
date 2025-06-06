import magma.ast_header as ast 
import lambdac.stdlib as std

def flatten_commas(expr):
    if isinstance(expr, ast.BinaryOperator) and expr.op == ",":
        return flatten_commas(expr.left) + flatten_commas(expr.right)
    return [expr]

def compose(funcs):
    # Converts [f, g, h, x] into f (g (h x))
    if len(funcs) == 1:
        return funcs[0]
    return f"{funcs[0]} ({compose(funcs[1:])})"

class NotSupported(Exception):
    pass

def compile_expr(expr: ast.Expression, varhash: dict):
    if isinstance(expr, ast.BinaryOperator):
        op = expr.op
        left = compile_expr(expr.left, varhash)
        right = compile_expr(expr.right, varhash)
        if op == "+": return f"({std.numbers.add} {left} {right})"
        elif op == "*": return f"({std.numbers.mult} {left} {right})"
        elif op == "**": return f"({right} {left})"
        elif op == "-": return f"({std.numbers.sub} {left} {right})"
        elif op == "/": return f"({std.numbers.div} {left} {right})"
        elif op == "%": return f"({std.numbers.mod} {left} {right})"
        elif op == "<": return f"({std.numbers.le} {left} {right})"
        elif op == ">": return f"({std.numbers.ge} {left} {right})"
        elif op == "<=": return f"({std.numbers.leq} {left} {right})"
        elif op == ">=": return f"({std.numbers.geq} {left} {right})"
        elif op == "==": return f"({std.numbers.eq} {left} {right})"
        elif op == "!=": return f"({std.bools.notgate} ({std.numbers.eq} {left} {right}))"
        elif op == "||": return f"({std.bools.orgate} {left} {right})"
        elif op == "&": return f"({std.bools.andgate} {left} {right})"
        elif op == "..": return f"({std.array.range} {left} {right})"
        elif op == "@": return f"({std.array.getter} {left} {right})"
    elif isinstance(expr, ast.BoolLiteral):
        if expr.value == "true": return std.true
        return std.false
    elif isinstance(expr, ast.IntLiteral):
        return std.numbers.make(expr.value)
    elif isinstance(expr, ast.Not):
        return f"({std.bools.notgate} {compile_expr(expr.expr, varhash)})"
    elif isinstance(expr, ast.Var):
        return f"({std.state.get_variable} {std.numbers.make(varhash[expr.name])})"
    elif isinstance(expr, ast.Array):
        return std.array.make([compile_expr(i, varhash) for i in expr.inner])

def compile_tree(tree: ast.SToken, varhash: dict):
    if isinstance(tree, ast.CodeBlock):
        chunks = [compile_tree(t, varhash) for t in tree.lines]
        if len(chunks) == 1:
            return chunks[0]
        return "λst." + compose(chunks[::-1] + ["st"])
    elif isinstance(tree, ast.For):
        expr = compile_expr(tree.iterator, varhash)
        body = compile_tree(tree.block, varhash)
        return std.state.for_loop(varhash[tree.var], expr, body)
    elif isinstance(tree, ast.If):
        expr = compile_expr(tree.cond, varhash)
        trueblock = compile_tree(tree.block, varhash)
        falseblock = compile_tree(tree.elseblock, varhash) if tree.elseblock is not None else ""
        return std.state.if_statement(expr, trueblock, falseblock)
    elif isinstance(tree, ast.Print):
        expr = compile_expr(tree.expr, varhash)
        return std.state.printer(expr)
    elif isinstance(tree, ast.Repeat):
        expr = compile_expr(tree.counter, varhash)
        body = compile_tree(tree.block, varhash)
        return std.state.repeater(expr, body)
    elif isinstance(tree, ast.VarAssign):
        varid = varhash[tree.varname]
        value = compile_expr(tree.expr, varhash)
        return std.state.variable_setter(varid, value)
    elif isinstance(tree, ast.ArrAssign):
        varid = varhash[tree.varname]
        ind = compile_expr(tree.ind, varhash)
        value = compile_expr(tree.expr, varhash)
        return std.state.array_setter(varid, ind, value)
    elif isinstance(tree, ast.While):
        expr = compile_expr(tree.cond, varhash)
        body = compile_tree(tree.block, varhash)
        return std.state.while_loop(expr, body)

def incr_tbl(id, tbl):
    tbl[id] = tbl.get(id, 0) + 1
 
def count_vars(tree, tbl):
    if isinstance(tree, ast.Var):
        incr_tbl(tree.name, tbl)
    if isinstance(tree, ast.VarAssign):
        incr_tbl(tree.varname, tbl)
        count_vars(tree.expr, tbl)
    if isinstance(tree, ast.ArrAssign):
        incr_tbl(tree.varname, tbl)
        count_vars(tree.ind, tbl)
        count_vars(tree.expr, tbl)
    if isinstance(tree, ast.For):
        incr_tbl(tree.var, tbl)
        count_vars(tree.iterator, tbl)
        count_vars(tree.block, tbl)
    else:
        for c in tree.children():
            count_vars(c, tbl)

def compile(tree):
    # Calculate the varhash, with most common variables having smaller numbers (slight optimisation)
    varcount = dict()
    count_vars(tree, varcount)
    varcount = sorted(varcount.items(), key=lambda item: item[1], reverse=True)
    varhash = {}
    i = 0
    for (v, _) in varcount:
        varhash[v] = i
        i += 1
    return f"({compile_tree(tree, varhash)}) {std.state.make(i)}"