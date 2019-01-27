from check import Check
from optimise import Optimise


def solver(problem):
    colors = problem.get("colors")
    customers = problem.get("customers")
    demands = problem.get("demands")

    check = Check(colors, customers, demands)

    return get_results(check.check())


def get_results(check):
    if check.possible:
        opt = Optimise(check.colors, check.customers, check.solution, check.nd_arr)
        opt.iterate_all_combinations()
        return " ".join(map(str, opt.solution))
    else:
        return "IMPOSSIBLE"
