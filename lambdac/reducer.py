# Returns Free[term], Bound[term]
def get_variables(term): # Empty set is not modified, this is fine
    term = term.unwrap()
    if term._type == "lambda":
        return get_variables(term.body, bound | {term.arg})
    if term._type == "call":
        leftf, leftb = get_variables(term._left, bound)
        rightf, rightb = get_variables(term._right, bound)
        return leftf | rightf, leftb | rightb
    if term._type == "var":
        if term.var in bound:
            return set(), bound
        else:
            return {term.var}, bound

def alpha_reduce(term):
    term = term.unwrap()
    if term.type == "var":
        if term.var == x:
            return arg
        return Node(term)
    
    if term.type == "lambda":
        if term.arg == x:
            # Instances of x inside of this term are independant of outside x's, we do nothing
            return Node(term)
        
        argfree, _ = get_variables(arg)
        if term.arg in argfree:
            # Generate fresh variable name
            termfree, termbound = get_variables(term)
            spoiled = argfree | termfree | termbound

            i = 0
            while f"v{i}" in spoiled:
                i += 1

            # Now v{i} is a fresh variable
            body = alpha_reduce(term.body, term.arg, Variable(f"v{i}"))
            return Node(Abstraction(f"v{i}", alpha_reduce(body, x, arg)))
        else:
            return Node(Abstraction(term.arg, alpha_reduce(term.body, x, arg)))
    
    if term.type == "call":
        return Node(Application(alpha_reduce(term.left, x, arg), alpha_reduce(term.right, x, arg)))

def is_beta_reducible(term):
    # Checks if term is of the form (λx.f[x]) y
    term = term.unwrap()
    return term.type == "call" and term._left.type == "lambda"

def beta_reduce(term):
    # Perform a beta-reduction to the contents of the Node, at the root
    # (λx.f[x]) y -> f[x/y]
    term = term.unwrap()
    return alpha_reduce(term._left.body, term._left.arg, term.right)

def perform_reduction(term):
    # Breadth first search (left to right) until beta or eta reducible expression is found
    # Reduce said expression in place and return True, or False if nothing to reduce found (thus normal form)
    queue = deque()
    queue.append(term)
    while len(queue) > 0:
        item = queue.popleft()
        if is_beta_reducible(item):
            item.term = beta_reduce(item)
            return True
        
        if item._type == "lambda":
            queue.append(item.unwrap().body)
        elif item._type == "call":
            queue.append(item.unwrap().left)
            queue.append(item.unwrap().right)
    return False

def render_state_printer(state_tree):
    printer = state_tree.unwrap().body.unwrap().right.unwrap()
    contents = []
    while isinstance(printer, Abstraction):
        try:
            contents.append(printer.body.unwrap().left.unwrap().right.unwrap())
            nprinter = printer.body.unwrap().right.unwrap()
        except:
            print("ERROR>", pretty(printer))
            raise
        printer = nprinter
    for i in contents[::-1]:
        print("P>", pretty(i))