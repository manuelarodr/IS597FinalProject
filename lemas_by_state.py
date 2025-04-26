import pandas as pd
columns = ['STATE',
           'STRATA',
           'FTSWORN',
           'PERS_FEMALE',
           'PERS_BLACK_FEM',
           'PERS_HISP_MALE',
           'PERS_HISP_FEM',
           'POL_CCRB', # civilian complaint board 2016
           'CIV_COMPL', # civilian complaint board 2020
           'CP_SURV_POLICY', #community feedback for informing agency policy 2016
           'FDBK_POLICY' #community feedback for informing agency policy 2020
           ]
lemas_2016 = pd.read_csv('LEMAS2016.tsv', usecols= lambda x: x.upper() in columns, sep='\t')
lemas_2016['POL_CCRB'] = lemas_2016['POL_CCRB'].where(lemas_2016['POL_CCRB'] == 1)
lemas_2016['CP_SURV_POLICY'] = lemas_2016['CP_SURV_POLICY'].where(lemas_2016['CP_SURV_POLICY'] == 1)

lemas_2016['agency_count'] = 1
lemas_by_state_2016 = lemas_2016.groupby(['STATE']).sum().reset_index()
lemas_by_state_2016['YEAR'] = 2016

lemas_2020 = pd.read_csv('LEMAS2020.tsv', usecols= lambda x: x.upper() in columns, sep='\t')
lemas_2020['CIV_COMPL'] = lemas_2020['CIV_COMPL'].where(lemas_2020['CIV_COMPL'] == 1)
lemas_2020['FDBK_POLICY'] = lemas_2020['FDBK_POLICY'].where(lemas_2020['FDBK_POLICY'] == 1)
lemas_2020['agency_count'] = 1
lemas_by_state_2020 = lemas_2020.groupby(['STATE']).sum().reset_index()
lemas_by_state_2020['YEAR'] = 2020

lemas_by_state = pd.concat([lemas_by_state_2016, lemas_by_state_2020], ignore_index=True)
print(lemas_by_state.info())