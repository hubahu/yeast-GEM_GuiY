from cobra import io

# Load model
model = io.read_sbml_model(r"D:\22_CodeProjects\yeast-GEM\model\yeast-GEM.xml")  # adjust path as needed


for rxn in model.exchanges:
    if "biomass" in rxn.id.lower() or "biomass" in rxn.name.lower():
        print(f"{rxn.id}: {rxn.name}")


# print("Exchange reactions in the model:")
# for rxn in model.exchanges:
#     print(f"{rxn.id}: {rxn.name}")
