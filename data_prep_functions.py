import pandas as pd
import re

def extract_state_total_crime(filepath: str) -> pd.DataFrame:
    """
    Extracts state-level summary statistics from Uniform Crime Reporting (UCR) "Crime in the United States
    by State" Excel tables for a given year, pulling estimated totals for population, violent crime, and
    property crime. It returns DataFrame with state abbreviations, year, population, and total Part I crime
    estimate.

    The tables are expected to follow a relatively consistent structure, such as those published in:
    - Table 3 (2016): https://ucr.fbi.gov/crime-in-the-u.s/2016/crime-in-the-u.s.-2016/tables/table-3
    - Table 5 (2020): https://cde.ucr.cjis.gov/LATEST/webapp/#

    Puerto Rico is included in the original files but is excluded from the returned DataFrame.

    Parameters:
        filepath (str): Path to the Excel file containing the UCR state summary table.

    Returns:
        pd.DataFrame: DataFrame with columns:
            - STATE: Two-letter state abbreviation
            - YEAR: Year of the report (inferred from header)
            - POPULATION: Estimated state population
            - TOTAL_CRIME: Sum of violent and property crimes

        >>> crime = extract_state_total_crime("Data/Table_05_Crime_in_the_United_States_by_State_2020.xlsx")
        >>> len(crime)
        51
        >>> crime['YEAR'].nunique()
        1
        >>> print(crime['YEAR'].iloc[0])
        2020
        >>> print(crime.loc[crime['STATE'].str.upper() == 'NC', 'TOTAL_CRIME'].values[0])
        280477
        >>> print(crime.loc[crime['STATE'].str.upper() == 'WY', 'POPULATION'].values[0])
        582328
        >>> crime2 = extract_state_total_crime("Data/table-3.xlsx")
        >>> crime2.loc[50, ['STATE', 'TOTAL_CRIME']].to_dict()
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

def apply_weight(df: pd.DataFrame, columns: list, weight_col: str = 'FINALWGT', prefix: str = 'W_') -> pd.DataFrame:
    """
    Multiplies specified columns by a weight column and adds them to the DataFrame with a prefix.

    :param df: DataFrame to modify
    :param columns: List of column names to weight
    :param weight_col: Name of the weight column (default: 'FINALWGT')
    :param prefix: Prefix for new weighted columns (default: 'W_')
    :return: The original DataFrame with weighted columns added
    """
    for col in columns:
        df[f"{prefix}{col}"] = df[col] * df[weight_col]
    return df

def weighted_binary(df: pd.DataFrame, col: str, weight_col: str = 'WEIGHT') -> float:
    """
    Computes the weighted proportion of agencies flagged (==1) for a given binary column,
    using the provided survey weight column.

    :param df: DataFrame containing the data
    :param col: Binary column to calculate weighted proportion for
    :param weight_col: Column containing survey weights (e.g., 'FINALWGT')
    :return: Weighted proportion of agencies with flag == 1
    """
    flagged = df[col] == 1
    return df.loc[flagged, weight_col].sum() / df[weight_col].sum()


def read_lemas_weight(filepath: str, return_strata_counts: bool = False, verbose: bool = True) -> pd.DataFrame:
    """
    Reads and processes LEMAS survey data from a tab-delimited file. Returns a DataFrame providing
    survey-weighted, state-level estimates of police agency characteristics—specifically, the
    demographic composition of full-time sworn officers and the prevalence of community-oriented
    accountability practices.

    Selected variables include:
        - Agency characteristics: STATE, STRATA, FTSWORN (full-time sworn officers)
        - Demographics: PERS_FEMALE, PERS_BLACK_FEM/MALE, PERS_HISP_FEM/MALE
        - Policy flags: CCRB (civilian complaint board), CFDBK_POLICY (community feedback)
        - Sampling weights: FINALWGT (2016), SAMPLINGWEIGHT (2020)

    Processing steps:
        - Standardizes column names and 'STRATA' codes across years
        - Replaces -8/-9 nonresponse codes with NaN in binary flags
        - Filters invalid rows (e.g., FTSWORN ≤ 0)
        - Applies survey weights and aggregates to state level
        - Calculates % female, % Black, and % Hispanic officers
        - Optionally adds STRATA group counts per state

    Parameters:
    :param filepath (str): Path to the input LEMAS TSV file (e.g., 'lemas_2016.tsv')
    :param return_strata_counts (bool): If True, includes per-state counts of agencies by STRATA group.

    :return: A state-level DataFrame including:
            - STATE: State abbreviation
            - YEAR: Survey year, extracted from the input filename
            - W_FTSWORN: Totals of full-time sworn officers in the state
            - %_FEMALE: Share of full-time sworn officers in the state who are female
            - %_BLACK: Share of sworn officers who are Black (female + male)
            - %_HISP: Share of sworn officers who are Hispanic (female + male)
            - CCRB: Proportion of agencies that reported having a civilian complaint board;
            - CFDBK_POLICY: Proportion of agencies that reported using community feedback
                            to inform internal policy decisions
            - (Optional) STRATA_* columns: If return_strata_counts is True, includes the number of agencies
                                           in each STRATA group for each state
            >>> df = read_lemas_weight("Data/LEMAS2016.tsv", verbose= False)
            >>> len(df)
            51
            >>> bool(df["CCRB"].min() >= 0 and df["CCRB"].max() <= 1)
            True
            >>> bool(df["CFDBK_POLICY"].min() >= 0 and df["CFDBK_POLICY"].max() <= 1)
            True
            >>> bool(df["%_FEMALE"].min() >= 0 and df["%_FEMALE"].max() <= 1)
            True
            >>> bool(df["%_BLACK"].min() >= 0 and df["%_BLACK"].max() <= 1)
            True
            >>> bool(df["%_HISP"].min() >= 0 and df["%_HISP"].max() <= 1)
            True
            >>> df_strata = read_lemas_weight("Data/LEMAS2016.tsv", return_strata_counts=True, verbose=False)
            >>> any(col.startswith("STRATA_") for col in df_strata.columns)
            True
    """
    columns = ['STATE',
               'STRATA',
               'FTSWORN',
               'PTSWORN',
               'PERS_FEMALE',
               'PERS_BLACK_FEM', 'PERS_BLACK_MALE',
               'PERS_HISP_FEM', 'PERS_HISP_MALE',
               'POL_CCRB',  # civilian complaint board flag 2016
               'CIV_COMPL',  # civilian complaint board flag  2020
               'CP_SURV_POLICY',  # community feedback used for informing agency policy flag 2016
               'FDBK_POLICY',  # community feedback used for informing agency policy flag 2020
               'FINALWGT',  # Survey weights 2016
               'SAMPLINGWEIGHT', # Survey weights 2020
               'COMPLETE'
               ]

    rename_columns = {
        'POL_CCRB': 'CCRB',
        'CIV_COMPL': 'CCRB',
        'CP_SURV_POLICY': 'CFDBK_POLICY',
        'FDBK_POLICY': 'CFDBK_POLICY',
        'FINALWGT':'WEIGHT',
        'SAMPLINGWEIGHT':'WEIGHT'
    }

    strata_map_2016_to_2020 = {
        101: 1, 102: 2, 103: 3, 104: 4, 105: 5, 106: 6, 107: 7,
        201: 8, 202: 9, 203: 10, 204: 11, 205: 12,
        206: 13, 207: 13,
        301: 15
    }

    lemas = pd.read_csv(filepath, usecols=lambda x: x.upper() in columns, sep='\t', na_values=[-8, -9])
    lemas = lemas.rename(columns=rename_columns)

    original_len = len(lemas)

    if 'COMPLETE' in lemas.columns:
        lemas = lemas[((lemas['FTSWORN'] > 0)|(lemas['PTSWORN'] >= 2)) & (lemas['COMPLETE']>0.6)].copy()
        clean_len = len(lemas)
        if verbose:
            print(f'{original_len - clean_len} rows from {original_len} dropped due to FTSWORN < 1 or survey completion rate below 60%.')

    # STRATA values are in 100–300 range for 2016 coding
    if lemas['STRATA'].max() > 15:
        lemas['STRATA'] = lemas['STRATA'].map(strata_map_2016_to_2020).fillna(lemas['STRATA'])

    ag_demo_cols = ['FTSWORN', 'PERS_FEMALE', 'PERS_BLACK_FEM', 'PERS_BLACK_MALE', 'PERS_HISP_FEM', 'PERS_HISP_MALE']
    lemas = apply_weight(lemas, ag_demo_cols, weight_col='WEIGHT')

    weighted_cols = [col for col in lemas.columns if col.startswith('W_')]

    dem_by_state = lemas.groupby('STATE', as_index=False)[weighted_cols].sum()

    binary_cols_by_state = (
        lemas.groupby('STATE', as_index=False)
        .apply(lambda x: pd.Series({
            'CCRB': weighted_binary(x, 'CCRB', 'WEIGHT'),
            'CFDBK_POLICY': weighted_binary(x, 'CFDBK_POLICY', 'WEIGHT')
        }))
        .reset_index(drop=True)
    )

    lemas_by_state = pd.merge(dem_by_state, binary_cols_by_state, on='STATE')

    lemas_by_state['YEAR'] = int(filepath[-8:-4])

    lemas_by_state['%_FEMALE'] = lemas_by_state['W_PERS_FEMALE'] / lemas_by_state['W_FTSWORN']
    lemas_by_state['%_BLACK'] = (
        lemas_by_state['W_PERS_BLACK_FEM'] + lemas_by_state['W_PERS_BLACK_MALE']
    ) / lemas_by_state['W_FTSWORN']
    lemas_by_state['%_HISP'] = (
        lemas_by_state['W_PERS_HISP_FEM'] + lemas_by_state['W_PERS_HISP_MALE']
    ) / lemas_by_state['W_FTSWORN']

    ordered_cols = [
        'STATE', 'YEAR',
        'W_FTSWORN',
        '%_FEMALE', '%_BLACK', '%_HISP',
        'CCRB', 'CFDBK_POLICY'
    ]

    lemas_by_state = lemas_by_state[ordered_cols]

    if return_strata_counts:
        strata_counts = pd.crosstab(lemas['STATE'], lemas['STRATA']).reset_index()
        strata_counts.columns = ['STATE'] + [f'STRATA_{c}' for c in strata_counts.columns[1:]]
        lemas_by_state = pd.merge(lemas_by_state, strata_counts, on='STATE', how='left')

    return lemas_by_state

def read_lemas(filepath: str, return_strata_counts: bool = False, verbose: bool = True) -> pd.DataFrame:
    """
        Reads and processes LEMAS survey data from a tab-delimited file. Returns a DataFrame providing
        state-level estimates of police agency characteristics—specifically, the
        demographic composition of full-time sworn officers and the prevalence of community-oriented
        accountability practices weighted by the number of full-time officers in the state.

        Selected variables include:
            - Agency characteristics: STATE, STRATA, FTSWORN (full-time sworn officers)
            - Demographics: PERS_FEMALE, PERS_BLACK_FEM/MALE, PERS_HISP_FEM/MALE
            - Policy flags: CCRB (civilian complaint board), CFDBK_POLICY (community feedback)
            - Sampling weights: FINALWGT (2016), SAMPLINGWEIGHT (2020)

        Processing steps:
            - Replaces -8/-9 nonresponse codes with NaN
            - Standardizes column names and 'STRATA' codes across years
            - Filters invalid rows (e.g., FTSWORN ≤ 0)
            - Applies survey weights and aggregates to state level
            - Calculates % female, % Black, and % Hispanic officers
            - Optionally adds STRATA group counts per state

        Parameters:
        :param filepath (str): Path to the input LEMAS TSV file (e.g., 'lemas_2016.tsv')
        :param return_strata_counts (bool): If True, includes per-state counts of agencies by STRATA group.

        :return: A state-level DataFrame including:
                - STATE: State abbreviation
                - YEAR: Survey year, extracted from the input filename
                - W_FTSWORN: Totals of full-time sworn officers in the state
                - %_FEMALE: Share of full-time sworn officers in the state who are female
                - %_BLACK: Share of sworn officers who are Black (female + male)
                - %_HISP: Share of sworn officers who are Hispanic (female + male)
                - CCRB: Proportion of officers in state employed at agency that reported having a civilian
                complaint board
                - CFDBK_POLICY: Proportion of officers in state that employed at agency that reported using community feedback
                                to inform internal policy decisions
                - (Optional) STRATA_* columns: If return_strata_counts is True, includes the number of agencies
                                               in each STRATA group for each state
                >>> df = read_lemas("Data/LEMAS2016.tsv", verbose= False)
                >>> len(df)
                51
                >>> bool(df["CCRB"].min() >= 0 and df["CCRB"].max() <= 1)
                True
                >>> bool(df["CFDBK_POLICY"].min() >= 0 and df["CFDBK_POLICY"].max() <= 1)
                True
                >>> bool(df["%_FEMALE"].min() >= 0 and df["%_FEMALE"].max() <= 1)
                True
                >>> bool(df["%_BLACK"].min() >= 0 and df["%_BLACK"].max() <= 1)
                True
                >>> bool(df["%_HISP"].min() >= 0 and df["%_HISP"].max() <= 1)
                True
                >>> df_strata = read_lemas("Data/LEMAS2016.tsv", return_strata_counts=True, verbose=False)
                >>> any(col.startswith("STRATA_") for col in df_strata.columns)
                True
        """
    columns = ['STATE',
               'STRATA',
               'FTSWORN',
               'PTSWORN',
               'PERS_FEMALE',
               'PERS_BLACK_FEM', 'PERS_BLACK_MALE',
               'PERS_HISP_FEM', 'PERS_HISP_MALE',
               'POL_CCRB',  # civilian complaint board flag 2016
               'CIV_COMPL',  # civilian complaint board flag  2020
               'CP_SURV_POLICY',  # community feedback used for informing agency policy flag 2016
               'FDBK_POLICY',  # community feedback used for informing agency policy flag 2020
               'FINALWGT',  # Survey weights 2016
               'SAMPLINGWEIGHT',  # Survey weights 2020
               'COMPLETE'
               ]

    rename_columns = {
        'POL_CCRB': 'CCRB',
        'CIV_COMPL': 'CCRB',
        'CP_SURV_POLICY': 'CFDBK_POLICY',
        'FDBK_POLICY': 'CFDBK_POLICY',
        'FINALWGT': 'WEIGHT',
        'SAMPLINGWEIGHT': 'WEIGHT'
    }

    strata_map_2016_to_2020 = {
        101: 1, 102: 2, 103: 3, 104: 4, 105: 5, 106: 6, 107: 7,
        201: 8, 202: 9, 203: 10, 204: 11, 205: 12,
        206: 13, 207: 13,
        301: 15
    }

    lemas = pd.read_csv(filepath, usecols=lambda x: x.upper() in columns, sep='\t', na_values=[-8, -9])
    lemas = lemas.rename(columns=rename_columns)

    original_len = len(lemas)

    if 'COMPLETE' in lemas.columns:
        lemas = lemas[((lemas['FTSWORN'] > 0)|(lemas['PTSWORN'] >= 2)) & (lemas['COMPLETE']>0.6)].copy()
        clean_len = len(lemas)
        if verbose:
            print(f'{original_len - clean_len} rows from {original_len} dropped due to FTSWORN < 1 or survey completion rate below 60%.')

    # STRATA values are in 100–300 range for 2016 coding
    if lemas['STRATA'].max() > 15:
        lemas['STRATA'] = lemas['STRATA'].map(strata_map_2016_to_2020).fillna(lemas['STRATA'])

    dem_by_state = lemas.groupby('STATE').agg({
        'FTSWORN': 'sum',
        'PERS_FEMALE': 'sum',
        'PERS_BLACK_FEM': 'sum',
        'PERS_BLACK_MALE': 'sum',
        'PERS_HISP_FEM': 'sum',
        'PERS_HISP_MALE': 'sum',
    }).reset_index()

    binary_cols_by_state = (
        lemas.groupby('STATE', as_index=False)
        .apply(lambda x: pd.Series({
            'CCRB': weighted_binary(x, 'CCRB'),
            'CFDBK_POLICY': weighted_binary(x, 'CFDBK_POLICY')
        }), include_groups=False)
        .reset_index(drop=True)
    )

    lemas_by_state = pd.merge(dem_by_state, binary_cols_by_state, on='STATE')

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
        'CCRB', 'CFDBK_POLICY'
    ]

    lemas_by_state = lemas_by_state[ordered_columns]

    if return_strata_counts:
        strata_counts = pd.crosstab(lemas['STATE'], lemas['STRATA']).reset_index()
        strata_counts.columns = ['STATE'] + [f'STRATA_{c}' for c in strata_counts.columns[1:]]
        lemas_by_state = pd.merge(lemas_by_state, strata_counts, on='STATE', how='left')

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

def standardize(series: pd.Series) -> pd.Series:
    return (series - series.min()) / (series.max() - series.min())
