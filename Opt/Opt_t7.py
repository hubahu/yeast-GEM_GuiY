# -*- coding: utf-8 -*-
"""yeast9_mva_knockout.py
Predict gene knockout targets to improve mevalonate (MVA) production in S. cerevisiae using yeast9 model.
"""
from cobra.io import read_sbml_model, load_json_model
from cobra.flux_analysis import single_gene_deletion
import pandas as pd
import matplotlib.pyplot as plt
import os

# ----------------------------
# STEP 1: 加载酵母9代谢模型
# ----------------------------
# 模型文件路径（根据实际存放位置修改）
#Model_path = r"D:\22_CodeProjects\yeast-GEM_GuiY\model\yeast-GEM.xml"
Model_path = r"E:\22_CodeProjects\yeast-GEM_GuiY\model\yeast-GEM.xml"
model = read_sbml_model(Model_path)
print(f"模型加载成功: {len(model.genes)}个基因, {len(model.reactions)}个反应")


# ----------------------------
# STEP 2: 检查/添加MVA合成路径
# ----------------------------
# 检查是否已有MVA分泌反应
if "MVA_ex" not in model.reactions:
    # 添加MVA合成关键反应（若模型未内置）
    from cobra import Metabolite, Reaction
    
    # 代谢物
    mva = Metabolite("mevalonate_c", compartment="c")
    
    # 反应1: Acetyl-CoA → HMG-CoA (异源酶MvaE/S)
    hmg_synth = Reaction("MVA_synthase")
    hmg_synth.add_metabolites({
        model.metabolites.get_by_id("accoa_c"): -2,
        model.metabolites.get_by_id("acac_c"): 1,
        model.metabolites.get_by_id("coa_c"): 1,
        model.metabolites.get_by_id("h_c"): 1,
    })
    
    # 反应2: MVA分泌
    mva_ex = Reaction("MVA_ex")
    mva_ex.add_metabolites({mva: -1})
    mva_ex.lower_bound = -1000  # 允许分泌
    
    model.add_reactions([hmg_synth, mva_ex])
    print("已添加MVA合成路径")
else:
    print("检测到模型已内置MVA路径")

# 设置目标为MVA分泌
model.objective = "MVA_ex"

# ----------------------------
# STEP 3: 模拟基因敲除（酵母9基因ID）
# ----------------------------
# 靶点基因列表（根据酵母9的基因ID调整）
target_genes = [
    "YGR175C",  # ERG9 (角鲨烯合成酶)
    "YPL028W",  # ERG12 (MVA激酶)
    "YPL061W",  # ALD6 (乙醛脱氢酶)
    "YLR044C",  # PDC1 (丙酮酸脱羧酶)
    "YPL231W",  # FAS1 (脂肪酸合成)
]

# 单基因敲除分析
ko_results = single_gene_deletion(
    model, 
    gene_list=target_genes, 
    method="fba", 
    processes=4
)

# 转换为DataFrame并排序
df = pd.DataFrame.from_dict(ko_results, orient="index")
df.columns = ["growth", "mva_flux"]
df["mva_flux"] = df["mva_flux"].abs()  # 取绝对值
df.sort_values("mva_flux", ascending=False, inplace=True)

# ----------------------------
# STEP 4: 结果可视化
# ----------------------------
plt.figure(figsize=(10, 5))
plt.bar(df.index, df["mva_flux"], color="skyblue")
plt.axhline(y=model.slim_optimize(), color="r", linestyle="--", label="野生型")
plt.xlabel("敲除基因")
plt.ylabel("MVA通量 (mmol/gDW/h)")
plt.title("酵母9模型基因敲除对MVA产量的影响")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig("yeast9_mva_knockout.png", dpi=300)
plt.show()

# 输出关键靶点
print("\n推荐敲除靶点（MVA产量提升）:")
print(df.head())