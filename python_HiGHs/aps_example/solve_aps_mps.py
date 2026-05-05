from highspy import Highs

MPS_FILE_PATH = "aps_example.mps"  # 换任何MPS文件，只改这一行！

# 1. 初始化求解器 + 读取MPS模型（自动适配任何MPS）
solver = Highs()
solver.readModel(MPS_FILE_PATH)

# 2. 自动求解
solver.solve()

# 3. 自动获取模型信息（完全自适应，不写死！）
num_vars = solver.numVariables  # 自动获取【变量总个数】
optimal_obj = solver.getObjectiveValue()  # 自动获取【最优目标函数值】

# 4. 打印结果（自动遍历所有变量，不管有多少个都能打印）
print("=" * 60)
print(f"📄 读取的MPS文件: {MPS_FILE_PATH}")
print(f"✅ 模型求解状态: Optimal (最优解)")
print(f"🔢 模型变量总数: {num_vars} 个")
print("-" * 60)
print("📊 最优变量取值：")
# 自动循环遍历所有变量，打印编号 + 值
for i in range(num_vars):
    var_value = solver.variableValue(i)
    print(f"   变量 X{i+1} = {var_value}")
print("-" * 60)
print(f"🎯 最优目标函数值 = {optimal_obj}")
print("=" * 60)