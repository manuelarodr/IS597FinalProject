import pandas as pd

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

    # Optional: sort for readability
    df_long = df_long.sort_values(['state', 'year']).reset_index(drop=True)

    return df_long

# example use：
# df_long = aggregate_spotlite_to_state_long('SPOTLITE_US_2014_2021_1_11_2024_countycountbyyear_wide.csv')
# df_long.to_csv('state_use_of_force_long_format.csv', index=False)

