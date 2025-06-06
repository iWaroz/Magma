import regex

class Repr(type):
    def __repr__(cls):
        return cls.__name__

class Token(metaclass=Repr):
    @classmethod
    def strn(self=None):
        return self.__name__

class Id(Token):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Id<{self.name}>"

class Int(Token):
    def __init__(self, num):
        self.num = num
    
    def strn(self=None):
        if self == None:
            return "Int"
        return f"Int:{self.num}"

    def __repr__(self):
        return f"Int<{self.num}>"
    
class Bool(Token):
    def __init__(self, val):
        self.val = val
    
    def strn(self=None):
        if self == None:
            return "Bool"
        return f"Bool:{self.val}"
    
    def __repr__(self):
        return f"Bool<{self.val}>"

class Operator(Token):
    def __init__(self, op):
        self.op = op
    
    def strn(self=None):
        if self == None:
            return "Op"
        return f"Op:{self.op}"
    
    def __repr__(self):
        return f"Op<{self.op}>"

class IndentDelta(Token):
    def __init__(self, delta):
        self.delta = delta
    
    def strn(self=None):
        if self == None:
            return "Delta"
        return f"Delta:{self.delta / abs(self.delta)}"

    def __repr__(self):
        return f"Delta<{self.delta}>"

class EOF(Token):
    pass

class Print(Token):
    pass

class If(Token):
    pass

class Elif(Token):
    pass

class Else(Token):
    pass

class For(Token):
    pass

class In(Token):
    pass

class Repeat(Token):
    pass

class While(Token):
    pass

class OpenBracket(Token):
    pass

class CloseBracket(Token):
    pass

class OpenParen(Token):
    pass

class CloseParen(Token):
    pass

class Indent(Token):
    pass

class Space(Token):
    pass

class NewLine(Token):
    pass

lexem_to_token = {
    "\n": NewLine,
    "(": OpenParen,
    ")": CloseParen,
    "[": OpenBracket,
    "]": CloseBracket,
    " ": Space,
    "\t": Indent
}

operators = ["=", "*", "**", "+", "-", "/", "%", "&", "||", "!", "<", ">", "<=", ">=", "==", "!=", "..", ",", "@"]
special_characters = "=*+-/%&|!<>.,@"

keywords = {
    "if": If,
    "else": Else,
    "elif": Elif,
    "for": For,
    "repeat": Repeat,
    "while": While,
    "print": Print,
    "in": In
}

def buffer_to_token(buffer):
    if buffer.isnumeric():
        return Int(int(buffer))
    if buffer in keywords:
        return keywords[buffer]
    if buffer in operators:
        return Operator(buffer)
    if buffer in ["true", "false"]:
        return Bool(buffer)
    if regex.match(r"\w(\w|\d|_)*", buffer):
        return Id(buffer)

def clear_buffer(buffer, tokens):
    new_token = buffer_to_token(buffer)

    if new_token is not None:
        return "", tokens + [new_token]
    return "", tokens

def tokenize(src: str):
    buffer = ""
    # -1 for arbitrary
    # 0 for text/numbers
    # 1 for special characters
    buffer_type = -1
    tokens = []
    for c in src:
        if c in lexem_to_token:
            buffer, tokens = clear_buffer(buffer, tokens)
            buffer_type = -1
            tokens.append(lexem_to_token[c])
        elif c in special_characters:
            if buffer_type != 1:
                buffer, tokens = clear_buffer(buffer, tokens)
            buffer += c
            buffer_type = 1
        else:
            if buffer_type != 0:
                buffer, tokens = clear_buffer(buffer, tokens)
            buffer += c
            buffer_type = 0
    buffer, tokens = clear_buffer(buffer, tokens)

    return tokens

def handle_negative_deltas(delta_stack, tokens, Δ):
    while Δ < 0:
        latest_up = delta_stack.pop()
        Δ += latest_up
        tokens.append(IndentDelta(-latest_up))

def indentation_handler(input_tokens):
    # Remove unnecessary Space tokens
    just_newlined = True
    despaced_tokens = []
    for token in input_tokens:
        if token in [Space, Indent]:
            if just_newlined:
                # Count indents as two spaces, not very sophisticated
                despaced_tokens += [Space] * (1 if token == Space else 2)
        elif token == NewLine:
            just_newlined = True
            despaced_tokens.append(NewLine)
        else:
            just_newlined = False
            despaced_tokens.append(token)

    # Replace newlines and spaces with IndentDelta instances
    # IndentDelta(0) means same level as previous code
    # Newlines between opening and closing parenthesises/brackets are considered to be cosmetic and thus ignored
    bracket_depth = 0 # Includes brackets and parenthesises, does not Dyck-validate
    indent_level = 0
    local_indent_level = -1
    delta_stack = []

    tokens = []
    for token in despaced_tokens:
        if token == NewLine:
            if bracket_depth == 0: local_indent_level = 0
        elif token == Space:
            if bracket_depth == 0: local_indent_level += 1
        else:
            if local_indent_level != -1: # only triggers at most once per line
                Δ = local_indent_level - indent_level
                if Δ > 0:
                    tokens.append(IndentDelta(Δ))
                    delta_stack.append(Δ)
                elif Δ < 0: # add multiple negative deltas in case of closing multiple blocks at once
                    handle_negative_deltas(delta_stack, tokens, Δ)
                indent_level = local_indent_level
                local_indent_level = -1 # prevent next token in line from handling the indent
            if token in [OpenBracket, OpenParen]:
                bracket_depth += 1
                tokens.append(token)
            elif token in [CloseBracket, CloseParen]:
                bracket_depth -= 1
                tokens.append(token)
            else:
                tokens.append(token)
    handle_negative_deltas(delta_stack, tokens, -indent_level)
    tokens.append(EOF)

    return tokens