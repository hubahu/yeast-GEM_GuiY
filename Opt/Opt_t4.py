# analyze_mva.py
from cobra.io import read_sbml_model
import pandas as pd

# 加载模型
Model_path = r"D:\22_CodeProjects\yeast-GEM_GuiY\model\yeast-GEM.xml"
model = read_sbml_model(Model_path)  # 修改为你的路径

# 搜索包含 "mva" 或 "mevalonate" 的反应
keywords = ["mva", "mevalonate"]
mva_related_reactions = [
    rxn for rxn in model.reactions
    if any(k in rxn.id.lower() or k in rxn.name.lower() for k in keywords)
]

# 打印相关反应信息
for rxn in mva_related_reactions:
    print(f"反应 ID: {rxn.id}")
    print(f"名称: {rxn.name}")
    print(f"反应式: {rxn.reaction}")
    print(f"相关基因: {[g.id for g in rxn.genes]}")
    print("=" * 40)
