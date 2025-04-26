import pandas as pd
from pathlib import Path

base_path = Path(__file__).parent
data_folder = base_path / 'Data'

columns = ['STATE',
           'STRATA',
           'FTSWORN',
           'PERS_FEMALE',
           'PERS_BLACK_FEM', 'PERS_BLACK_MALE',
           'PERS_HISP_FEM', 'PERS_HISP_MALE',
           'POL_CCRB', # civilian complaint board flag 2016
           'CIV_COMPL', # civilian complaint board flag  2020
           'CP_SURV_POLICY', #community feedback used for informing agency policy flag 2016
           'FDBK_POLICY' #community feedback used for informing agency policy flag 2020
           ]

rename_columns = {
    'POL_CCRB': 'CCRB',
    'CIV_COMPL': 'CCRB',
    'CP_SURV_POLICY': 'CFDBK_POLICY',
    'FDBK_POLICY': 'CFDBK_POLICY'
}

def weighted_flags(df: pd.DataFrame, col: str, weight_col:str = 'FTSWORN'):
    """

    :param df:
    :param col:
    :param weight_col:
    :return:
    """
    flagged = df[col].notna()
    return df.loc[flagged, weight_col].sum() / df[weight_col].sum()

def read_lemas(filepath: str):
    """

    :param filepath:
    :return:
    """
    lemas = pd.read_csv(filepath, usecols=lambda x: x.upper() in columns, sep='\t')
    lemas = lemas.rename(columns=rename_columns)

    for col in set(rename_columns.values()):
        if col in lemas.columns:
            lemas[col] = lemas[col].where(lemas[col] == 1)

    original_len = len(lemas)

    # remove rows where full-time sworn is 0 or negative and where demographic counts are below 0
    lemas = lemas[(lemas['FTSWORN'] > 0) & (lemas[columns[3:8]] >= 0).all(axis=1)]

    clean_len = len(lemas)

    print(f'{original_len - clean_len} rows dropped due to FTSWORN <=0 or invalid demographic counts.')

    lemas['AG_STATE'] = lemas['STRATA'] > 300
    lemas['AG_SHERIFF'] = (lemas['STRATA'] > 200) & (lemas['STRATA'] <= 300)
    lemas['AG_LOCAL'] = (lemas['STRATA'] > 100) & (lemas['STRATA'] <= 200)

    dem_by_state = lemas.groupby('STATE').agg({
        'FTSWORN': 'sum',
        'PERS_FEMALE': 'sum',
        'PERS_BLACK_FEM': 'sum',
        'PERS_BLACK_MALE': 'sum',
        'PERS_HISP_FEM': 'sum',
        'PERS_HISP_MALE': 'sum',
        'AG_STATE': 'sum',
        'AG_SHERIFF': 'sum',
        'AG_LOCAL': 'sum'
    }).reset_index()

    flagcols_by_state = lemas.groupby('STATE', group_keys=False).apply(
        lambda x: pd.Series({
            'CCRB': weighted_flags(x.drop(columns='STATE'), 'CCRB'),
            'CFDBK_POLICY': weighted_flags(x.drop(columns='STATE'), 'CFDBK_POLICY')
        })
    ).reset_index()

    lemas_by_state = pd.merge(dem_by_state, flagcols_by_state, on='STATE')

    lemas_by_state['YEAR'] = int(filepath.stem[-4:])

    lemas_by_state['%_FEMALE'] = lemas_by_state['PERS_FEMALE'] / lemas_by_state['FTSWORN']
    lemas_by_state['%_BLACK'] = (lemas_by_state['PERS_BLACK_FEM'] + lemas_by_state['PERS_BLACK_MALE']) / lemas_by_state['FTSWORN']
    lemas_by_state['%_HISP'] = (lemas_by_state['PERS_HISP_FEM'] + lemas_by_state['PERS_HISP_MALE']) / lemas_by_state['FTSWORN']

    ordered_columns = [
        'STATE', 'YEAR',
        'FTSWORN',
        '%_FEMALE', '%_BLACK', '%_HISP',
        'CCRB', 'CFDBK_POLICY',
        'AG_STATE', 'AG_SHERIFF', 'AG_LOCAL',
        'PERS_FEMALE', 'PERS_BLACK_FEM', 'PERS_BLACK_MALE', 'PERS_HISP_FEM', 'PERS_HISP_MALE'
    ]

    lemas_by_state = lemas_by_state[ordered_columns]

    return lemas_by_state

lemas_2016 = read_lemas(data_folder / 'LEMAS2016.tsv')
lemas_2020 = read_lemas(data_folder / 'LEMAS2020.tsv')
lemas_all = pd.concat([lemas_2016, lemas_2020], ignore_index=True)

