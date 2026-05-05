"""
MPS 案例：主生产计划（Master Production Schedule, MPS）
使用 Google OR-Tools pywraplp 混合整数规划（MIP）求解

问题描述：
  - 1 种产品，2 个计划周期（t=1, 2）
  - 需求量：D1=10, D2=15
  - 期初库存：I0=5，安全库存要求：SS=2
  - 每期最大产能：Cap=20
  - 单位生产成本 C=10，生产准备成本 S=50，单位库存持有成本 H=2
  - 目标：最小化总成本（生产成本 + 准备成本 + 库存成本）

决策变量：
  - X1, X2 : 第 1、2 期的生产数量（连续）
  - Y1, Y2 : 第 1、2 期是否开机生产（二进制，=1 表示生产）
  - I1, I2 : 第 1、2 期末的库存量（连续）

约束条件：
  (1) 库存平衡约束（Inventory Balance）
      I1 = I0 + X1 - D1   =>  I1 - X1 = -5  （等式）
      I2 = I1 + X2 - D2   =>  I2 - I1 - X2 = -15  （等式）
  (2) 生产与准备逻辑约束（Setup Logic，Big-M = 100）
      X1 <= M * Y1   =>  X1 - 100*Y1 <= 0
      X2 <= M * Y2   =>  X2 - 100*Y2 <= 0
  (3) 产能约束（Capacity）
      X1 <= Cap = 20
      X2 <= Cap = 20
  (4) 安全库存约束（Safety Stock）
      I1 >= SS = 2
      I2 >= SS = 2
"""

from ortools.init.python import init
from ortools.linear_solver import pywraplp


