import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt

# Set the layout to wide mode
st.set_page_config(layout="wide")

st.title("Echo Air Emissions Data")

# Load filtered echo air emissions data
poll_rpt_combined_emissions = 'data/filtered_echo_data.csv'
df = pd.read_csv(poll_rpt_combined_emissions, low_memory=False)

# Clean up the data
df.columns = df.columns.str.strip()
df['REGISTRY_ID'] = df['REGISTRY_ID'].astype(str)
df['REPORTING_YEAR'] = df['REPORTING_YEAR'].astype(str)
df = df.where(pd.notnull(df), None)
df['ANNUAL_EMISSION'] = pd.to_numeric(df['ANNUAL_EMISSION'], errors='coerce')
df[['REGISTRY_ID', 'FIPS_CODE', 'EPA_REGION_CODE', 'POSTAL_CODE']] = df[['REGISTRY_ID', 'FIPS_CODE', 'EPA_REGION_CODE', 'POSTAL_CODE']].astype(str)

# Data Selectors and Annual Emissions Information
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Select Data Filters")

    # Get unique program options from the dataset
    available_programs = df['PGM_SYS_ACRNM'].unique()
    default_program_index = list(available_programs).index('E-GGRT') if 'E-GGRT' in available_programs else 0
    selected_program = st.selectbox('Select Program', sorted(available_programs), index=default_program_index)

    # Filter the data by the selected program
    df_program_filtered = df[df['PGM_SYS_ACRNM'] == selected_program]

    # Get unique pollutant options and add "All" option
    available_pollutants = df_program_filtered['POLLUTANT_NAME'].unique()
    pollutant_options = ['All'] + sorted(available_pollutants)
    selected_pollutant = st.selectbox('Select Pollutant Name', pollutant_options)

    # Filter data by pollutant
    df_pollutant_filtered = df_program_filtered if selected_pollutant == 'All' else df_program_filtered[df_program_filtered['POLLUTANT_NAME'] == selected_pollutant]

    # Get the unit of measure for the selected pollutant
    unit_of_measure = df_pollutant_filtered['UNIT_OF_MEASURE'].iloc[0]

    # Define non-continental US states and territories
    non_continental_states = ['HI', 'AK', 'GU', 'VI', 'AS', 'MP', 'PR']
    continental_states = [state for state in df['STATE_CODE'].unique() if state not in non_continental_states]
    continental_states.sort()

    # Add "Continental US" as an option for state selection
    state_options = ['Continental US'] + continental_states
    selected_state = st.selectbox('Select State Code', state_options, index=state_options.index('TX'))

    # Filter data by state or "Continental US"
    df_filtered = df_pollutant_filtered[df_pollutant_filtered['STATE_CODE'].isin(continental_states)] if selected_state == 'Continental US' else df_pollutant_filtered[df_pollutant_filtered['STATE_CODE'] == selected_state]

    # Dropdown for year selection
    years = df_filtered['REPORTING_YEAR'].unique()
    selected_year = st.selectbox('Select Reporting Year', sorted(years))

    # Filter the data by selected year
    df_filtered_year = df_filtered[df_filtered['REPORTING_YEAR'] == selected_year]

    # Dropdown for Top XX facilities
    top_facilities = [5, 10, 25, 50, 100]
    selected_top = st.selectbox('Select Top Facilities', top_facilities, index=top_facilities.index(10))

    # Group by key columns and sum emissions for the selected year
    df_grouped = df_filtered_year.groupby(
        ['REPORTING_YEAR', 'REGISTRY_ID', 'UNIT_OF_MEASURE', 'PRIMARY_NAME', 'CITY_NAME', 'STATE_CODE', 'POSTAL_CODE', 'LATITUDE83', 'LONGITUDE83']
    ).agg({'ANNUAL_EMISSION': 'sum'}).reset_index()

    # Sort by annual emissions and get top XX facilities
    df_top = df_grouped.sort_values(by='ANNUAL_EMISSION', ascending=False).head(selected_top)
    # Store the REGISTRY_IDs of the Top XX facilities
    top_registry_ids = df_top['REGISTRY_ID'].tolist()

    # Calculate total state emissions and total top emissions for the selected year
    total_state_emissions = df_filtered_year['ANNUAL_EMISSION'].sum().round(1)
    total_reporting_facilities = df_filtered_year['REGISTRY_ID'].nunique()
    top_emissions_total = df_top['ANNUAL_EMISSION'].sum().round(1)

    # Calculate the percentage of top XX emissions relative to total state emissions for the selected year
    proportion_from_top = (top_emissions_total / total_state_emissions * 100).round(1) if total_state_emissions > 0 else 0

    # Now rerun annual emissions by year for the original top XX facilities across all years, for the selected program
    df_top_all_years = df[(df['REGISTRY_ID'].isin(top_registry_ids)) & (df['PGM_SYS_ACRNM'] == selected_program)]

    # Group by REPORTING_YEAR and sum emissions for the Top XX facilities across all years (rounding sum)
    df_top_emissions_by_year = df_top_all_years.groupby('REPORTING_YEAR').agg({'ANNUAL_EMISSION': 'sum'}).reset_index()
    df_top_emissions_by_year['ANNUAL_EMISSION'] = df_top_emissions_by_year['ANNUAL_EMISSION'].round(1)

    # Calculate annual emissions totals across the selected state for all years
    df_state_totals_by_year = df_filtered.groupby('REPORTING_YEAR').agg({'ANNUAL_EMISSION': 'sum'}).reset_index()
    df_state_totals_by_year['ANNUAL_EMISSION'] = df_state_totals_by_year['ANNUAL_EMISSION'].round(1)

    # Merge state totals with top XX facilities totals for a combined chart
    df_combined = pd.merge(df_state_totals_by_year, df_top_emissions_by_year, on='REPORTING_YEAR', how='left', suffixes=('_State', f'_Top{selected_top}'))
    df_combined.fillna(0, inplace=True)

    # Ensure 'ANNUAL_EMISSION' is numeric and drop any NaN values for Lorenz Curve calculation
    df_grouped['ANNUAL_EMISSION'] = pd.to_numeric(df_grouped['ANNUAL_EMISSION'], errors='coerce')
    df_grouped_filtered = df_grouped[df_grouped['ANNUAL_EMISSION'] > 0].dropna(subset=['ANNUAL_EMISSION'])
    emissions_array = df_grouped_filtered['ANNUAL_EMISSION'].values

    # Lorenz Curve calculation
    def lorenz_curve(x):
        x = np.sort(x)
        cumulative_values = np.cumsum(x) / np.sum(x)
        cumulative_values = np.insert(cumulative_values, 0, 0)
        cumulative_share = np.linspace(0, 1, len(cumulative_values))
        return cumulative_share, cumulative_values

    cumulative_share, cumulative_values = lorenz_curve(emissions_array)

