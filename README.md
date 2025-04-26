# Agency Structure, Community Demographics, and the Use of Lethal Force: A Multi-Source State-Level Analysis

## Motivation

The use of lethal force by law enforcement remains a central concern in discussions around policing in the United States. While many analyses focus on individual incidents or large-scale trends, fewer have explored how internal police agency characteristics—such as training hours, gender composition, and accountability structures—might correlate with use-of-force outcomes across communities, particularly when controlling for local population and socioeconomic factors.

Our project aims to investigate whether and how agency-level organizational factors contribute to county-level differences in lethal force incidents, as recorded in publicly available datasets.

## Hypotheses

- **Hypothesis 1**: Counties with police agencies that have a higher proportion of female officers will have a lower average count of lethal force incidents per year.
- **Hypothesis 2**: Agencies with a civilian complaint board have significantly fewer yearly lethal force incidents than those without.
- **Hypothesis 3**: Police agencies with a higher proportion of minority officers (Black, Latino) are less likely to be involved in lethal force incidents.
- **Hypothesis 4**: The relationships described in H1–H3 will be stronger in 2020 than in 2016, reflecting the increasing impact of organizational accountability measures over time.

## Data Sources

The SPOTLITE database provides data at the county level, while LEMAS provides data at the agency level. To enable comparison, we first need to aggregate both datasets to the **state level**. We will focus on the years **2016** and **2020**, as these are the only years with complete and valid data across both sources.

### 1. SPOTLITE Database (Cline Center, UIUC)

- **Source**: [SPOTLITE Data](https://clinecenter.illinois.edu/spotlite/data)
- **Data Span**: 2014–2021
- **Fields**: Incident date, county/state identifiers, type of force, metadata from multiple reporting sources.

### 2. LEMAS (Law Enforcement Management and Administrative Statistics) Survey

- **Years**: 2013, 2016, 2020
- **Fields**:
  - % female officers
  - Total sworn personnel
  - In-service training hours
  - Civilian complaint board existence
  - Overtime restrictions (if available)

> **Note**: Variable coding is inconsistent across survey years, but the desired information is available for all three waves.

### 3. U.S. Census and Labor Statistics (for contextual normalization and control variables)

- **Years**: 2016 & 2020
- **Source**: [Census Data](https://data.census.gov/table/ACSST1Y2023.S1902?q=United+States&t=Income+(Households,+Families,+Individuals)&g=010XX00US,$0400000)
- **Fields**:
  - Resident population size (per capita normalization)
  - Median household income
  - Race/ethnicity proportions

> **Note**: These measures will be extracted from multiple relevant tables to match the SPOTLITE and LEMAS data.
