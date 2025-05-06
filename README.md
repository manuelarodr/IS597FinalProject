# Agency Structure, Community Demographics, and the Use of Lethal Force: A Multi-Source State-Level Analysis

## Motivation

The use of lethal force by law enforcement remains a central concern in discussions around policing in the United States. While many analyses focus on individual incidents or large-scale trends, fewer have explored how internal police agency characteristics—such as training hours, gender composition, and accountability structures—might correlate with use-of-force outcomes across communities, particularly when controlling for local population and socioeconomic factors.

Our project aims to investigate whether and how agency-level organizational factors contribute to state-level differences in lethal force incidents, as recorded in publicly available datasets.

## Hypotheses

- **Hypothesis 1**: States that have a higher proportion of female officers will have a less lethal force incidents per year.
- **Hypothesis 2**: States that have a higher proportion of minority officers (Black, Latino) are less likely to be involved in lethal force incidents.
- **Hypothesis 3**: States where a greater share of officers are employed in agencies with a civilian complaint review board will have a less lethal force incidents per year.
- **Hypothesis 4**: The relationships described in H1–H3 will be stronger in 2020 than in 2016, reflecting the increasing impact of organizational accountability measures over time.

## Data Sources

The SPOTLITE database provides data at the county level, while LEMAS provides data at the agency level. To enable comparison, we first need to aggregate both datasets to the **state level**. We will focus on the years **2016** and **2020**, as these are the only years with complete and valid data across both sources.

### 1. SPOTLITE Database (Cline Center, UIUC)

- **Source**: [SPOTLITE Data](https://clinecenter.illinois.edu/spotlite/data)
- **Data Span**: 2014–2021
- **Fields**: Incident date, county/state identifiers, type of force, metadata from multiple reporting sources.

### 2. LEMAS (Law Enforcement Management and Administrative Statistics) Survey

- **Years**: 2016 and 2020
- **Fields**:
  - Full-time sworn personel demographics
  - Civilian complaint board existence


### 3. U.S. Census and Labor Statistics (for contextual normalization and control variables)

- **Years**: 2016 & 2020
- **Source**: [Census Data](https://data.census.gov/table/ACSST1Y2023.S1902?q=United+States&t=Income+(Households,+Families,+Individuals)&g=010XX00US,$0400000)
- **Fields**:
  - Resident population size (per capita normalization)
  - Median household income
  - Race/ethnicity proportions

> **Note**: These measures will be extracted from multiple relevant tables to match the SPOTLITE and LEMAS data.

## Data Preparation

To enable state-level analysis across different data sources, we conducted a series of preprocessing steps to ensure consistency, reliability, and alignment with our research goals.

First, we aggregated the SPOTLITE incident data from the county level to the state level for 2016 and 2020. For each state-year pair, we computed the total number of lethal force incidents. We reshaped the dataset into a long format, where each row represents a specific state in a specific year, allowing easier integration with other datasets.

Second, from the LEMAS survey data, we extracted agency-level organizational characteristics, including the percentage of female officers, the existence of a civilian complaint board, and the proportion of minority officers. We then aggregated these attributes to the state level by calculating weighted averages, using the number of sworn personnel as the weighting factor to reflect the relative size of agencies within each state.

Third, we obtained population size and crime incident counts for each state and year from U.S. Census and FBI UCR/NIBRS datasets. We matched these contextual variables with the SPOTLITE and LEMAS data by state and year identifiers.

To control for differences in population size and crime environment, we computed two normalized outcome variables for each state-year observation:
- **Lethal force incidents per 100,000 residents**, using the state’s population as the denominator.
- **Lethal force incidents per 1,000 crime incidents**, using the state's total reported crime incidents as the denominator.

By using both normalization strategies, we aim to control for the varying population sizes and baseline levels of crime across states, providing a more nuanced and robust assessment of how agency structure relates to the use of lethal force.

All datasets were merged based on state identifiers and year, with careful attention to missing data and consistency across sources.
