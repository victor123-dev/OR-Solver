"""
APS 案例：车间调度问题（Job Shop Scheduling Problem, JSP）
使用 Google OR-Tools pywraplp 混合整数规划（MIP）求解

问题描述：
  - 2 个工单（Job 1, Job 2），2 台机器（M1, M2）
  - Job 1 工艺路线：M1（加工时长 p11=3） → M2（加工时长 p12=2）
  - Job 2 工艺路线：M2（加工时长 p22=4） → M1（加工时长 p21=1）
  - 目标：最小化最大完工时间 Cmax（Makespan）

决策变量：
  - x11, x12 : Job 1 在 M1、M2 上的开始时间（连续）
  - x21, x22 : Job 2 在 M1、M2 上的开始时间（连续）
  - z121      : 二进制，=1 表示 M1 上 Job 1 先于 Job 2
  - z122      : 二进制，=1 表示 M2 上 Job 1 先于 Job 2
  - cmax      : 最大完工时间（连续）

约束条件：
  (1) 工序先后顺序约束（Precedence）
      Job 1: x12 >= x11 + p11
      Job 2: x21 >= x22 + p22
  (2) 完工时间约束（Makespan）
      cmax >= x12 + p12
      cmax >= x21 + p21
  (3) 机器产能独占约束（Disjunctive，Big-M = 100）
      M1: x11 - x21 + M*z121 <= M - p11   (z121=1 时 Job1 先)
          x21 - x11 - M*z121 <= -p21      (z121=0 时 Job2 先)
      M2: x12 - x22 + M*z122 <= M - p12   (z122=1 时 Job1 先)
          x22 - x12 - M*z122 <= -p22      (z122=0 时 Job2 先)
"""

from ortools.init.python import init
from ortools.linear_solver import pywraplp


