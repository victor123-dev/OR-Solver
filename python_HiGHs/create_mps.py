from highspy import Highs, ObjSense, HighsVarType, kHighsInf

# 1. 初始化HiGHS求解器
solver = Highs()
solver.silent(True)  # 关闭控制台输出

# 2. 添加变量（x1, x2，下界0，上界无穷，目标系数分别为3、4）
x1 = solver.addVariable(lb=0, ub=kHighsInf, obj=3.0, name="X1")
x2 = solver.addVariable(lb=0, ub=kHighsInf, obj=4.0, name="X2")

# 3. 定义线性约束
# 约束1: x1 + 2x2 ≤ 14 → 下界=-∞，上界=14
expr1 = x1 + 2 * x2
expr1.bounds = (-kHighsInf, 14.0)
con1 = solver.addConstr(expr1, name="CON1")

# 约束2: 3x1 - x2 ≥ 0 → 下界=0，上界=+∞
expr2 = 3 * x1 - x2
expr2.bounds = (0.0, kHighsInf)
con2 = solver.addConstr(expr2, name="CON2")

# 约束3: x1 - x2 ≤ 2 → 下界=-∞，上界=2
expr3 = x1 - x2
expr3.bounds = (-kHighsInf, 2.0)
con3 = solver.addConstr(expr3, name="CON3")

# 4. 设置目标为最大化
solver.setObjective(sense=ObjSense.kMaximize)

# 导出MPS文件
solver.writeModel("lp_example_generated.mps")

print("MPS文件生成成功！")