import pandas as pd

# read dbid2name.csv
dbid2name = pd.read_csv('./data/dbid2name.csv')

# 读取 entity2id.txt 文件
entity2id = pd.read_csv('./data/entity2id.txt', sep='\t', header=None, names=['a', 'b'])

# 创建从 a 到 b 的索引
a_to_b_index = {int(k): int(v) for k, v in zip(entity2id['a'], entity2id['b']) if k != 'a' and v != 'b'}

# 创建基因名称到 ID 的映射字典，忽略大小写
symbol_to_id = dict(zip(dbid2name["name"], dbid2name["_id"]))

# 读取 SLKB_rawSL.csv 文件
sl_raw = pd.read_csv('./data/SLKB_rawSL.csv')

# 选择特定细胞系（例如 'K562' 'RPE1'）
cell_line = '22RV1'
sl_filtered = sl_raw[sl_raw['cell_line_origin'] == cell_line].copy()

# 重命名列以便后续处理
sl_filtered = sl_filtered.rename(columns={'gene_1': 'geneA_name', 'gene_2': 'geneB_name'})

# 转换基因名称为 ID
sl_filtered['geneA_ID'] = sl_filtered['geneA_name'].map(symbol_to_id)
sl_filtered['geneB_ID'] = sl_filtered['geneB_name'].map(symbol_to_id)

# 去除无法映射的行（NaN 值）
sl_filtered = sl_filtered.dropna(subset=['geneA_ID', 'geneB_ID'])

# 将 ID 转换为整数
sl_filtered['geneA_ID'] = sl_filtered['geneA_ID'].astype(int)
sl_filtered['geneB_ID'] = sl_filtered['geneB_ID'].astype(int)

# 通过 a_to_b_index 进行二次映射
sl_filtered['geneA_ID_mapped'] = sl_filtered['geneA_ID'].map(a_to_b_index)
sl_filtered['geneB_ID_mapped'] = sl_filtered['geneB_ID'].map(a_to_b_index)

# 将 ID 映射为整数，并去除无法映射的行（NaN 值）
sl_filtered = sl_filtered.dropna(subset=['geneA_ID_mapped', 'geneB_ID_mapped'])
sl_filtered['geneA_ID_mapped'] = sl_filtered['geneA_ID_mapped'].astype(int)
sl_filtered['geneB_ID_mapped'] = sl_filtered['geneB_ID_mapped'].astype(int)

# 转换 SL_or_not 列为 1 或 0
sl_filtered['label'] = sl_filtered['SL_or_not'].apply(lambda x: 1 if x == 'SL' else 0)

# 按 label 分组，1 在前，0 在后，并按 geneA_ID 升序排序
sl_filtered = sl_filtered.sort_values(by=['label', 'geneA_ID_mapped'], ascending=[False, True])

# 提取需要的列：geneA_ID, geneB_ID, label
output_data = sl_filtered[['geneA_ID_mapped', 'geneB_ID_mapped', 'label']]

print("a_to_b_index 的键值对数量:", len(a_to_b_index))
print("geneA_ID 中的唯一值数量:", sl_filtered['geneA_ID'].nunique())
print("geneB_ID 中的唯一值数量:", sl_filtered['geneB_ID'].nunique())

# 打印 symbol_to_id 的部分映射关系
print("symbol_to_id 映射关系示例:")
print(list(symbol_to_id.items())[:10])  # 打印前 10 个映射关系

# 打印 a_to_b_index 的部分映射关系
print("a_to_b_index 映射关系示例:")
print(list(a_to_b_index.items())[:10])  # 打印前 10 个映射关系

# 打印部分映射结果用于检查
print("原始 geneA_ID 和映射后的 geneA_ID_mapped 示例:")
print(sl_filtered[['geneA_ID', 'geneA_ID_mapped']].head(10))

print("原始 geneB_ID 和映射后的 geneB_ID_mapped 示例:")
print(sl_filtered[['geneB_ID', 'geneB_ID_mapped']].head(10))


# 计算正负样本数
positive_count = sl_filtered[sl_filtered['label'] == 1].shape[0]
negative_count = sl_filtered[sl_filtered['label'] == 0].shape[0]

# 构建输出文件名，包含细胞系名称和正负样本数
output_file = f'./data/sl_filtered_output_{cell_line}_pos{positive_count}_neg{negative_count}.txt'

# 输出为指定格式的 txt 文件
output_data.to_csv(output_file, sep='\t', index=False, header=False)

print(f"数据已保存到 {output_file}")