with col2:
    st.subheader("Summary Statistics")

    # Display Annual Emissions Information
    st.write(f"Total Emissions for '{selected_state}': {total_state_emissions:,} {unit_of_measure}")
    st.write(f"Total Reporting Facilities: {total_reporting_facilities}")
    st.write(f"Total Emissions for the Top {selected_top} Facilities: {top_emissions_total:,} {unit_of_measure}")
    st.write(f"Proportion of Total Emissions from Top {selected_top} Facilities: {proportion_from_top:.1f}%")

# Top XX Facilities and Map
col3, col4 = st.columns([1, 1])

with col3:
    if not df_top.empty:
        # Round ANNUAL_EMISSION to 1 decimal point and add commas
        df_top['ANNUAL_EMISSION'] = df_top['ANNUAL_EMISSION'].map(lambda x: f"{x:,.1f}")
        
        df_display = df_top[['PRIMARY_NAME', 'ANNUAL_EMISSION', 'CITY_NAME', 'STATE_CODE', 'POSTAL_CODE', 'LATITUDE83', 'LONGITUDE83']]
        
        st.subheader(f"Top {selected_top} Facilities for {selected_year} in {selected_state}")
        st.dataframe(df_display.style.hide(axis="index"))
    else:
        st.warning(f"No data available for {selected_year} in {selected_state} for the {selected_program} program.")

with col4:
    st.subheader("Location of Top Facilities")
    # Create and display the map
    df_top['lat'] = pd.to_numeric(df_top['LATITUDE83'], errors='coerce')
    df_top['lon'] = pd.to_numeric(df_top['LONGITUDE83'], errors='coerce')
    df_top = df_top.dropna(subset=['lat', 'lon'])
    zoom_level = 7 if df_top['lat'].std() < 1 and df_top['lon'].std() < 1 else 5

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_top,
        get_position=["lon", "lat"],
        get_radius=5000,
        get_fill_color=[200, 0, 0, 140],
        pickable=True,
    )

    # Add tooltips with the PRIMARY_NAME and CITY_NAME
    tooltip = {
        "html": "<b>Facility:</b> {PRIMARY_NAME}<br/><b>City:</b> {CITY_NAME}, {STATE_CODE} {POSTAL_CODE}<br/><b>Registry ID:</b> {REGISTRY_ID}",
        "style": {
            "backgroundColor": "steelblue",
            "color": "white"
        }
    }

    view_state = pdk.ViewState(latitude=df_top['lat'].mean(), longitude=df_top['lon'].mean(), zoom=zoom_level, pitch=0)
    deck = pdk.Deck(layers=[scatter_layer], initial_view_state=view_state, tooltip=tooltip)
    st.pydeck_chart(deck)

# Line Chart and Lorenz Curve
col5, col6 = st.columns([1, 1])

with col5:
    if not df_combined.empty:
        st.subheader(f"Annual Emissions ({unit_of_measure}): {selected_state} vs Top {selected_top} Facilities")
        st.line_chart(df_combined.set_index('REPORTING_YEAR'))

    else:
        st.warning(f"No emission data found for {selected_state}.")

with col6:
    st.subheader("Emissions Distribution Curve")
 
    # Plot Lorenz curve
    plt.figure(figsize=(8, 6))
    plt.plot(cumulative_share, cumulative_values, label='Lorenz Curve')
    plt.plot([0, 1], [0, 1], linestyle='--', label='Equality Line')
    plt.title("Lorenz Curve of Emissions Distribution")
    plt.xlabel("Cumulative Share of Facilities")
    plt.ylabel("Cumulative Share of Emissions")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)