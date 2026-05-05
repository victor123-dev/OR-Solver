"""
complex_aps_or_tools.py
=======================
企业级复杂 APS 案例：柔性车间调度问题（FJSP）
含序列相关换型时间（SDST）、发布日期、交货期与加权拖期惩罚

背景：某离散制造企业（如机械加工车间）接到 3 张工单，需要在 3 台机器上
      按工艺路线加工。每台机器在切换加工对象时需要换型时间，且每张工单
      都有最早可开工时间（发布日期）和客户要求的交货期。
      目标：在满足所有工艺约束和机器独占性约束的前提下，最小化加权拖期
      总成本，同时兼顾整体完工时间。

=== 问题数据 ===
工单（Jobs）：J1, J2, J3
机器（Machines）：M1, M2, M3
Big-M = 200

工单 J1：工序 O11 → O12
  O11 可选机器：M1（加工时长=4）, M2（加工时长=5）
  O12 可选机器：M2（加工时长=3）, M3（加工时长=4）
  发布日期 r1=0，交货期 d1=12，权重 w1=10

工单 J2：工序 O21 → O22
  O21 可选机器：M1（加工时长=3）, M3（加工时长=5）
  O22 可选机器：M1（加工时长=4）, M2（加工时长=4）
  发布日期 r2=2，交货期 d2=10，权重 w2=15

工单 J3：工序 O31（单工序）
  O31 可选机器：M2（加工时长=6）, M3（加工时长=5）
  发布日期 r3=4，交货期 d3=14，权重 w3=8

序列相关换型时间（SDST，所有机器相同）：
  J1→J2: 2,  J1→J3: 1
  J2→J1: 3,  J2→J3: 2
  J3→J1: 1,  J3→J2: 1

=== 目标函数 ===
Min  10·T1 + 15·T2 + 8·T3 + 0.1·Cmax
"""

from ortools.init.python import init
from ortools.linear_solver import pywraplp


# ============================================================
# 问题数据
# ============================================================
BIG_M = 200

# 加工时间 p[job][op][machine]，0 表示不可用
p = {
    (0, 0, 0): 4, (0, 0, 1): 5, (0, 0, 2): 0,
    (0, 1, 0): 0, (0, 1, 1): 3, (0, 1, 2): 4,
    (1, 0, 0): 3, (1, 0, 1): 0, (1, 0, 2): 5,
    (1, 1, 0): 4, (1, 1, 1): 4, (1, 1, 2): 0,
    (2, 0, 0): 0, (2, 0, 1): 6, (2, 0, 2): 5,
}

r = [0, 2, 4]    # 发布日期
d = [12, 10, 14] # 交货期
w = [10, 15, 8]  # 拖期权重

sdst = {
    (0, 1): 2, (0, 2): 1,
    (1, 0): 3, (1, 2): 2,
    (2, 0): 1, (2, 1): 1,
}

# 工单结构：jobs[i] = [(op_index, [eligible_machines]), ...]
jobs = [
    [(0, [0, 1]), (1, [1, 2])],
    [(0, [0, 2]), (1, [0, 1])],
    [(0, [1, 2])],
]

# 每台机器上可能出现的操作：(job_i, op_l, x_var_name, s_var_name, proc_time_on_k)
machine_ops = {
    0: [(0, 0, 'X11M1', 'S11', p[(0,0,0)]),
        (1, 0, 'X21M1', 'S21', p[(1,0,0)]),
        (1, 1, 'X22M1', 'S22', p[(1,1,0)])],
    1: [(0, 0, 'X11M2', 'S11', p[(0,0,1)]),
        (0, 1, 'X12M2', 'S12', p[(0,1,1)]),
        (1, 1, 'X22M2', 'S22', p[(1,1,1)]),
        (2, 0, 'X31M2', 'S31', p[(2,0,1)])],
    2: [(0, 1, 'X12M3', 'S12', p[(0,1,2)]),
        (1, 0, 'X21M3', 'S21', p[(1,0,2)]),
        (2, 0, 'X31M3', 'S31', p[(2,0,2)])],
}