def main():
    print("Google OR-Tools version:", init.OrToolsVersion.version_string())

    # ------------------------------------------------------------------ #
    #  加工时间参数
    # ------------------------------------------------------------------ #
    p11 = 3   # Job 1 在 M1 上的加工时长
    p12 = 2   # Job 1 在 M2 上的加工时长
    p22 = 4   # Job 2 在 M2 上的加工时长
    p21 = 1   # Job 2 在 M1 上的加工时长
    BIG_M = 100  # Big-M 常数（需大于所有可能的完工时间）

    # ------------------------------------------------------------------ #
    #  创建 MIP 求解器（SCIP 支持混合整数规划）
    # ------------------------------------------------------------------ #
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        print("Could not create solver SCIP")
        return

    infinity = solver.infinity()

    # ------------------------------------------------------------------ #
    #  决策变量
    # ------------------------------------------------------------------ #
    # 连续变量：各工序开始时间（下界 0，上界无穷）
    x11 = solver.NumVar(0, infinity, "x11")   # Job 1 在 M1 上的开始时间
    x12 = solver.NumVar(0, infinity, "x12")   # Job 1 在 M2 上的开始时间
    x21 = solver.NumVar(0, infinity, "x21")   # Job 2 在 M1 上的开始时间
    x22 = solver.NumVar(0, infinity, "x22")   # Job 2 在 M2 上的开始时间
    cmax = solver.NumVar(0, infinity, "cmax") # 最大完工时间

    # 二进制变量：机器上的加工顺序
    z121 = solver.IntVar(0, 1, "z121")  # =1: M1 上 Job1 先于 Job2
    z122 = solver.IntVar(0, 1, "z122")  # =1: M2 上 Job1 先于 Job2

    print("Number of variables =", solver.NumVariables())

    # ------------------------------------------------------------------ #
    #  约束条件
    # ------------------------------------------------------------------ #

    # (1) 工序先后顺序约束 —— 同一工单必须按工艺路线顺序加工
    # Job 1: x12 >= x11 + p11  =>  x11 - x12 <= -p11
    c_prec1 = solver.Constraint(-infinity, -p11, "PREC1")
    c_prec1.SetCoefficient(x11,  1)
    c_prec1.SetCoefficient(x12, -1)

    # Job 2: x21 >= x22 + p22  =>  x22 - x21 <= -p22
    c_prec2 = solver.Constraint(-infinity, -p22, "PREC2")
    c_prec2.SetCoefficient(x22,  1)
    c_prec2.SetCoefficient(x21, -1)

    # (2) 完工时间约束 —— cmax >= 每个工单最后一道工序的完成时间
    # cmax >= x12 + p12  =>  x12 - cmax <= -p12
    c_mksp1 = solver.Constraint(-infinity, -p12, "MKSP1")
    c_mksp1.SetCoefficient(x12,   1)
    c_mksp1.SetCoefficient(cmax, -1)

    # cmax >= x21 + p21  =>  x21 - cmax <= -p21
    c_mksp2 = solver.Constraint(-infinity, -p21, "MKSP2")
    c_mksp2.SetCoefficient(x21,   1)
    c_mksp2.SetCoefficient(cmax, -1)

    # (3) 机器产能独占约束（Big-M 析取约束）
    # M1 — 约束 A：x11 - x21 + M*z121 <= M - p11
    c_disj1a = solver.Constraint(-infinity, BIG_M - p11, "DISJ1A")
    c_disj1a.SetCoefficient(x11,   1)
    c_disj1a.SetCoefficient(x21,  -1)
    c_disj1a.SetCoefficient(z121,  BIG_M)

    # M1 — 约束 B：x21 - x11 - M*z121 <= -p21
    c_disj1b = solver.Constraint(-infinity, -p21, "DISJ1B")
    c_disj1b.SetCoefficient(x21,   1)
    c_disj1b.SetCoefficient(x11,  -1)
    c_disj1b.SetCoefficient(z121, -BIG_M)

    # M2 — 约束 C：x12 - x22 + M*z122 <= M - p12
    c_disj2a = solver.Constraint(-infinity, BIG_M - p12, "DISJ2A")
    c_disj2a.SetCoefficient(x12,   1)
    c_disj2a.SetCoefficient(x22,  -1)
    c_disj2a.SetCoefficient(z122,  BIG_M)

    # M2 — 约束 D：x22 - x12 - M*z122 <= -p22
    c_disj2b = solver.Constraint(-infinity, -p22, "DISJ2B")
    c_disj2b.SetCoefficient(x22,   1)
    c_disj2b.SetCoefficient(x12,  -1)
    c_disj2b.SetCoefficient(z122, -BIG_M)

    print("Number of constraints =", solver.NumConstraints())

    # ------------------------------------------------------------------ #
    #  目标函数：最小化 Cmax
    # ------------------------------------------------------------------ #
    objective = solver.Objective()
    objective.SetCoefficient(cmax, 1)
    objective.SetMinimization()

    # ------------------------------------------------------------------ #
    #  求解
    # ------------------------------------------------------------------ #
    print(f"Solving with {solver.SolverVersion()}")
    result_status = solver.Solve()

    print(f"Status: {result_status}")
    if result_status != pywraplp.Solver.OPTIMAL:
        print("The problem does not have an optimal solution!")
        if result_status == pywraplp.Solver.FEASIBLE:
            print("A potentially suboptimal solution was found")
        else:
            print("The solver could not solve the problem.")
            return

    # ------------------------------------------------------------------ #
    #  输出结果
    # ------------------------------------------------------------------ #
    print()
    print("=" * 60)
    print("  APS 车间排程 —— 最优解")
    print("=" * 60)
    print(f"  目标函数（最大完工时间 Cmax） = {cmax.solution_value():.1f}")
    print()
    print("  加工顺序决策：")
    print(f"    z121 = {z121.solution_value():.0f}  "
          f"（M1 上：{'Job1 先于 Job2' if z121.solution_value() > 0.5 else 'Job2 先于 Job1'}）")
    print(f"    z122 = {z122.solution_value():.0f}  "
          f"（M2 上：{'Job1 先于 Job2' if z122.solution_value() > 0.5 else 'Job2 先于 Job1'}）")
    print()
    print("  甘特图时间表（开始时间 → 结束时间）：")
    print(f"    Job 1 @ M1 : [{x11.solution_value():.1f}, {x11.solution_value() + p11:.1f}]")
    print(f"    Job 1 @ M2 : [{x12.solution_value():.1f}, {x12.solution_value() + p12:.1f}]")
    print(f"    Job 2 @ M2 : [{x22.solution_value():.1f}, {x22.solution_value() + p22:.1f}]")
    print(f"    Job 2 @ M1 : [{x21.solution_value():.1f}, {x21.solution_value() + p21:.1f}]")
    print("=" * 60)
    print()
    print("Advanced usage:")
    print(f"Problem solved in {solver.wall_time():d} milliseconds")
    print(f"Problem solved in {solver.iterations():d} iterations")


if __name__ == "__main__":
    init.CppBridge.init_logging("aps_or_tools.py")
    cpp_flags = init.CppFlags()
    cpp_flags.stderrthreshold = True
    cpp_flags.log_prefix = False
    init.CppBridge.set_flags(cpp_flags)
    main()
