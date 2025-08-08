"""
查照关键字的相关反应
"""

from cobra.io import read_sbml_model
from collections import defaultdict
import pandas as pd



def find_keyword_related_components(model, keywords, case_sensitive=False):
    """
    查找模型中与关键字相关的反应和代谢物
    
    参数:
        model: 加载的COBRA模型对象
        keywords: 字符串或字符串列表，要搜索的关键字
        case_sensitive: 是否区分大小写
        
    返回:
        dict: 包含反应和代谢物信息的字典
    """
    if isinstance(keywords, str):
        keywords = [keywords]
    
    # 初始化结果存储
    results = {
        'search_keywords': keywords,
        'reactions': defaultdict(list),
        'metabolites': defaultdict(list),
        'summary': {}
    }
    
    # 设置匹配函数
    def is_match(text):
        text = str(text)
        if not case_sensitive:
            text = text.lower()
            kw_list = [kw.lower() for kw in keywords]
        else:
            kw_list = keywords
        return any(kw in text for kw in kw_list)
    
    # 搜索代谢物
    for met in model.metabolites:
        fields_to_check = {
            'id': met.id,
            'name': met.name,
            'formula': met.formula,
            'compartment': met.compartment
        }
        
        for field, value in fields_to_check.items():
            if value and is_match(value):
                results['metabolites'][met.id].append({
                    'field': field,
                    'value': value,
                    'compartment': met.compartment
                })
    
    # 搜索反应
    for rxn in model.reactions:
        # 检查反应ID和名称
        fields_checked = {}
        if is_match(rxn.id):
            fields_checked['id'] = rxn.id
        if rxn.name and is_match(rxn.name):
            fields_checked['name'] = rxn.name
        
        # 检查反应方程式中的代谢物
        met_matches = []
        for met in rxn.metabolites:
            if is_match(met.id) or (met.name and is_match(met.name)):
                met_matches.append({
                    'metabolite_id': met.id,
                    'metabolite_name': met.name,
                    'coefficient': rxn.metabolites[met]
                })
        
        # 如果有匹配则记录
        if fields_checked or met_matches:
            results['reactions'][rxn.id] = {
                'name': rxn.name,
                'matches': fields_checked,
                'metabolite_matches': met_matches,
                'reaction_string': rxn.build_reaction_string(),
                'subsystem': rxn.subsystem,
                'lower_bound': rxn.lower_bound,
                'upper_bound': rxn.upper_bound
            }
    
    # 生成摘要统计
    results['summary'] = {
        'Reaction ID': rxn.id,
        'Name': rxn.name,
        'total_reactions_matched': len(results['reactions']),
        'total_metabolites_matched': len(results['metabolites']),
        'matched_reaction_ids': list(results['reactions'].keys()),
        'matched_metabolite_ids': list(results['metabolites'].keys())
    }
    
    return results

# def save_results(results, output_prefix):
#     """
#     将结果保存到Excel和文本文件
#     """
#     # 保存为Excel
#     with pd.ExcelWriter(f"{output_prefix}_results.xlsx") as writer:
#         # 反应数据
#         reactions_data = []
#         for rxn_id, data in results['reactions'].items():
#             reactions_data.append({
#                 
#                 'Name': data['name'],
#                 'Matched Fields': ', '.join(data['matches'].keys()),
#                 'Subsystem': data['subsystem'],
#                 'Reaction': data['reaction_string'],
#                 'Bounds': f"{data['lower_bound']} to {data['upper_bound']}"
#             })
#         pd.DataFrame(reactions_data).to_excel(writer, sheet_name='Reactions', index=False)
        
#         # 代谢物数据
#         metabolites_data = []
#         for met_id, matches in results['metabolites'].items():
#             for match in matches:
#                 metabolites_data.append({
#                     'Metabolite ID': met_id,
#                     'Compartment': match['compartment'],
#                     'Matched Field': match['field'],
#                     'Matched Value': match['value']
#                 })
#         pd.DataFrame(metabolites_data).to_excel(writer, sheet_name='Metabolites', index=False)
    
#     # 保存为文本报告
#     with open(f"{output_prefix}_report.txt", "w") as f:
#         f.write(f"Keyword Search Report\n{'='*30}\n")
#         f.write(f"Search Keywords: {', '.join(results['search_keywords'])}\n\n")
        
