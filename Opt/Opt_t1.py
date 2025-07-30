from cobra import io

# Load model
model = io.read_sbml_model(r"D:\22_CodeProjects\yeast-GEM\model\yeast-GEM.xml")  # adjust path as needed

# Check biomass objective value
solution = model.optimize()
print("Default biomass objective:", solution.objective_value)

# Change objective: Ethanol production (check actual reaction ID first!)
model.objective = "r_1761"
solution = model.optimize()
print("Max ethanol production:", solution.objective_value)

# Optional: Knock out a gene
gene = model.genes.get_by_id("YGR192C")  # example gene
gene.knock_out()
solution = model.optimize()
print("Objective after knockout:", solution.objective_value)

