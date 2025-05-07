import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_histogram(df, column, bins=15, color='#1f77b4', figsize=(8, 5)):
    """
    Plots a histogram for a specified column.

    :param df (pd.DataFrame): Input DataFrame.
    :param column (str): The column to plot.
    :param bins (int): Number of bins in the histogram.
    :param color (str): Bar color.
    :param label_dict (dict): Optional mapping of column names
    :param figsize (tuple): Figure size.
    """

    plt.figure(figsize=figsize)
    df[column].hist(bins=bins, color=color, edgecolor='white')
    plt.grid(axis='y')
    plt.title(f'Distribution of column')
    plt.xlabel(column)
    plt.ylabel('# of Observations')
    plt.tight_layout()
    plt.show()

def bar_by_state_year(df: pd.DataFrame, value_col:str , state_col: str ='STATE_NAME', year_col: str ='YEAR',
                    label_dict: dict =None, figsize: tuple =(14, 6), color_map: dict ={2016: '#1f77b4', 2020: '#BA4A00'}):
    """
    Plots a bar chart of any variable across states, split by year and ordered by descending order of the variable in the
    earliest year.

    :param df: Input data.
    :param value_col: Column name for the numeric variable to plot.
    :param state_col: Column name for state.
    :param year_col: Column name for year.
    :param label_dict: Optional mapping for value_col label in title/y-axis.
    :param figsize: Figure size for the plot.
    :param color_map: Optional mapping for value_col label in title/y-axis.
    """
    value_label = label_dict.get(value_col, value_col) if label_dict else value_col

    # sort states by desc order of the value in the earliest year
    df_plot = df.copy()
    state_order = ( df_plot[df_plot[year_col] == df_plot[year_col].min()].sort_values(by=value_col, ascending=False)[state_col].tolist())

    # convert to categorical so seaborn respects order
    df_plot[state_col] = pd.Categorical(df_plot[state_col], categories=state_order, ordered=True)

    # Plot
    plt.figure(figsize=figsize)
    sns.barplot(data=df_plot, x=state_col, y=value_col, hue=year_col, palette= color_map)
    plt.xticks(rotation=90)
    plt.title(f'{value_label} by State and Year')
    plt.xlabel('State')
    plt.ylabel(value_label)
    plt.tight_layout()
    plt.legend(title='Year')
    plt.show()

def scatter_dual_year_highlight(df: pd.DataFrame, x_var: str, y_var: str, label_map: dict = None, color_map: dict = {2016: '#1f77b4', 2020: '#BA4A00'}):
    """
    Creates side-by-side scatterplots comparing two years. Each subplot shows plots data for both years and highlights
    the relevant year in color. Adds a horizontal line for the mean y-value.


    :param df: Combined DataFrame with at least 'YEAR', x_var, y_var columns.
    :param x_var: Column name to use as x-axis.
    :param y_var: Column name to use as y-axis.
    :param label_map: Optional dict mapping column names to labels. Defaults to None.
    :param color_map: Optional dict mapping each year to a color.
    """
    x_label = label_map.get(x_var, x_var.replace('_', ' ')) if label_map else x_var.replace('_', ' ')
    y_label = label_map.get(y_var, y_var.replace('_', ' ')) if label_map else y_var.replace('_', ' ')

    x_title = x_label.replace(' (log1p)', '').replace(' (log1p-scaled)', '')
    y_title = y_label.replace(' (log1p)', '').replace(' (log1p-scaled)', '')

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
    fig.suptitle(f'{x_title} vs \n {y_title}', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

def plot_correlation_matrix(df, figsize=(12, 10), annot_fmt=".2f"):
    corr = df.corr(method='spearman')

    plt.figure(figsize=figsize)
    sns.heatmap(corr,
                annot=True,
                fmt=annot_fmt,
                cmap='RdBu_r',
                vmin=-1, vmax=1,
                center=0,
                linewidths=0.5,
                cbar_kws={'label': 'Correlation'})

    plt.title("Spearman Correlation Matrix", fontsize=16)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

def plot_quartile_boxplot(df: pd.DataFrame, x_var: str, y_var: str, label_map: dict = None, n_quartiles=4):
    """
    Plots a boxplot of y_var across quartiles of x_var.

    :param df: Input DataFrame.
    :param x_var: The column to bin into quartiles.
    :param y_var: The dependent variable to plot on the y-axis.
    :param label_map: Optional dictionary to map x_var and y_var to labels.
    :param n_quartiles: Number of quantile bins (default = 4).
    """
    # Quartile labels
    quartile_labels = [f'Q{i + 1}' for i in range(n_quartiles)]
    quartile_labels[0] += ' (Lowest)'
    quartile_labels[-1] += ' (Highest)'

    quartile_col = f'{x_var}_Q'
    df[quartile_col] = pd.qcut(df[x_var], q=n_quartiles, labels=quartile_labels)

    # Get readable axis labels if provided
    x_label = label_map.get(x_var, x_var) if label_map else x_var
    y_label = label_map.get(y_var, y_var) if label_map else y_var

    # Plot
    sns.boxplot(data=df, x=quartile_col, y=y_var, color='#1f77b4')
    plt.title(f'{y_label} by {x_label} Quartile')
    plt.xlabel(f'{x_label} Quartile')
    plt.ylabel(y_label)
    plt.tight_layout()
    plt.show()
