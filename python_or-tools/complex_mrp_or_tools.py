"""
complex_mrp_or_tools.py
=======================
企业级复杂 MRP 案例：多层次、多品种、能力受限批量计划（ML-CLSP）
含 BOM 物料清单、多资源产能约束、缺货惩罚与安全库存

背景：某消费品制造企业生产 2 种成品（FG1, FG2），需要消耗 3 种自制零部件
      （C1, C2, C3）。企业拥有 2 种关键资源（装配线 R1、机加工中心 R2），
      规划周期为 4 周。在满足客户需求、产能限制和安全库存要求的前提下，
      最小化总成本（生产成本 + 换线成本 + 库存成本 + 缺货惩罚）。

=== BOM 物料清单 ===
  FG1 ← 2×C1 + 1×C2
  FG2 ← 1×C1 + 2×C3

=== 外部需求（成品） ===
         第1周  第2周  第3周  第4周
  FG1:     0    30    40    20
  FG2:     0    20    25    15

=== 品项参数 ===
品项  | 生产成本 | 换线成本 | 库存成本 | 缺货成本 | R1工时 | R2工时 | R1换线 | R2换线 | 初始库存 | 安全库存 | 最大产量
FG1  |   50    |   200   |   10    |   80    |  2.0  |  0.5  |  15   |   5   |   10   |    5    |   60
FG2  |   45    |   180   |    8    |   70    |  1.5  |  0.8  |  12   |   8   |    5   |    5    |   50
C1   |   15    |    80   |    3    |    -    |  0.5  |  1.0  |   5   |  10   |   20   |   10    |  120
C2   |   10    |    60   |    2    |    -    |  0.0  |  0.8  |   0   |   8   |   15   |    8    |   80
C3   |   12    |    70   |   2.5   |    -    |  0.0  |  0.6  |   0   |   6   |    8   |    6    |   80

=== 资源产能（小时/周） ===
  R1: 80 小时/周（各周相同）
  R2: 120 小时/周（各周相同）

=== 决策变量 ===
  X[i,t]  : 品项 i 在第 t 周的生产数量（连续）
  Y[i,t]  : 品项 i 在第 t 周是否开机（二进制）
  I[i,t]  : 品项 i 在第 t 周末的库存量（连续）
  BO[i,t] : 成品 i 在第 t 周末的缺货量（连续，仅 FG1/FG2）

=== 约束条件 ===
(1) 成品库存平衡（含缺货）
(2) 零部件库存平衡（含 BOM 相关需求）
(3) 换线逻辑约束（Big-M）
(4) 资源产能约束（含换线时间）
(5) 安全库存约束

=== 目标函数 ===
Min Σ(生产成本 + 换线成本 + 库存成本) + Σ(缺货惩罚)
"""

from ortools.init.python import init
from ortools.linear_solver import pywraplp


# ============================================================
# 问题数据
# ============================================================
items    = ['FG1', 'FG2', 'C1', 'C2', 'C3']
fg_items = ['FG1', 'FG2']
periods  = [1, 2, 3, 4]
resources = ['R1', 'R2']

demand = {
    ('FG1', 1): 0,  ('FG1', 2): 30, ('FG1', 3): 40, ('FG1', 4): 20,
    ('FG2', 1): 0,  ('FG2', 2): 20, ('FG2', 3): 25, ('FG2', 4): 15,
}

bom = {
    'FG1': {'C1': 2, 'C2': 1},
    'FG2': {'C1': 1, 'C3': 2},
}

prod_cost  = {'FG1': 50,  'FG2': 45,  'C1': 15,  'C2': 10,  'C3': 12}
setup_cost = {'FG1': 200, 'FG2': 180, 'C1': 80,  'C2': 60,  'C3': 70}
hold_cost  = {'FG1': 10,  'FG2': 8,   'C1': 3,   'C2': 2,   'C3': 2.5}
back_cost  = {'FG1': 80,  'FG2': 70}

prod_time = {
    'FG1': {'R1': 2.0, 'R2': 0.5},
    'FG2': {'R1': 1.5, 'R2': 0.8},
    'C1':  {'R1': 0.5, 'R2': 1.0},
    'C2':  {'R1': 0.0, 'R2': 0.8},
    'C3':  {'R1': 0.0, 'R2': 0.6},
}
setup_time = {
    'FG1': {'R1': 15, 'R2': 5},
    'FG2': {'R1': 12, 'R2': 8},
    'C1':  {'R1': 5,  'R2': 10},
    'C2':  {'R1': 0,  'R2': 8},
    'C3':  {'R1': 0,  'R2': 6},
}
init_inv   = {'FG1': 10, 'FG2': 5, 'C1': 20, 'C2': 15, 'C3': 8}
safety_stk = {'FG1': 5,  'FG2': 5, 'C1': 10, 'C2': 8,  'C3': 6}
max_prod   = {'FG1': 60, 'FG2': 50, 'C1': 120, 'C2': 80, 'C3': 80}
capacity   = {('R1', t): 80 for t in periods}
capacity.update({('R2', t): 120 for t in periods})


