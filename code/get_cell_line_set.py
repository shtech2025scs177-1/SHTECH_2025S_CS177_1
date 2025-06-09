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
cell_line_set_dataset_filename = 'cell_line_set.csv'

sl_data_path = os.path.join(dir_data, sl_data_filename)
cell_line_set_dataset_path = os.path.join(dir_data, cell_line_set_dataset_filename)

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

cell_line_dict = {}

for cell_line in SL_data['cell_line_origin']:
    cell_line_dict[cell_line] = cell_line_dict.get(cell_line, 0) + 1
    
print('Cell line Length:', len(cell_line_dict))

cell_line_list = []
cell_line_num_list = []
for cell_line, cell_line_num in cell_line_dict.items():
    cell_line_list.append(cell_line)
    cell_line_num_list.append(cell_line_num)

cell_line_list, cell_line_num_list = zip(*sorted(zip(cell_line_list, cell_line_num_list), key=lambda x: x[0]))

cell_line_df = pd.DataFrame({
    'cell_line_origin': cell_line_list,
    'cell_line_gene_num': cell_line_num_list
})

cell_line_df = cell_line_df.astype({'cell_line_origin': 'string', 'cell_line_gene_num': 'int'})

cell_line_df.to_csv(cell_line_set_dataset_path, index=False)