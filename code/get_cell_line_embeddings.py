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

gene_embeddings_dataset_filename = 'gene_embeddings.pkl'
gene_expression_dataset_filename = 'gene_expression.csv'
cell_embeddings_dataset_filename = 'cell_embeddings_genePT-w.pkl'
cell_line_set_dataset_filename = 'cell_line_set.csv'
gene_embeddings_dataset_path = os.path.join(dir_data, gene_embeddings_dataset_filename)
gene_expression_dataset_path = os.path.join(dir_data, gene_expression_dataset_filename)
cell_embeddings_dataset_path = os.path.join(dir_data, cell_embeddings_dataset_filename)
cell_line_set_dataset_path = os.path.join(dir_data, cell_line_set_dataset_filename)

gene_expression_df = pd.read_csv(gene_expression_dataset_path)
cell_line_df = pd.read_csv(cell_line_set_dataset_path, dtype = {'cell_line_origin': 'string', 'cell_line_gene_num': int})

with open(gene_embeddings_dataset_path, 'rb') as file:
    gene_embeddings:dict = pickle.load(file)
    
cell_embeddings_genePT_w = {}

default_embeddings = np.zeros_like(list(gene_embeddings.values())[0])

print('Dim embeddings: ', len(default_embeddings))

for cell_line in cell_line_df.loc[:, 'cell_line_origin']:
    cell_embeddings_genePT_w[cell_line] = default_embeddings

gene_expression_df.set_index('Description', inplace=True)

for column in gene_expression_df.columns[1:]:
    cell_embeddings_genePT_w[column] = default_embeddings
    
    for row in gene_expression_df.index:
        try:
            cell_embeddings_genePT_w[column] = cell_embeddings_genePT_w[column] + gene_expression_df.loc[row, column] * gene_embeddings[row]
        except:
            import pdb;pdb.set_trace()
            
    cell_embeddings_genePT_w[column] = cell_embeddings_genePT_w[column] / np.linalg.norm(cell_embeddings_genePT_w[column])
        
with open(cell_embeddings_dataset_path, 'wb') as file:
    pickle.dump(cell_embeddings_genePT_w, file)