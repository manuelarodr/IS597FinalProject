import pandas as pd
import re

def extract_state_total_crime(filepath: str) -> pd.DataFrame:
    """
    Extracts estimated state-level totals for population, violent crime, and property crime
    from "Crime in the United States by State" summarized Excel tables and calculates total
    Part I crime estimate for each state (violent crime + property crime). Puerto Rico is
    also reported in the original tables, but it is dropped here.

    Parameters:
        filepath (str): Path to the Excel file.

    Returns:
        pd.DataFrame: Processed DataFrame with STATE, POPULATION, and TOTAL_CRIME columns.

        >>> df = extract_state_total_crime("Data/Table_05_Crime_in_the_United_States_by_State_2020.xlsx")
        >>> len(df)
        51
        >>> df['YEAR'].nunique()
        1
        >>> print(df['YEAR'].iloc[0])
        2020
        >>> print(df.loc[df['STATE'].str.upper() == 'NC', 'TOTAL_CRIME'].values[0])
        280477
        >>> print(df.loc[df['STATE'].str.upper() == 'WY', 'POPULATION'].values[0])
        582328
        >>> df2 = extract_state_total_crime("Data/table-3.xlsx")
        >>> df2.loc[50, ['STATE', 'TOTAL_CRIME']].to_dict()
        {'STATE': 'WY', 'TOTAL_CRIME': 12890}
    """

    df = pd.read_excel(filepath, header=None)

    year = int(''.join(re.findall(r'\d+', str(df.iloc[2, 0]))))

    # table header starts on fourth row
    cleaned_header = df.iloc[3].astype(str).str.replace('\n', ' ', regex=False).str.strip().str.replace(r'\d+', '', regex=True).str.upper().str.replace('  ', ' ')

    df.columns = cleaned_header

    # drop Table title rows and header
    df = df.drop(index=range(4)).reset_index(drop=True)

    df['STATE'] = df['STATE'].replace(r'^\s*$', pd.NA, regex=True)

    # Forward-fill state names
    df['STATE'] = df['STATE'].ffill()

    # rows ending in 'TOTAL' in area column contain the state total estimates
    df = df[df['AREA'].str.upper().str.endswith('TOTAL', na=False)].copy()

    dtypes = {'STATE':'str', 'POPULATION':'Int64', 'VIOLENT CRIME':'Int64', 'PROPERTY CRIME':'Int64'}

    df = df[list(dtypes)].copy().astype(dtypes)

    # Clean state names and remove Puerto Rico
    df['STATE'] = df['STATE'].str.strip().replace(r'\d+', '', regex=True)
    df = df[~df['STATE'].str.upper().eq('PUERTO RICO')]

    state_to_abbrev = {
        'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR',
        'CALIFORNIA': 'CA', 'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE',
        'FLORIDA': 'FL', 'GEORGIA': 'GA', 'HAWAII': 'HI', 'IDAHO': 'ID',
        'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA', 'KANSAS': 'KS',
        'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD',
        'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS',
        'MISSOURI': 'MO', 'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV',
        'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ', 'NEW MEXICO': 'NM', 'NEW YORK': 'NY',
        'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH', 'OKLAHOMA': 'OK',
        'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
        'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT',
        'VERMONT': 'VT', 'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV',
        'WISCONSIN': 'WI', 'WYOMING': 'WY', 'DISTRICT OF COLUMBIA': 'DC'
    }
    # convert from full-state name to state abbreviation
    df['STATE'] = df['STATE'].str.upper().map(state_to_abbrev)

    # Calculate total crime
    df['TOTAL_CRIME'] = df['VIOLENT CRIME'] + df['PROPERTY CRIME']

    df['YEAR'] = year

    df = df[['STATE','YEAR','POPULATION','TOTAL_CRIME']].sort_values('STATE').reset_index(drop=True)

    return df

def weighted_flags(df: pd.DataFrame, col: str, weight_col:str = 'FTSWORN'):
    """
        Helper function for read_lemas().
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
    columns = ['STATE',
               'STRATA',
               'FTSWORN',
               'PERS_FEMALE',
               'PERS_BLACK_FEM', 'PERS_BLACK_MALE',
               'PERS_HISP_FEM', 'PERS_HISP_MALE',
               'POL_CCRB',  # civilian complaint board flag 2016
               'CIV_COMPL',  # civilian complaint board flag  2020
               'CP_SURV_POLICY',  # community feedback used for informing agency policy flag 2016
               'FDBK_POLICY'  # community feedback used for informing agency policy flag 2020
               ]

    rename_columns = {
        'POL_CCRB': 'CCRB',
        'CIV_COMPL': 'CCRB',
        'CP_SURV_POLICY': 'CFDBK_POLICY',
        'FDBK_POLICY': 'CFDBK_POLICY'
    }

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

    lemas_by_state['YEAR'] = int(filepath[-8:-4])

    lemas_by_state['%_FEMALE'] = lemas_by_state['PERS_FEMALE'] / lemas_by_state['FTSWORN']
    lemas_by_state['%_BLACK'] = (lemas_by_state['PERS_BLACK_FEM'] + lemas_by_state['PERS_BLACK_MALE']) / lemas_by_state[
        'FTSWORN']
    lemas_by_state['%_HISP'] = (lemas_by_state['PERS_HISP_FEM'] + lemas_by_state['PERS_HISP_MALE']) / lemas_by_state[
        'FTSWORN']

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

def aggregate_spotlite_to_state_long(csv_path: str) -> pd.DataFrame:
    """
    Aggregates SPOTLITE county-level use-of-force data to state-level for selected years (2016, 2020),
    and reshapes the result to long format with one row per state per year.

    Parameters:
        csv_path (str): Path to the county-level SPOTLITE data.

    Returns:
        pd.DataFrame: State-level long-format data for 2016 and 2020.
    """
    # Load data
    df = pd.read_csv(csv_path)

    # Select relevant columns
    year_cols = ['y2016', 'y2020']
    group_keys = ['state', 'state_name']

    # Aggregate county-level to state-level
    df_state = df.groupby(group_keys)[year_cols].sum().reset_index()

    # Reshape to long format
    df_long = pd.melt(
        df_state,
        id_vars=group_keys,
        value_vars=year_cols,
        var_name='year',
        value_name='use_of_force_count'
    )

    # Convert 'y2016' → 2016 (int)
    df_long['year'] = df_long['year'].str.extract(r'y(\d{4})').astype(int)

    df_long.columns = df_long.columns.str.upper()

    # Optional: sort for readability
    df_long = df_long.sort_values(['STATE']).reset_index(drop=True)

    return df_long

# example use：
# df_long = aggregate_spotlite_to_state_long('SPOTLITE_US_2014_2021_1_11_2024_countycountbyyear_wide.csv')
# df_long.to_csv('state_use_of_force_long_format.csv', index=False)
