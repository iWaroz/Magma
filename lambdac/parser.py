import string
from collections import deque

def lex(src):
    tokens = []
    buffer = ""

    for c in src:
        if c in ["(", ")", ".", "λ"]:
            if buffer != "":
                tokens.append(buffer)
                buffer = ""
            tokens.append(c)
        if c in string.whitespace:
            if buffer != "":
                tokens.append(buffer)
                buffer = ""
        if c in string.ascii_letters + "_" + string.digits:
            buffer += c

    if buffer != "":
        tokens.append(buffer)
    return tokens

PUNC = "()λ."
VAR = "var"

class LambdaTerm:
    # Unwraps nodes
    def unwrap(self):
        while self.type == "node":
            self = self.term
        return self
    
    @property
    def _type(self):
        return self.unwrap().type

# Mutable wrappers for lambda terms to allow for in place reduction within a tree
class Node(LambdaTerm):
    def __init__(self, term):
        self.term: LambdaTerm = term
        self.type = "node"

class Variable(LambdaTerm):
    def __init__(self, var):
        self.type = "var"
        self.var: str = var

# Represents λarg.body
class Abstraction(LambdaTerm):
    def __init__(self, arg, body):
        self.type = "lambda"
        self.arg: str = arg
        self.body: LambdaTerm = body
    
    @property
    def _body(self):
        return self.body.unwrap()

# Representes (left right)
class Application(LambdaTerm):
    def __init__(self, left, right):
        self.type = "call"
        self.left: LambdaTerm = left
        self.right: LambdaTerm = right

    @property
    def _left(self):
        return self.left.unwrap()
    
    @property
    def _right(self):
        return self.right.unwrap()

class Stream:
    def __init__(self, tokenlist):
        self.tokens = tokenlist + ["EOF"]
        self.depth = 0

    def consume(self):
        self.depth += 1
        return self.tokens[self.depth - 1]

    def expect(self, typ):
        if typ in PUNC:
            assert self.tokens[self.depth] == typ
        if typ == VAR:
            assert self.tokens[self.depth] not in PUNC
        return self.consume()
    
    @property
    def peek(self):
        return self.tokens[self.depth]

# Turn f g h t into (((f g) h) t), or with more functions
def call_collapse(terms):
    if len(terms) == 2:
        return Node(Application(terms[0], terms[1]))
    else:
        return Node(Application(call_collapse(terms[:-1]), terms[-1]))

# Parse any lambda expression
def parse_lambda_term(stream):
    if stream.peek == "λ":
        stream.expect("λ")
        varname = stream.expect(VAR)
        stream.expect(".")
        body = parse_lambda_term(stream)
        return Node(Abstraction(varname, body))
    else:
        terms = []
        while stream.peek not in [")", "EOF"]:
            if stream.peek == "(":
                stream.expect("(")
                terms.append(parse_lambda_term(stream))
                stream.expect(")")
            elif stream.peek not in PUNC:
                terms.append(Node(Variable(stream.expect(VAR))))
            elif stream.peek == "λ":
                terms.append(parse_lambda_term(stream))
        
        if len(terms) == 1:
            return terms[0]
        else:
            return call_collapse(terms)