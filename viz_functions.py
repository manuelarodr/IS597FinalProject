import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def scatter_dual_year_highlight(df: pd.DataFrame, x_var: str, y_var: str, label_map: dict = None, color_map: dict = {2016: '#1f77b4', 2020: '#BA4A00'}):
    """
    Creates side-by-side scatterplots comparing two years.
    Each subplot shows plots data for both years and highlights the relevant year in color.
    Adds a horizontal line for the mean y-value.


    :param df (pd.DataFrame): Combined DataFrame with at least 'YEAR', x_var, y_var columns.
    :param x_var (str): Column name to use as x-axis.
    :param y_var (str): Column name to use as y-axis.
    :param label_map (dict): Optional dict mapping column names to labels. Defaults to None.
    :param color_map (dict): Optional dict mapping each year to a color.
    """
    x_label = label_map.get(x_var, x_var.replace('_', ' ')) if label_map else x_var.replace('_', ' ')
    y_label = label_map.get(y_var, y_var.replace('_', ' ')) if label_map else y_var.replace('_', ' ')

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    for ax, year in zip(axes, sorted(df['YEAR'].unique())):
        ax.scatter(df[x_var], df[y_var], color='lightgray', alpha=0.4)

        # highlight points from the selected year
        df_year = df[df['YEAR'] == year]
        ax.scatter(df_year[x_var], df_year[y_var],
                   color=color_map.get(year, 'black'), alpha=0.9)

        # add mean line  y_var
        y_mean = df_year[y_var].mean()
        ax.axhline(y=y_mean, color=color_map.get(year, 'black'), linestyle='--', linewidth=1)
        ax.text(x=0.98, y=y_mean, s=f'Mean = {y_mean:.2f}',
                ha='right', va='bottom', fontsize=10, color=color_map.get(year, 'black'),
                transform=ax.get_yaxis_transform())

        ax.set_title(f"{year}")
        ax.set_xlabel(x_label)
        ax.grid(False)

    axes[0].set_ylabel(y_label)
    fig.suptitle(f'{x_label} vs \n {y_label}', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

def plot_correlation_matrix(df, figsize=(12, 10), annot_fmt=".2f"):
    corr = df.corr()

    plt.figure(figsize=figsize)
    sns.heatmap(corr,
                annot=True,
                fmt=annot_fmt,
                cmap='RdBu_r',
                vmin=-1, vmax=1,
                center=0,
                linewidths=0.5,
                cbar_kws={'label': 'Correlation'})

    plt.title("Correlation Matrix", fontsize=16)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()