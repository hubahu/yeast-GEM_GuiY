from cobra import io
from cobra.flux_analysis import single_gene_deletion
from itertools import combinations

# 1. 载入模型
model = io.read_sbml_model(r"D:\22_CodeProjects\yeast-GEM\model\yeast-GEM.xml")

# 2. 设置目标函数为 MVA 外排反应
model.objective = "EX_mev__L(e)"  # 请替换为你模型中的实际ID

# 3. 添加最小生长约束（例如细胞生长至少为80%最大）
biomass_rxn = model.reactions.get_by_id("r_2111")  # 假设是生长反应，请确认实际ID
solution = model.optimize()
min_growth = 0.8 * solution.fluxes[biomass_rxn.id]
biomass_rxn.lower_bound = min_growth

print(f"Minimum growth rate required: {min_growth:.4f}")

# 4. 查找参与 MVA 产物的所有反应（粗筛）
mva_rxn = model.reactions.get_by_id("EX_mev__L(e)")  # 替换为实际 ID
precursors = mva_rxn.reactants

related_rxns = set()
for met in precursors:
    related_rxns.update(met.reactions)

# 5. 找出涉及这些反应的基因
related_genes = set()
for rxn in related_rxns:
    related_genes.update(rxn.genes)

print(f"\nGenes possibly related to MVA pathway: {[g.id for g in related_genes]}\n")

# 6. 对每个基因做敲除模拟，评估 MVA 产量与生长率
results = []
for gene in related_genes:
    model_temp = model.copy()
    model_temp.genes.get_by_id(gene.id).knock_out()
    sol = model_temp.optimize()
    results.append((gene.id, sol.objective_value, sol.fluxes[biomass_rxn.id] if sol.status == 'optimal' else 0.0))

# 7. 打印结果
print("Gene\tMVA\tGrowth")
for gene, mva, growth in results:
    print(f"{gene}\t{mva:.4f}\t{growth:.4f}")