def main():
    print("Google OR-Tools version:", init.OrToolsVersion.version_string())

    # ------------------------------------------------------------------ #
    #  参数定义
    # ------------------------------------------------------------------ #
    D1   = 10    # 第 1 期需求量
    D2   = 15    # 第 2 期需求量
    I0   = 5     # 期初库存
    SS   = 2     # 安全库存要求
    Cap  = 20    # 每期最大产能
    C    = 10    # 单位生产成本
    S    = 50    # 单次生产准备成本
    H    = 2     # 单位库存持有成本（每期）
    BIG_M = 100  # Big-M 常数（需大于最大可能生产量）

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
    # 连续变量：生产数量（下界 0）
    X1 = solver.NumVar(0, infinity, "X1")   # 第 1 期生产数量
    X2 = solver.NumVar(0, infinity, "X2")   # 第 2 期生产数量

    # 连续变量：期末库存（下界 0）
    I1 = solver.NumVar(0, infinity, "I1")   # 第 1 期末库存
    I2 = solver.NumVar(0, infinity, "I2")   # 第 2 期末库存

    # 二进制变量：是否开机生产
    Y1 = solver.IntVar(0, 1, "Y1")   # 第 1 期是否生产
    Y2 = solver.IntVar(0, 1, "Y2")   # 第 2 期是否生产

    print("Number of variables =", solver.NumVariables())

    # ------------------------------------------------------------------ #
    #  约束条件
    # ------------------------------------------------------------------ #

    # (1) 库存平衡约束 —— 等式约束（lb = ub = rhs）
    # 第 1 期：I1 - X1 = I0 - D1 = 5 - 10 = -5
    rhs1 = I0 - D1   # = -5
    c_inv1 = solver.Constraint(rhs1, rhs1, "INV1")
    c_inv1.SetCoefficient(I1,  1)
    c_inv1.SetCoefficient(X1, -1)

    # 第 2 期：I2 - I1 - X2 = -D2 = -15
    rhs2 = -D2        # = -15
    c_inv2 = solver.Constraint(rhs2, rhs2, "INV2")
    c_inv2.SetCoefficient(I2,  1)
    c_inv2.SetCoefficient(I1, -1)
    c_inv2.SetCoefficient(X2, -1)

    # (2) 生产与准备逻辑约束（Big-M）
    # X1 - M*Y1 <= 0
    c_set1 = solver.Constraint(-infinity, 0, "SET1")
    c_set1.SetCoefficient(X1,  1)
    c_set1.SetCoefficient(Y1, -BIG_M)

    # X2 - M*Y2 <= 0
    c_set2 = solver.Constraint(-infinity, 0, "SET2")
    c_set2.SetCoefficient(X2,  1)
    c_set2.SetCoefficient(Y2, -BIG_M)

    # (3) 产能约束 —— 每期生产量不超过最大产能
    # X1 <= Cap
    c_cap1 = solver.Constraint(-infinity, Cap, "CAP1")
    c_cap1.SetCoefficient(X1, 1)

    # X2 <= Cap
    c_cap2 = solver.Constraint(-infinity, Cap, "CAP2")
    c_cap2.SetCoefficient(X2, 1)

    # (4) 安全库存约束 —— 期末库存不低于安全库存
    # I1 >= SS  =>  -I1 <= -SS
    c_ss1 = solver.Constraint(SS, infinity, "SS1")
    c_ss1.SetCoefficient(I1, 1)

    # I2 >= SS
    c_ss2 = solver.Constraint(SS, infinity, "SS2")
    c_ss2.SetCoefficient(I2, 1)

    print("Number of constraints =", solver.NumConstraints())

    # ------------------------------------------------------------------ #
    #  目标函数：最小化总成本
    #  Min  C*X1 + C*X2 + S*Y1 + S*Y2 + H*I1 + H*I2
    # ------------------------------------------------------------------ #
    objective = solver.Objective()
    objective.SetCoefficient(X1,  C)
    objective.SetCoefficient(X2,  C)
    objective.SetCoefficient(Y1,  S)
    objective.SetCoefficient(Y2,  S)
    objective.SetCoefficient(I1,  H)
    objective.SetCoefficient(I2,  H)
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
    print("  MPS 主生产计划 —— 最优解")
    print("=" * 60)
    print(f"  目标函数（最小总成本） = {objective.Value():.1f}")
    print()
    print("  成本拆解：")
    prod_cost = C * (X1.solution_value() + X2.solution_value())
    setup_cost = S * (Y1.solution_value() + Y2.solution_value())
    hold_cost = H * (I1.solution_value() + I2.solution_value())
    print(f"    生产成本  = {C} × ({X1.solution_value():.1f} + {X2.solution_value():.1f}) = {prod_cost:.1f}")
    print(f"    准备成本  = {S} × ({Y1.solution_value():.0f} + {Y2.solution_value():.0f}) = {setup_cost:.1f}")
    print(f"    库存成本  = {H} × ({I1.solution_value():.1f} + {I2.solution_value():.1f}) = {hold_cost:.1f}")
    print()
    print("  生产计划（MPS 排产结果）：")
    print(f"    第 1 期：Y1={Y1.solution_value():.0f}（{'生产' if Y1.solution_value() > 0.5 else '不生产'}），"
          f"X1={X1.solution_value():.1f}，期末库存 I1={I1.solution_value():.1f}")
    print(f"    第 2 期：Y2={Y2.solution_value():.0f}（{'生产' if Y2.solution_value() > 0.5 else '不生产'}），"
          f"X2={X2.solution_value():.1f}，期末库存 I2={I2.solution_value():.1f}")
    print()
    print("  库存平衡验证：")
    print(f"    第 1 期：期初{I0} + 生产{X1.solution_value():.1f} - 需求{D1} = {I0 + X1.solution_value() - D1:.1f}（= I1={I1.solution_value():.1f}）")
    print(f"    第 2 期：期初{I1.solution_value():.1f} + 生产{X2.solution_value():.1f} - 需求{D2} = {I1.solution_value() + X2.solution_value() - D2:.1f}（= I2={I2.solution_value():.1f}）")
    print("=" * 60)
    print()
    print("Advanced usage:")
    print(f"Problem solved in {solver.wall_time():d} milliseconds")
    print(f"Problem solved in {solver.iterations():d} iterations")


if __name__ == "__main__":
    init.CppBridge.init_logging("mps_or_tools.py")
    cpp_flags = init.CppFlags()
    cpp_flags.stderrthreshold = True
    cpp_flags.log_prefix = False
    init.CppBridge.set_flags(cpp_flags)
    main()
