import os
import sys

dir_now = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(dir_now)
dir_module = os.path.join(project_dir, 'module')
dir_code = os.path.join(project_dir, 'code')
dir_data = os.path.join(project_dir, 'data')

sys.path.append(dir_module)

import pandas as pd
import signal
import fire
import time

import genesearch
import pdutility

def main(n=False, l=36000):

    gene_set_dataset_filename = 'gene_set.csv'
    gene_summary_dataset_filename = 'gene_summary.csv'

    gene_set_dataset_path = os.path.join(dir_data, gene_set_dataset_filename)
    gene_summary_dataset_path = os.path.join(dir_data, gene_summary_dataset_filename)

    if os.path.exists(gene_summary_dataset_path) and (not n):
        gene_df = pd.read_csv(gene_summary_dataset_path, dtype = {'gene_symbol': 'string', 'gene_id': int, 'gene_summary': 'string', 'gene_search_error_code': int})
    else:
        gene_df = pd.read_csv(gene_set_dataset_path, dtype = {'gene_symbol': 'string'})
        
    pdutility.add_column_try(gene_df, 'gene_search_error_code', -1, int)
    pdutility.add_column_try(gene_df, 'gene_id', -1, int)
    pdutility.add_column_try(gene_df, 'gene_summary', '', 'string')
    
    global gene_exist
    global gene_none
    global gene_d

    gene_exist = 0
    gene_none = 0
    gene_d = 0

    def saving_file():
        print("Saving file and exiting...")
        print('Gene Set Length:', gene_df.shape[0])
        print('Gene Summary Exist:', gene_exist)
        print('Gene Summary None:', gene_none)
        gene_df.to_csv(gene_summary_dataset_path, index=False)

    def signal_handler(signum, frame):
        saving_file()
        sys.exit(0)
        
    def exception_handler(exc_type, exc_value, exc_traceback):
        saving_file()
        sys.__excepthook__(exc_type, exc_value, exc_traceback)  # 调用默认的异常处理程序

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 注册异常处理函数
    sys.excepthook = exception_handler

    def genesearch_column_add(row):
        if row['gene_search_error_code'] != 0:
            gene_ans = genesearch.get_gene_id_summary_from_symbol_sim_except(row['gene_symbol'])
            if gene_ans[0] == None:
                gene_ans = (-1, gene_ans[1], gene_ans[2])
            global gene_d
            gene_d = gene_d + 1
        else:
            gene_ans = (row['gene_id'], row['gene_summary'], row['gene_search_error_code'])

        global gene_exist
        global gene_none

        is_exist = (gene_ans[2] == 0)
        gene_exist = gene_exist + is_exist
        gene_none = gene_none + (not is_exist)
        
        if row['gene_search_error_code'] != 0:
            print(f"Gene({row['gene_symbol']}):", 'exist' if is_exist else 'none')
        
        return gene_ans

    for ri in range(gene_df.shape[0]):
        istry = True
        isbreak = False
        while(istry):
            try:
                result = genesearch_column_add(gene_df.iloc[ri])
                gene_df.loc[ri, 'gene_id'] = int(result[0])
                gene_df.loc[ri, 'gene_summary'] = str(result[1])
                gene_df.loc[ri, 'gene_search_error_code'] = int(result[2])
                if gene_d >= l:
                    isbreak = True
                istry = False
            except:
                time.sleep(10)
        if isbreak:
            break


    saving_file()

    gene_df.to_csv(gene_summary_dataset_path, index=False)

if __name__ == "__main__":
    fire.Fire(main)