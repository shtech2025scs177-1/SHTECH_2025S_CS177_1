import os
import sys

dir_now = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(dir_now)
dir_module = os.path.join(project_dir, 'module')
dir_code = os.path.join(project_dir, 'code')
dir_data = os.path.join(project_dir, 'data')

sys.path.append(dir_module)

import pandas as pd

sl_data_filename = 'SLKB_rawSL.csv'
gene_set_dataset_filename = 'gene_set.csv'

sl_data_path = os.path.join(dir_data, sl_data_filename)
gene_set_dataset_path = os.path.join(dir_data, gene_set_dataset_filename)

SL_data = pd.read_csv(sl_data_path, dtype = \
    {"gene_pair": 'string', 
     "study_origin": int, 
     "cell_line_origin": 'string', 
     "gene_1": 'string', 
     "gene_2": 'string', 
     "SL_or_not": 'string', 
     "SL_score": float, 
     "statistical_score": float, 
     "SL_score_cutoff": float, 
     "statistical_score_cutoff": float}
    )

gene_set = set()

gene_set.update(SL_data['gene_1'])
gene_set.update(SL_data['gene_2'])

print('Gene Set Length:', len(gene_set))

gene_list = list(gene_set)

gene_list = sorted(gene_list)

gene_df = pd.DataFrame(gene_list, columns = ['gene_symbol'], dtype = 'string')

gene_df.to_csv(gene_set_dataset_path, index=False)