def main():
    print("Google OR-Tools version:", init.OrToolsVersion.version_string())

    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        print("Could not create solver SCIP"); return

    inf = solver.infinity()

    # ============================================================
    # 决策变量
    # ============================================================
    X  = {(i, t): solver.NumVar(0, inf, f'X_{i}_{t}') for i in items for t in periods}
    Y  = {(i, t): solver.IntVar(0, 1,   f'Y_{i}_{t}') for i in items for t in periods}
    Iv = {(i, t): solver.NumVar(0, inf, f'I_{i}_{t}') for i in items for t in periods}
    BO = {(i, t): solver.NumVar(0, inf, f'BO_{i}_{t}') for i in fg_items for t in periods}

    print(f"Number of variables = {solver.NumVariables()}")

    # ============================================================
    # 约束条件
    # ============================================================

    # (1) 成品库存平衡（含缺货）
    # I[i,t] - BO[i,t] = I[i,t-1] - BO[i,t-1] + X[i,t] - D[i,t]
    # => I[i,t] - BO[i,t] - X[i,t] - I[i,t-1] + BO[i,t-1] = -D[i,t]
    for i in fg_items:
        for t in periods:
            d_val = demand.get((i, t), 0)
            if t == 1:
                rhs = float(-d_val + init_inv[i])
            else:
                rhs = float(-d_val)
            ct = solver.Constraint(rhs, rhs, f'INV_{i}_{t}')
            ct.SetCoefficient(Iv[(i, t)],  1)
            ct.SetCoefficient(BO[(i, t)], -1)
            ct.SetCoefficient(X[(i, t)],  -1)
            if t > 1:
                ct.SetCoefficient(Iv[(i, t-1)], -1)
                ct.SetCoefficient(BO[(i, t-1)],  1)

    # (2) 零部件库存平衡（含 BOM 相关需求）
    # I[c,t] = I[c,t-1] + X[c,t] - Σ_{parent} bom[parent][c] * X[parent,t]
    # => I[c,t] - X[c,t] + Σ bom[p][c]*X[p,t] - I[c,t-1] = 0 (t>1)
    # For t=1: I[c,t] - X[c,t] + Σ bom[p][c]*X[p,t] = init_inv[c]
    for c in ['C1', 'C2', 'C3']:
        for t in periods:
            rhs = float(init_inv[c]) if t == 1 else 0.0
            ct = solver.Constraint(rhs, rhs, f'INV_{c}_{t}')
            ct.SetCoefficient(Iv[(c, t)],  1)
            ct.SetCoefficient(X[(c, t)],  -1)
            if t > 1:
                ct.SetCoefficient(Iv[(c, t-1)], -1)
            for parent, children in bom.items():
                if c in children:
                    ct.SetCoefficient(X[(parent, t)], float(children[c]))

    # (3) 换线逻辑约束（Big-M）：X[i,t] <= MaxProd[i] * Y[i,t]
    for i in items:
        for t in periods:
            ct = solver.Constraint(-inf, 0, f'SET_{i}_{t}')
            ct.SetCoefficient(X[(i, t)],  1)
            ct.SetCoefficient(Y[(i, t)], -float(max_prod[i]))

    # (4) 资源产能约束（含换线时间）
    # Σ_i (prod_time[i][r] * X[i,t] + setup_time[i][r] * Y[i,t]) <= Cap[r,t]
    for r in resources:
        for t in periods:
            ct = solver.Constraint(-inf, float(capacity[(r, t)]), f'CAP_{r}_{t}')
            for i in items:
                pt = prod_time[i][r]
                st = setup_time[i][r]
                if pt != 0:
                    ct.SetCoefficient(X[(i, t)], pt)
                if st != 0:
                    ct.SetCoefficient(Y[(i, t)], float(st))

    # (5) 安全库存约束：I[i,t] >= SS[i]
    for i in items:
        for t in periods:
            ss = safety_stk[i]
            if ss > 0:
                ct = solver.Constraint(float(ss), inf, f'SS_{i}_{t}')
                ct.SetCoefficient(Iv[(i, t)], 1)

    print(f"Number of constraints = {solver.NumConstraints()}")

    # ============================================================
    # 目标函数
    # ============================================================
    objective = solver.Objective()
    for i in items:
        for t in periods:
            objective.SetCoefficient(X[(i, t)], prod_cost[i])
            objective.SetCoefficient(Y[(i, t)], float(setup_cost[i]))
            objective.SetCoefficient(Iv[(i, t)], hold_cost[i])
    for i in fg_items:
        for t in periods:
            objective.SetCoefficient(BO[(i, t)], float(back_cost[i]))
    objective.SetMinimization()

    # ============================================================
    # 求解
    # ============================================================
    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()
    print(f"Status: {status}")
    if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        print("No feasible solution found."); return

    # ============================================================
    # 输出结果
    # ============================================================
    print()
    print("=" * 80)
    print("  复杂 MRP 多层次批量计划（ML-CLSP）—— 最优解")
    print("=" * 80)
    print(f"  目标函数值（总成本） = {objective.Value():.2f}")
    print()

    # 成本拆解
    total_prod = sum(prod_cost[i] * X[(i,t)].solution_value() for i in items for t in periods)
    total_setup = sum(setup_cost[i] * Y[(i,t)].solution_value() for i in items for t in periods)
    total_hold = sum(hold_cost[i] * Iv[(i,t)].solution_value() for i in items for t in periods)
    total_back = sum(back_cost[i] * BO[(i,t)].solution_value() for i in fg_items for t in periods)
    print(f"  成本拆解：生产成本={total_prod:.1f}  换线成本={total_setup:.1f}  "
          f"库存成本={total_hold:.1f}  缺货惩罚={total_back:.1f}")
    print()

    # 生产计划表
    print("  【MPS 生产计划（各品项各周期）】")
    header = f"  {'品项':<6}" + "".join(f"{'第'+str(t)+'周':>12}" for t in periods)
    print(header)
    print("  " + "-" * (6 + 12 * len(periods)))
    for i in items:
        row = f"  {i:<6}"
        for t in periods:
            xv = X[(i,t)].solution_value()
            yv = Y[(i,t)].solution_value()
            flag = "●" if yv > 0.5 else " "
            row += f"  {flag}{xv:>7.1f}   "
        print(row)
    print("  （● 表示该周期开机生产）")
    print()

    # 库存状态表
    print("  【期末库存状态（各品项各周期）】")
    print(header)
    print("  " + "-" * (6 + 12 * len(periods)))
    for i in items:
        row = f"  {i:<6}"
        for t in periods:
            iv_val = Iv[(i,t)].solution_value()
            row += f"  {iv_val:>10.1f}  "
        print(row)
    print()

    # 缺货情况
    has_backorder = False
    for i in fg_items:
        for t in periods:
            bv = BO[(i,t)].solution_value()
            if bv > 1e-4:
                if not has_backorder:
                    print("  【缺货预警（Backorder）】")
                    has_backorder = True
                print(f"    {i} 第{t}周末缺货 {bv:.2f} 件，缺货惩罚 = {back_cost[i]}×{bv:.2f} = {back_cost[i]*bv:.2f}")
    if not has_backorder:
        print("  【缺货预警】：无缺货，所有需求均按时满足。")
    print()

    # 产能利用率
    print("  【资源产能利用率（小时）】")
    print(f"  {'资源':<6}" + "".join(f"{'第'+str(t)+'周':>14}" for t in periods))
    print("  " + "-" * (6 + 14 * len(periods)))
    for r in resources:
        row = f"  {r:<6}"
        for t in periods:
            used = sum(
                prod_time[i][r] * X[(i,t)].solution_value() +
                setup_time[i][r] * Y[(i,t)].solution_value()
                for i in items
            )
            cap = capacity[(r, t)]
            row += f"  {used:.1f}/{cap}({100*used/cap:.0f}%)  "
        print(row)
    print()

    # BOM 物料平衡验证
    print("  【BOM 物料平衡验证（关键周期）】")
    for c in ['C1', 'C2', 'C3']:
        for t in periods:
            dep_demand = sum(
                bom.get(parent, {}).get(c, 0) * X[(parent, t)].solution_value()
                for parent in ['FG1', 'FG2']
            )
            if dep_demand > 1e-4:
                prev_inv = init_inv[c] if t == 1 else Iv[(c, t-1)].solution_value()
                prod_qty = X[(c, t)].solution_value()
                end_inv  = Iv[(c, t)].solution_value()
                print(f"    {c} 第{t}周: 期初{prev_inv:.1f} + 生产{prod_qty:.1f} - 消耗{dep_demand:.1f} = 期末{end_inv:.1f}")

    print("=" * 80)
    print()
    print("Advanced usage:")
    print(f"Problem solved in {solver.wall_time():d} milliseconds")
    print(f"Problem solved in {solver.iterations():d} iterations")


if __name__ == "__main__":
    init.CppBridge.init_logging("complex_mrp_or_tools.py")
    cpp_flags = init.CppFlags()
    cpp_flags.stderrthreshold = True
    cpp_flags.log_prefix = False
    init.CppBridge.set_flags(cpp_flags)
    main()
