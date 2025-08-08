'''
加载 yeast-GEM 模型
设置 MVA 输出反应为目标函数
保持 80% 生长作为约束
执行 optknock 分析以找出一组可行的基因敲除
输出敲除组合及对 MVA 的提升预测
'''

from cobra.io import read_sbml_model
from cobra.flux_analysis import pfba
from itertools import combinations
import pandas as pd

# Step 1: 加载模型
Model_path = r"D:\22_CodeProjects\yeast-GEM_GuiY\model\yeast-GEM.xml"
model = read_sbml_model(Model_path)  # 路径根据你文件位置调整

# Step 2: 查找 MVA 的胞外输出反应
mva_met = next((m for m in model.metabolites 
                if "mevalonate" in m.name.lower() and m.compartment == "c"), None)
if not mva_met:
    raise Exception("找不到胞质中的 mevalonate")

mva_export_rxn = None
for rxn in model.reactions:
    if mva_met in rxn.metabolites and "->" in rxn.reaction and mva_met in rxn.products:
        mva_export_rxn = rxn
        break
if not mva_export_rxn:
    raise Exception("未找到 MVA 输出反应")

# Step 3: 设置最大生长速率
biomass_rxn = model.reactions.get_by_id("r_2111")  # 通常是 biomass
max_growth = pfba(model).fluxes[biomass_rxn.id]
biomass_rxn.lower_bound = 0.8 * max_growth
print(f"生长下限设置为 {0.8 * max_growth:.4f} mmol/gDW/h")

# Step 4: 筛选可敲除的基因相关反应（可选步骤）
# 这里简化处理，选择所有非必需且非生物质相关的反应作为候选
candidate_reactions = [rxn.id for rxn in model.reactions 
                      if rxn.id != biomass_rxn.id 
                      and not rxn.id.startswith(('EX_', 'DM_', 'sink_'))]

print(f"候选敲除反应数量: {len(candidate_reactions)}")

# 限制候选反应数量以避免组合爆炸
if len(candidate_reactions) > 100:
    import random
    candidate_reactions = random.sample(candidate_reactions, 100)

# Step 5: 简单的 OptKnock 实现（尝试有限组合）
results = []
max_knockouts = 3
top_n = 10  # 保存前10个最佳结果

# 评估所有可能的单敲除
for knockout in candidate_reactions:
    with model:
        model.reactions.get_by_id(knockout).knock_out()
        try:
            growth = pfba(model).fluxes[biomass_rxn.id]
            production = pfba(model).fluxes[mva_export_rxn.id]
            results.append({
                "knockouts": [knockout],
                "fitness": production,
                "biomass": growth,
                "production": production
            })
        except:
            continue

# 评估双敲除组合（如果候选反应不太多）
if len(candidate_reactions) <= 50:
    for knockout1, knockout2 in combinations(candidate_reactions, 2):
        with model:
            model.reactions.get_by_id(knockout1).knock_out()
            model.reactions.get_by_id(knockout2).knock_out()
            try:
                growth = pfba(model).fluxes[biomass_rxn.id]
                production = pfba(model).fluxes[mva_export_rxn.id]
                results.append({
                    "knockouts": [knockout1, knockout2],
                    "fitness": production,
                    "biomass": growth,
                    "production": production
                })
            except:
                continue

# 评估三敲除组合（如果候选反应很少）
if len(candidate_reactions) <= 20:
    for knockout_combo in combinations(candidate_reactions, 3):
        with model:
            for ko in knockout_combo:
                model.reactions.get_by_id(ko).knock_out()
            try:
                growth = pfba(model).fluxes[biomass_rxn.id]
                production = pfba(model).fluxes[mva_export_rxn.id]
                results.append({
                    "knockouts": list(knockout_combo),
                    "fitness": production,
                    "biomass": growth,
                    "production": production
                })
            except:
                continue

# Step 6: 分析结果
if results:
    df = pd.DataFrame(results)
    df = df.sort_values("fitness", ascending=False).head(top_n)
    print("最佳基因敲除组合：")
    print(df[["knockouts", "fitness", "biomass", "production"]])
else:
    print("没有找到可行的敲除组合")
