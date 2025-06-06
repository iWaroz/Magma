import sys
import time

import lambdac.parser as lcp
import lambdac.reducer as lcr
import lambdac.prettyprint as pretty

import magma.tokenize as mgt
import magma.grammar as mgg
import magma.to_lambda as mgl

if len(sys.argv) == 1:
    print("Invalid Usage: run\033[1;35m magma help\033[1;0m for help")
    exit(1)

if sys.argv[1] == "compile":
    if len(sys.argv) < 3:
        print("No file name provided, try\033[1;35m magma compile file.mg\033[1;0m")
        exit(1)
    fname = sys.argv[2]
    with open(fname) as f:
        src = f.read()
    tokens = mgt.tokenize(src)
    indtokens = mgt.indentation_handler(tokens)
    tree = mgg.parse_tokens(indtokens)
    lambd = mgl.compile(tree)
    if len(sys.argv) < 4:
        print(lambd)
    else:
        with open(sys.argv[3], "w", encoding="utf-8") as f:
            f.write(lambd)
        print(f"Successfully compiled\033[1;35m {sys.argv[2]}\033[1;0m to\033[1;35m {sys.argv[3]}\033[1;0m")

elif sys.argv[1] == "run":
    if len(sys.argv) < 3:
        print("No file name provided, try\033[1;35m magma run file.lc\033[1;0m")
        exit(1)
    with open(sys.argv[2], encoding="utf-8") as f:
        src = f.read()
    tree = lcr.parse_lambda_term(lcp.Stream(lcp.lex(src)))
    print("|>", pretty.pretty(tree))
    counter = 0
    total_steps = 0

    t0 = time.perf_counter()
    while lcr.perform_reduction(tree):
        total_steps += 1
        if total_steps % 200 == 0:
            print(total_steps, "steps ran")
    t1 = time.perf_counter()
    print("β>", pretty.pretty(tree))
    lcr.render_state_printer(tree)
    print(f"Executed in {total_steps} steps")
    print(f"Took {t1-t0:2f} seconds")