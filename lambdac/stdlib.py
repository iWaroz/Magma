arbitrary_value = "nil"

true = "(λa.λb.a)"
false = "(λa.λb.b)"

class pair:
    def make(x, y):
        return f"(λb.b({x})({y}))"
    
    first = f"(λp.p {true})"
    second = f"(λp.p {false})"

class flow:
    # if then else
    def ifte(cond, trueblock, falseblock):
        return f"(({cond})({trueblock})({falseblock}))"
    
    Y = f"((λf.(λx.f(x x))(λx.f(x x))))"

class bools:
    true = "(λa.λb.a)"
    false = "(λa.λb.b)"
    notgate = f"(λx.x {false} {true})"
    orgate = f"(λa.λb.a a b)"
    andgate = f"(λa.λb.a b a)"

class numbers:
    def make(n):
        return f"(λf.λa.{'(f ' * n}a{')'*n})"

    iszero = f"(λn.n(λa.{false}){true})" # n == 0?
    succ = f"(λn.λf.λa.f(n f a))" # n + 1
    pred = "(λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u))" # n - 1
    mult = f"(λn.λm.λf.n(m f))" # n * m
    add = f"(λn.λm.λf.λa.n f (m f a))" # n + m
    sub = f"(λn.λm.m {pred} n)" # n - m
    geq = f"(λn.λm.{iszero} ({sub} m n))" # n >= m iff m - n <= 0 iff m - n = 0 since (0 - 1 -> 0)
    leq = f"(λn.λm.{iszero} ({sub} n m))" # n <= m
    ge = f"(λn.λm.({bools.notgate} ({iszero} ({sub} n m))))" # n > m iff n - m > 0 iff n - m != 0
    le = f"(λn.λm.({bools.notgate} ({iszero} ({sub} m n))))" # n < m
    eq = f"(λn.λm.{bools.andgate} ({leq} n m) ({leq} m n))" # m == n iff n <= m and n >= m
    div = f"({flow.Y} λF.λn.λm.({le} n m)({make(0)})(F ({sub} n m) m))" # n / m
    mod = f"({flow.Y} λF.λn.λm.({le} n m) n (F ({sub} n m) m))" # n % m

    fact = f"({flow.Y} (λF.λn.({iszero} n) ({make(1)}) (λf.n (F ({pred} n) f))))"


class linked_list:
    def make(size):
        if size == 0:
            return arbitrary_value
        return pair.make(arbitrary_value, linked_list.make(size-1))
    
    # Args: list num
    getter = f"(λl.λn.((n (λp.p {false}) l) ({true})))"

    # Args: list num newval
    setter = f"({flow.Y} (λF.λl.λn.λx.({numbers.iszero} n) (λp.p(x)({pair.second} l)) (λp.p({pair.first} l)(F ({pair.second} l) ({numbers.pred} n) x))))"

def make_array(contents):
    if len(contents) == 0:
        return pair.make(false, arbitrary_value)
    return pair.make(true, pair.make(contents[0], make_array(contents[1:])))

class array:
    # Data type for usage by the program
    make = make_array

    # New list [e, ...lst]
    def prepend(e, lst):
        return pair.make(true, pair.make(e, lst))
    
    head = f"(λl.{pair.first} ({pair.second} l))"
    tail = f"(λl.{pair.second} ({pair.second} l))"

    # Args: arr id
    getter = f"(λl.λn.(n (λp.p {false} {false}) l) {false} {true})"

    # Args: arr id val
    setter = f"({flow.Y} (λF.λl.λn.λx.({numbers.iszero} n) (λb.b({true})(λp.p(x)({tail} l))) (λb.b({true})(λp.p({head} l)(F ({tail} l) ({numbers.pred} n) x)))))"

    # Args: arr (g := λacc.λx.acc') acc
    fold_left = f"({flow.Y} (λF.λl.λg.λa.({pair.first} l) (F ({tail} l) g (g a ({head} l))) a))"

    # range n m gives [n, n+1, ..., m]
    range = f"({flow.Y} (λF.λn.λm.({numbers.eq} n m)({make(['m'])})(" + prepend('n', f"(F ({numbers.succ} n) m)") + ")))"

class state:
    def make(memsize):
        # <Memory, Print>
        return f"(λi.i({linked_list.make(memsize)})({linked_list.make(0)}))"

    # Helper functions
    get_mem = f"(st {true})"
    get_prnt = f"(st {false})"

    set_mem =  f"(λm.λi.i m {get_prnt})"
    set_prnt = f"(λm.λi.i {get_mem} m)"

    # Provide variable id as arg
    get_variable = f"({linked_list.getter} {get_mem})"

    # State pipeline functions
    def variable_setter(varid, value):
        if isinstance(varid, int):
            varid = numbers.make(varid)
        return f"(λst.{state.set_mem} ({linked_list.setter} {state.get_mem} ({varid}) ({value})))"

    def array_setter(varid, ind, value):
        if isinstance(varid, int):
            varid = numbers.make(varid)
        return state.variable_setter(varid, f"{array.setter} ({state.get_mem} ({varid})) {ind} {value}")

    def printer(value):
        return f"(λst.{state.set_prnt} (λp.p({value}){state.get_prnt}))"
    
    def repeater(value, body):
        return f"({value} ({body}))"
    
    # Doubt
    def for_loop(varid, iterable, body):
        if isinstance(varid, int):
            varid = numbers.make(varid)
        # arr (g := λst.λx.st') st
        var_setter = f"{state.set_mem} ({linked_list.setter} {state.get_mem} {varid} x)"
        var_setter = state.variable_setter(varid, f"{array.head} l")
        return f"(λst.{flow.Y} (λF.λl.λst.({pair.first} l) (F ({array.tail} l) ({body} ({var_setter} st))) st) ({iterable}) st)"
    
    def while_loop(expr, body):
        return f"({flow.Y} (λF.λst.({expr}) (F ({body} st)) st) )"
    
    def if_statement(expr, true_block, false_block):
        return f"(λst.{expr} ({true_block} st) ({false_block} st))"