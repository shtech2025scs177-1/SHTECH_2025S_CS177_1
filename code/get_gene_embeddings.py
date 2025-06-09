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

from transformers import AutoTokenizer, AutoModel

def main(n = False, l = 36000):

    gene_summary_dataset_filename = 'gene_summary.csv'
    gene_embeddings_dataset_filename = 'gene_embeddings.pkl'
    gene_embeddings_log_dataset_filename = 'gene_embeddings_log.pkl'
    gene_summary_dataset_path = os.path.join(dir_data, gene_summary_dataset_filename)
    gene_embeddings_dataset_path = os.path.join(dir_data, gene_embeddings_dataset_filename)
    gene_embeddings_log_dataset_path = os.path.join(dir_data, gene_embeddings_log_dataset_filename)

    gene_df = pd.read_csv(gene_summary_dataset_path, dtype = {'gene_symbol': 'string', 'gene_id': int, 'gene_summary': 'string', 'gene_search_error_code': int})

    if os.path.exists(gene_embeddings_dataset_path) and (not n):
        with open(gene_embeddings_dataset_path, 'rb') as file:
            gene_embeddings = pickle.load(file)
        with open(gene_embeddings_log_dataset_path, 'rb') as file:
            gene_embeddings_log = pickle.load(file)
    else:
        gene_embeddings = {}
        gene_embeddings_log = [0]
    
    def saving_file():
        print("Saving file and exiting...")
        print(f"embeddings length: {len(gene_embeddings)}")
        print(f"Rest of gene_embeddings: {gene_embeddings_log[1:]}, [{gene_embeddings_log[0]}:{gene_df['gene_symbol'].shape[0]}]")
        with open(gene_embeddings_dataset_path, 'wb') as file:
            pickle.dump(gene_embeddings, file)
        with open(gene_embeddings_log_dataset_path, 'wb') as file:
            pickle.dump(gene_embeddings_log, file)
    
    def signal_handler(signum, frame):
        saving_file()
        sys.exit(0)
        
    def exception_handler(exc_type, exc_value, exc_traceback):
        saving_file()
        sys.__excepthook__(exc_type, exc_value, exc_traceback)  # 调用默认的异常处理程序

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    sys.excepthook = exception_handler

    # 初始化 GPT-3.5 模型和分词器
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    model = AutoModel.from_pretrained("gpt2")
    hidden_size = model.config.hidden_size
    # 创建一个零张量，维度为 (hidden_size,)
    default_embedding = torch.zeros(hidden_size)

    def get_description_str(description):
        if pd.isna(description):
            return ""
        else:
            return description

    def remove_brace(description:str):
        des_list = description.split('[')
        return des_list[0]




    gene_embeddings_log_list = gene_embeddings_log[1:] + [i for i in range(gene_embeddings_log[0], gene_df.shape[0])]
    log_start = gene_embeddings_log[0]

    gene_n = 0
    
    for gene_index, gene, error_code, description in zip(gene_embeddings_log_list, 
                                                         gene_df['gene_symbol'].iloc[gene_embeddings_log_list], 
                                                        gene_df['gene_search_error_code'].iloc[gene_embeddings_log_list], 
                                                        gene_df['gene_summary'][gene_embeddings_log_list]):
        
        
        if error_code != 0:
            description_n = ''
            if gene_index >= log_start:
                gene_embeddings_log.append(gene_index)
                gene_embeddings_log[0] = gene_embeddings_log[0] + 1
            continue
        
        else:
            description_n = description
            if gene_index < log_start:
                gene_embeddings_log.remove(gene_index)
        
        try:
            description_str = get_description_str(description_n)
            description_clear = remove_brace(description_str)
            
            if description_clear == '':
                gene_embeddings[gene] = default_embedding.numpy()
            else:
                inputs = tokenizer(description_clear, return_tensors="pt")
                outputs = model(**inputs)
                gene_embeddings[gene] = outputs.last_hidden_state.mean(dim=1).detach().numpy()[0]
                
        except:
            print('Type of description:', type(description_n))
            print('description:', description_n)
            exit(0)
            
        print(f"Gene({gene}): ", gene_embeddings[gene][0:5])
        gene_embeddings_log[0] = gene_embeddings_log[0] + 1
        gene_n = gene_n + 1
        if gene_n > l:
            break
        
    saving_file()

if __name__ == "__main__":
    fire.Fire(main)