import streamlit as st
import data_utils

###
# GLOBAL INIT CODE
###
if 'sql_connection' not in st.session_state:
    st.session_state['sql_connection'] = data_utils.get_connection()

###
# PAGE SPECIFIC CODE
###

st.set_page_config(
    page_title="Dashboard Main Page",
    page_icon="🏠",
)

st.markdown("# Brazil Deforestation, Climate, and Land Usage Trends Dashboard 🇧🇷")
st.markdown("## This is the main page of the dashboard")
st.markdown("---")

st.markdown("---")
st.title("Stats at a Glance:")
latest_clim_year = data_utils.get_latest_clim_year(st.session_state['sql_connection'])
latest_co2_emissions = data_utils.get_total_yearly_emissions(st.session_state['sql_connection'], latest_clim_year)
latest_deforestation = data_utils.get_total_yearly_deforestation(st.session_state['sql_connection'], latest_clim_year)
with st.container(border=True):
    st.markdown(f"## Latest full deforestation and CO2 Emision Stats from year {latest_clim_year}:")
    st.markdown(f"### Latest Total CO2 Emissions -")
    st.markdown(f"{latest_co2_emissions} _Tons_")
    st.markdown(f"### Latest Total Deforestation -")
    st.markdown(f"{latest_deforestation} _Acres_")

with st.container(border=True):
    latest_lu_year = data_utils.get_latest_land_year(st.session_state['sql_connection'])
    st.markdown(f"### Average Land Use Percentages from year {latest_lu_year}:")
    land_use_df = data_utils.get_average_yearly_percent_land_usage(st.session_state['sql_connection'], latest_lu_year)
    st.dataframe(land_use_df, hide_index=True)

