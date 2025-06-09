import os
import sys

dir_now = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(dir_now)
dir_module = os.path.join(project_dir, 'module')
dir_code = os.path.join(project_dir, 'code')
dir_data = os.path.join(project_dir, 'data')

sys.path.append(dir_module)

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com/"

import torch
import numpy as np
import pandas as pd
import pickle
import fire
import signal
import re

from transformers import AutoTokenizer, AutoModel

gene_rpkm_dataset_filename = 'CCLE_RNAseq_genes_rpkm_20180929.gct'
gene_set_dataset_filename = 'gene_set.csv'
cell_line_set_dataset_filename = 'cell_line_set.csv'
gene_expression_dataset_filename = 'gene_expression.csv'
gene_rpkm_dataset_path = os.path.join(dir_data, gene_rpkm_dataset_filename)
gene_set_dataset_path = os.path.join(dir_data, gene_set_dataset_filename)
cell_line_set_dataset_path = os.path.join(dir_data, cell_line_set_dataset_filename)
gene_expression_dataset_path = os.path.join(dir_data, gene_expression_dataset_filename)

gene_expression_df = pd.read_csv(gene_rpkm_dataset_path, sep = '\t', skiprows = 2)
gene_df = pd.read_csv(gene_set_dataset_path, dtype = {'gene_symbol': 'string'})
cell_line_df = pd.read_csv(cell_line_set_dataset_path, dtype = {'cell_line_origin': 'string', 'cell_line_gene_num': int})

row_restr = '^' + '$|^'.join(gene_df.loc[:, 'gene_symbol']) + '$'
# print(row_restr[0:30])

column_restr = '^Description|^' + '|^'.join(cell_line_df.loc[:, 'cell_line_origin'])
# print(column_restr)

gene_expression_df_output = \
gene_expression_df.loc[gene_expression_df.loc[:,'Description'].str.contains(row_restr, regex = True), 
                       gene_expression_df.columns.str.contains(column_restr, regex = True)]

gene_expression_df_output = gene_expression_df_output.drop_duplicates(subset='Description', keep='first')
gene_expression_df_output.columns = [col.split('_')[0] for col in gene_expression_df_output.columns]
gene_expression_df_output.set_index('Description', inplace=True)
gene_expression_df_output.to_csv(gene_expression_dataset_path, index_label='Description')

print(f'gene: {gene_expression_df_output.shape[0]}/{gene_df.shape[0]}')
print(f'cell line: {gene_expression_df_output.shape[1]}/{cell_line_df.shape[0]}')



# print(gene_expression_df.shape)
# print(gene_expression_df.iloc[0:5, 0:5])


with open(os.path.join(dir_data, 'temp.txt'), 'w') as f:
    original_stdout = sys.stdout
    sys.stdout = f
    print(gene_expression_df.loc[gene_expression_df.loc[:,'Description'].str.contains(r'^CKS1B$|^A3GALT2$|^AADAC$'), 
                       gene_expression_df.columns.str.contains(r'Description|K562|786O|RPE1|^.*$')])
    print(gene_expression_df.columns)
    sys.stdout = original_stdout
