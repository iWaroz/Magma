color_stack = 0
colors = ["\x1b[31m", "\x1b[32m", "\x1b[33m", "\x1b[34m", "\x1b[35m", "\x1b[36m"]

def open_color():
    global color_stack
    color_stack += 1
    return colors[color_stack % len(colors)]

def close_color():
    global color_stack
    color_stack -= 1
    return colors[color_stack % len(colors)]

def _prettify(tree):
    tree = tree.unwrap()
    if tree.type == "call":
        return open_color() + f"({_prettify(tree.left)} {_prettify(tree.right)})" + close_color()
    if tree.type == "var":
        return tree.var
    if tree.type == "lambda":
        return open_color() + f"[λ{tree.arg}.{_prettify(tree.body)}]" + close_color()

def pretty(tree) -> str:
    return _prettify(tree) + "\x1b[39m"

def pretty_print(tree):
    print(_prettify(tree) + "\x1b[39m")