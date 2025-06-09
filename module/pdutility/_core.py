import pandas as pd
import numpy as np
def add_column_try(pdn:pd.DataFrame, column, fill, atype):
    if not column in pdn.columns:
        pdn[column] = fill
    pdn[column] = pdn[column].astype(atype)