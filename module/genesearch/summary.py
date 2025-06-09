import requests

def get_gene_id_from_symbol(gene_symbol):
    # 构建查询 URL
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term={gene_symbol}[Gene]+AND+Homo+sapiens[Organism]&retmode=json"
    
    # 发送 GET 请求
    response = requests.get(url)
    
    # 检查响应状态码
    if response.status_code == 200:
        # 解析 JSON 数据
        data = response.json()
        
        # 提取基因 ID
        if "esearchresult" in data and "idlist" in data["esearchresult"] and len(data["esearchresult"]["idlist"]) > 0:
            return {'id': data["esearchresult"]["idlist"][0], 'exist': True, 'error_code': 0}
        else:
            return {'error': "No gene id found(from gene symbol).", 'error_code': 1, 'exist': False}
    else:
        return {'error': f"Failed to retrieve data. Status code: {response.status_code}(from gene id)", 'error_code': 2, 'exist': False}

def get_gene_summary_from_id(gene_id):
    # 构建查询 URL
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id={gene_id}&retmode=json"
    
    # 发送 GET 请求
    response = requests.get(url)
    
    # 检查响应状态码
    if response.status_code == 200:
        # 解析 JSON 数据
        data = response.json()
        
        # 提取基因摘要信息
        if "result" in data and gene_id in data["result"] and data["result"][gene_id].get("summary") != None:
            summary = data["result"][gene_id]["summary"]
            return {'summary':summary, 'exist': True, 'error_code': 0}
        else:
            return {'error': "No gene summary found(from gene id).", 'error_code': 3, 'exist': False}
    else:
        return {'error': f"Failed to retrieve data. Status code: {response.status_code}(from gene symbol)", 'error_code': 4, 'exist': False}

def get_gene_id_summary_from_symbol(gene_symbol):
    gene_id = get_gene_id_from_symbol(gene_symbol)
    if gene_id['exist']:
        gene_summary = get_gene_summary_from_id(gene_id['id'])
        gene_summary['id'] = gene_id['id']
        return gene_summary
    else:
        return gene_id
    
def get_gene_id_summary_from_symbol_sim_except(gene_symbol):
    gene_id_summary = get_gene_id_summary_from_symbol(gene_symbol)
    return (gene_id_summary.get('id'), gene_id_summary.get('summary'), gene_id_summary.get('error_code'))
    
def get_gene_summary_from_symbol_sim(gene_symbol):
    gene_summary = get_gene_id_summary_from_symbol(gene_symbol)
    if gene_summary['exist']:
        return gene_summary['summary']
    else:
        return None
    
def get_gene_summary_from_symbol_sim_except(gene_symbol):
    gene_summary = get_gene_id_summary_from_symbol(gene_symbol)
    if gene_summary['exist']:
        return gene_summary['summary']
    else:
        return gene_summary
    
def print_gene_summary_from_symbol(gene_symbol):
    gene_summary = get_gene_id_summary_from_symbol(gene_symbol)
    if gene_summary['exist']:
        print(f'Gene Summary({gene_symbol}):', gene_summary['summary'])
    else:
        print(f'Gene Summary({gene_symbol})(error):', gene_summary)