#         f.write(f"Summary:\n")
#         f.write(f"- Matched Reactions: {results['summary']['total_reactions_matched']}\n")
#         f.write(f"- Matched Metabolites: {results['summary']['total_metabolites_matched']}\n\n")
        
#         f.write("Matched Reactions:\n")
#         for rxn_id, data in results['reactions'].items():
#             f.write(f"\n{rxn_id} ({data['name']})\n")
#             f.write(f"Subsystem: {data['subsystem']}\n")
#             f.write(f"Reaction: {data['reaction_string']}\n")
#             if data['matches']:
#                 f.write(f"Matched in: {', '.join(data['matches'].keys())}\n")
#             if data['metabolite_matches']:
#                 f.write("Matching Metabolites:\n")
#                 for met in data['metabolite_matches']:
#                     f.write(f"  {met['metabolite_id']} ({met['metabolite_name']}): {met['coefficient']}\n")
        
#         f.write("\n\nMatched Metabolites:\n")
#         for met_id, matches in results['metabolites'].items():
#             f.write(f"\n{met_id}\n")
#             for match in matches:
#                 f.write(f"  {match['field']}: {match['value']} (compartment: {match['compartment']})\n")

def print_results(results):
    """在控制台格式化输出结果"""
    print("\n" + "="*50)
    print(f" 搜索结果 (关键词: {', '.join(results['search_keywords'])})")
    print("="*50)
    
    # 输出代谢物结果
    print("\n匹配的代谢物:")
    if not results['metabolites']:
        print("  (无)")
    else:
        for met_id, matches in results['metabolites'].items():
            for match in matches:
                print(f"  - {met_id} ({match['value']}) [区室: {match['compartment']}]")
    
    # 输出反应结果
    print("\n匹配的反应:")
    if not results['reactions']:
        print("  (无)")
    else:
        for rxn_id, data in results['reactions'].items():
            print(f"\n■ {rxn_id} ({data['name']})")
            print(f"  亚系统: {data['subsystem']}")
            print(f"  反应式: {data['reaction_string']}")
            
            if data['match_fields']:
                print("  匹配字段:")
                for field in data['match_fields']:
                    print(f"    - {field}")
            
            if data['metabolite_matches']:
                print("  相关代谢物:")
                for met in data['metabolite_matches']:
                    coeff = f"{met['coeff']:+}" if met['coeff'] != 1 else ""
                    print(f"    - {met['id']} ({met['name']}) {coeff}")

if __name__ == "__main__":

    # 配置参数
    MODEL_PATH = r"D:\22_CodeProjects\yeast-GEM_GuiY\model\yeast-GEM.xml"  # 修改为你的模型路径
    SEARCH_KEYWORDS = ["coa", "acetyl"]  # 可以修改为任何你想搜索的关键词
    # OUTPUT_PREFIX = "coa_search"  # 输出文件前缀
    
    # 加载模型
    print(f"Loading model from {MODEL_PATH}...")
    model = read_sbml_model(MODEL_PATH)
    print(f"Model loaded: {len(model.reactions)} reactions, {len(model.metabolites)} metabolites")
    
    # # 执行搜索
    # print(f"\nSearching for keywords: {', '.join(SEARCH_KEYWORDS)}")
    # results = find_keyword_related_components(model, SEARCH_KEYWORDS, case_sensitive=False)
    
    # # 保存结果
    # print(f"\nFound {results['summary']['total_reactions_matched']} reactions and {results['summary']['total_metabolites_matched']} metabolites matching the keywords.")
    # # print("\nSaving results...")
    # save_results(results, OUTPUT_PREFIX)
    # print(f"Results saved to {OUTPUT_PREFIX}_results.xlsx and {OUTPUT_PREFIX}_report.txt")
    
    # 打印摘要
    # print("\nSearch Summary:")
    # print(f"- Matched reactions: {results['summary']['total_reactions_matched']}")
    # print(f"- Matched metabolites: {results['summary']['total_metabolites_matched']}")
    # print("\nTop 5 matched reactions:")
    # for rxn_id in list(results['reactions'].keys())[:5]:
    #     print(f"  {rxn_id}: {results['reactions'][rxn_id]['name']}")

    # 执行搜索
    print(f"\n正在搜索关键词: {', '.join(SEARCH_KEYWORDS)}")
    results = find_keyword_related_components(model, SEARCH_KEYWORDS, case_sensitive=False)
    
    # 输出结果
    print_results(results)
    print("\n搜索完成!")