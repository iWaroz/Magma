class Repr(type):
    def __repr__(cls):
        return cls.__name__

class SToken(metaclass=Repr):
    pass

class Expression(SToken):
    def __init__(self):
        pass

class Not(Expression):
    def __init__(self, expr):
        self.expr = expr
    
    def children(self):
        return [self.expr]

class BinaryOperator(Expression):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    
    def children(self):
        return [self.left, self.right]

class Var(Expression):
    def __init__(self, name):
        self.name = name
    
    def children(self):
        return []

class Array(Expression):
    def __init__(self, inner):
        self.inner = inner
    
    def children(self):
        return self.inner

class IntLiteral(Expression):
    def __init__(self, value):
        self.value = value
    
    def children(self):
        return []

class BoolLiteral(Expression):
    def __init__(self, value):
        self.value = value
    
    def children(self):
        return []

class While(SToken):
    def __init__(self, cond, block):
        self.cond = cond
        self.block = block
    
    def children(self):
        return [self.cond, self.block]

class If(SToken):
    def __init__(self, cond, block, elseblock=None):
        self.cond = cond
        self.block = block
        self.elseblock = elseblock
    
    def children(self):
        return [self.cond, self.block] + ([] if self.elseblock is None else [self.elseblock])

class For(SToken):
    def __init__(self, var, iterator, block):
        self.var = var
        self.iterator = iterator
        self.block = block
    
    def children(self):
        return [self.iterator, self.block]

class Print(SToken):
    def __init__(self, expr):
        self.expr = expr
    
    def children(self):
        return [self.expr]

class Repeat(SToken):
    def __init__(self, count, block):
        self.counter = count
        self.block = block
    
    def children(self):
        return [self.counter, self.block]

class VarAssign(SToken):
    def __init__(self, varname, expr):
        self.varname = varname
        self.expr = expr
    
    def children(self):
        return [self.expr]

class ArrAssign(SToken):
    def __init__(self, varname, ind, expr):
        self.varname = varname
        self.ind = ind
        self.expr = expr
    
    def children(self):
        return [self.expr, self.ind]

class CodeBlock(SToken):
    def __init__(self, lines):
        self.lines = lines
    
    def children(self):
        return self.lines