
'''
载入模型
识别 Mevalonate (MVA) 的输出反应
以 80% 生长速率为约束优化 MVA 产量
执行所有基因的单敲除分析
筛选出提升 MVA 的有效敲除候选基因
'''

from cobra.io import read_sbml_model
from cobra.flux_analysis import pfba, single_gene_deletion

# 加载 yeast-GEM 模型
Model_path = r"D:\22_CodeProjects\yeast-GEM_GuiY\model\yeast-GEM.xml"
model = read_sbml_model(Model_path)  # 路径根据你文件位置调整

# 设置目标产物 MVA 的代谢物对象
mva_met = next((m for m in model.metabolites if "mevalonate" in m.name.lower() and m.compartment == "c"), None)
if not mva_met:
    raise Exception("未找到胞质中的 mevalonate")

# 找出 MVA 输出反应（从胞内 -> 胞外）
mva_export_rxn = None
for rxn in model.reactions:
    if mva_met in rxn.metabolites and "->" in rxn.reaction and mva_met in rxn.products:
        mva_export_rxn = rxn
        break
if not mva_export_rxn:
    raise Exception("未找到 mevalonate 的输出反应")

# 保存原始目标函数
original_obj = model.objective

# 获取最大生长速率
model.objective = "r_2111"  # 通常是 biomass reaction，实际名称可根据模型确认
max_growth = model.optimize().objective_value
print(f"最大生长速率: {max_growth:.4f}")

# 设置最低生长约束为 80%
model.reactions.get_by_id("r_2111").lower_bound = 0.8 * max_growth

# 设置目标为 MVA 输出
model.objective = mva_export_rxn

# 获取当前最优 MVA 输出速率
solution = pfba(model)
baseline_mva_flux = solution.fluxes[mva_export_rxn.id]
print(f"原始 MVA 输出通量: {baseline_mva_flux:.4f}")

# 执行单基因敲除分析
print("正在执行单基因敲除分析，请稍等...")
result = single_gene_deletion(model)

# 提取潜在有效基因敲除（MVA 提升 >5%，生长保持 ≥80%）
threshold = 0.05
result["mva_flux"] = result["flux"]
valid = result[
    (result["growth"] >= 0.8 * max_growth * 0.99) &
    (result["mva_flux"] > baseline_mva_flux * (1 + threshold))
]

# 输出结果
print("\n潜在提升 MVA 的敲除基因：")
print(valid[["ids", "growth", "mva_flux"]].sort_values(by="mva_flux", ascending=False))