def main():
    print("Google OR-Tools version:", init.OrToolsVersion.version_string())

    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        print("Could not create solver SCIP"); return

    inf = solver.infinity()

    # ============================================================
    # 决策变量
    # ============================================================
    # 机器分配变量（二进制）
    X = {}
    for i, job_ops in enumerate(jobs):
        for l, (_, machines) in enumerate(job_ops):
            for k in machines:
                name = f'X{i+1}{l+1}M{k+1}'
                X[(i, l, k)] = solver.IntVar(0, 1, name)

    # 工序开始时间（连续）
    S = {}
    for i, job_ops in enumerate(jobs):
        for l in range(len(job_ops)):
            name = f'S{i+1}{l+1}'
            S[(i, l)] = solver.NumVar(0, inf, name)

    # 拖期变量（连续，>= 0）
    T = [solver.NumVar(0, inf, f'T{i+1}') for i in range(3)]

    # Makespan（连续）
    Cmax = solver.NumVar(0, inf, 'CMAX')

    # 机器排序变量（二进制）
    Y = {}
    disj_pairs = []
    dc = 0
    for k, ops in machine_ops.items():
        for ai in range(len(ops)):
            for bi in range(ai + 1, len(ops)):
                jA, lA, xnA, snA, pAk = ops[ai]
                jB, lB, xnB, snB, pBk = ops[bi]
                if jA == jB:
                    continue
                yAB = solver.IntVar(0, 1, f'Y{jA+1}{jB+1}M{k+1}_{dc}')
                yBA = solver.IntVar(0, 1, f'Y{jB+1}{jA+1}M{k+1}_{dc}')
                Y[(jA, jB, k, dc)] = yAB
                Y[(jB, jA, k, dc)] = yBA
                disj_pairs.append((k, jA, lA, xnA, snA, pAk,
                                      jB, lB, xnB, snB, pBk,
                                      yAB, yBA, dc))
                dc += 1

    print(f"Number of variables = {solver.NumVariables()}")

    # ============================================================
    # 约束条件
    # ============================================================

    # (1) 机器分配约束：每道工序恰好分配到一台机器
    for i, job_ops in enumerate(jobs):
        for l, (_, machines) in enumerate(job_ops):
            ct = solver.Constraint(1, 1, f'ASGN{i+1}{l+1}')
            for k in machines:
                ct.SetCoefficient(X[(i, l, k)], 1)

    # (2) 发布日期约束：第一道工序的开始时间 >= 发布日期
    for i in range(3):
        ct = solver.Constraint(float(r[i]), inf, f'REL{i+1}')
        ct.SetCoefficient(S[(i, 0)], 1)

    # (3) 工序先后顺序约束（工艺路线）
    # s_{i,l+1} >= s_{i,l} + sum_k(p[i,l,k] * X[i,l,k])
    # => s_{i,l} - s_{i,l+1} + sum_k(p[i,l,k]*X[i,l,k]) <= 0
    for i, job_ops in enumerate(jobs):
        for l in range(len(job_ops) - 1):
            _, machines = job_ops[l]
            ct = solver.Constraint(-inf, 0, f'PREC{i+1}{l+1}')
            ct.SetCoefficient(S[(i, l)], 1)
            ct.SetCoefficient(S[(i, l + 1)], -1)
            for k in machines:
                ct.SetCoefficient(X[(i, l, k)], float(p[(i, l, k)]))

    # (4) 析取约束（含 SDST）
    # A 在 B 之前：s_B - s_A - M*yAB - M*xA - M*xB >= p_Ak + sdst[jA->jB] - 2M
    # => s_A - s_B - M*yAB - M*xA - M*xB <= -(p_Ak + sdst[jA->jB]) - M
    # B 在 A 之前：s_A - s_B - M*yBA - M*xA - M*xB <= -(p_Bk + sdst[jB->jA]) - M
    # 排序完整性：yAB + yBA >= xA + xB - 1
    # 排序互斥：yAB + yBA <= 1
    for (k, jA, lA, xnA, snA, pAk,
            jB, lB, xnB, snB, pBk,
            yAB, yBA, dc) in disj_pairs:

        xA = X[(jA, lA, k)]
        xB = X[(jB, lB, k)]
        sA = S[(jA, lA)]
        sB = S[(jB, lB)]
        sdst_AB = sdst.get((jA, jB), 0)
        sdst_BA = sdst.get((jB, jA), 0)

        # 排序完整性
        ct1 = solver.Constraint(-1, inf, f'ORD1_{dc}')
        ct1.SetCoefficient(yAB, 1); ct1.SetCoefficient(yBA, 1)
        ct1.SetCoefficient(xA, -1); ct1.SetCoefficient(xB, -1)

        # 排序互斥
        ct2 = solver.Constraint(-inf, 1, f'ORD2_{dc}')
        ct2.SetCoefficient(yAB, 1); ct2.SetCoefficient(yBA, 1)

        # A 在 B 之前
        rhs_AB = -(pAk + sdst_AB) - BIG_M
        ct3 = solver.Constraint(-inf, float(rhs_AB), f'DSJAB_{dc}')
        ct3.SetCoefficient(sA,  1); ct3.SetCoefficient(sB, -1)
        ct3.SetCoefficient(yAB, -BIG_M)
        ct3.SetCoefficient(xA,  -BIG_M); ct3.SetCoefficient(xB, -BIG_M)

        # B 在 A 之前
        rhs_BA = -(pBk + sdst_BA) - BIG_M
        ct4 = solver.Constraint(-inf, float(rhs_BA), f'DSJBA_{dc}')
        ct4.SetCoefficient(sB,  1); ct4.SetCoefficient(sA, -1)
        ct4.SetCoefficient(yBA, -BIG_M)
        ct4.SetCoefficient(xA,  -BIG_M); ct4.SetCoefficient(xB, -BIG_M)

    # (5) 拖期约束：T_i >= C_i_last - d_i
    # => s_i_last + sum_k(p_i_last_k * X_i_last_k) - T_i <= d_i
    last_ops = [(1, [1, 2]), (1, [0, 1]), (0, [1, 2])]  # (last_op_l, eligible_machines)
    for i, (ll, machines) in enumerate(last_ops):
        ct = solver.Constraint(-inf, float(d[i]), f'TARD{i+1}')
        ct.SetCoefficient(S[(i, ll)], 1)
        ct.SetCoefficient(T[i], -1)
        for k in machines:
            ct.SetCoefficient(X[(i, ll, k)], float(p[(i, ll, k)]))

    # (6) Makespan 约束：Cmax >= C_i_last
    for i, (ll, machines) in enumerate(last_ops):
        ct = solver.Constraint(-inf, 0, f'MKSP{i+1}')
        ct.SetCoefficient(S[(i, ll)], 1)
        ct.SetCoefficient(Cmax, -1)
        for k in machines:
            ct.SetCoefficient(X[(i, ll, k)], float(p[(i, ll, k)]))

    print(f"Number of constraints = {solver.NumConstraints()}")

    # ============================================================
    # 目标函数：Min 10·T1 + 15·T2 + 8·T3 + 0.1·Cmax
    # ============================================================
    objective = solver.Objective()
    for i in range(3):
        objective.SetCoefficient(T[i], float(w[i]))
    objective.SetCoefficient(Cmax, 0.1)
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
    print("=" * 70)
    print("  复杂 APS 柔性车间排程（FJSP）—— 最优解")
    print("=" * 70)
    print(f"  目标函数值（加权拖期 + 0.1×Cmax） = {objective.Value():.2f}")
    print(f"  最大完工时间 Cmax = {Cmax.solution_value():.1f}")
    print()

    # 机器分配结果
    print("  【机器分配方案】")
    op_names = {(0,0):'O11', (0,1):'O12', (1,0):'O21', (1,1):'O22', (2,0):'O31'}
    machine_names = {0:'M1', 1:'M2', 2:'M3'}
    for i, job_ops in enumerate(jobs):
        for l, (_, machines) in enumerate(job_ops):
            for k in machines:
                if X[(i, l, k)].solution_value() > 0.5:
                    op = op_names[(i, l)]
                    mk = machine_names[k]
                    st = S[(i, l)].solution_value()
                    pt = p[(i, l, k)]
                    print(f"    {op} → {mk}  开始={st:.1f}  结束={st+pt:.1f}  加工时长={pt}")

    print()
    print("  【甘特图时间轴（按机器）】")
    for k in range(3):
        mk = machine_names[k]
        schedule = []
        for jj, lj, xn, sn, ptk in machine_ops[k]:
            xvar = X.get((jj, lj, k))
            if xvar and xvar.solution_value() > 0.5:
                st = S[(jj, lj)].solution_value()
                job_name = f'J{jj+1}'
                op_name = op_names[(jj, lj)]
                schedule.append((st, st + ptk, job_name, op_name))
        schedule.sort()
        if schedule:
            print(f"    {mk}: " + "  ".join(
                f"[{s:.0f},{e:.0f}]{jn}({on})" for s, e, jn, on in schedule))

    print()
    print("  【拖期与交货期分析】")
    job_names_list = ['J1', 'J2', 'J3']
    for i in range(3):
        ll, machines = last_ops[i]
        completion = S[(i, ll)].solution_value() + sum(
            p[(i, ll, k)] * X[(i, ll, k)].solution_value() for k in machines)
        tard = T[i].solution_value()
        status_str = f"拖期 {tard:.1f}" if tard > 1e-6 else "按时完成"
        print(f"    {job_names_list[i]}: 完工时间={completion:.1f}  交货期={d[i]}  {status_str}  "
              f"拖期惩罚={w[i]}×{tard:.1f}={w[i]*tard:.1f}")

    print()
    print("  【换型时间说明】")
    for (k, jA, lA, xnA, snA, pAk,
            jB, lB, xnB, snB, pBk,
            yAB, yBA, dc) in disj_pairs:
        xA = X[(jA, lA, k)]; xB = X[(jB, lB, k)]
        if xA.solution_value() > 0.5 and xB.solution_value() > 0.5:
            mk = machine_names[k]
            if yAB.solution_value() > 0.5:
                s_val = sdst.get((jA, jB), 0)
                print(f"    {mk}: J{jA+1}→J{jB+1} 换型时间={s_val}")
            elif yBA.solution_value() > 0.5:
                s_val = sdst.get((jB, jA), 0)
                print(f"    {mk}: J{jB+1}→J{jA+1} 换型时间={s_val}")

    print("=" * 70)
    print()
    print("Advanced usage:")
    print(f"Problem solved in {solver.wall_time():d} milliseconds")
    print(f"Problem solved in {solver.iterations():d} iterations")


if __name__ == "__main__":
    init.CppBridge.init_logging("complex_aps_or_tools.py")
    cpp_flags = init.CppFlags()
    cpp_flags.stderrthreshold = True
    cpp_flags.log_prefix = False
    init.CppBridge.set_flags(cpp_flags)
    main()
