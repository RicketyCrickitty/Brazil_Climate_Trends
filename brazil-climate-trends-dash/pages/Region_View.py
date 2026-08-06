import streamlit as st
import pandas as pd
from datetime import datetime
import data_utils
from data_utils import get_region_list, get_region_id_from_name, get_region_info

###
# GLOBAL INIT CODE
###
if 'sql_connection' not in st.session_state:
    st.session_state['sql_connection'] = data_utils.get_connection()

###
# PAGE SPECIFIC CODE
###
st.set_page_config(
    page_title="Regional Viewer Page",
    page_icon="🔍",
)

# Information Zone
regions = get_region_list(st.session_state['sql_connection'])
region_name = st.selectbox('region_select', regions)

region_id = get_region_id_from_name(st.session_state['sql_connection'], region_name)
st.write(f'You chose: {region_name}, see below for info')
st.dataframe(get_region_info(st.session_state['sql_connection'], region_id), hide_index=True)

st.title('Latest Climate Markers')
min_clim_year = data_utils.get_min_climate_marker_year(st.session_state['sql_connection'], region_id)
max_clim_year = data_utils.get_max_climate_marker_year(st.session_state['sql_connection'], region_id)
st.header(f'Data available from {min_clim_year} to {max_clim_year}')
latest_climate_df = data_utils.get_latest_region_markers(st.session_state['sql_connection'], region_id)
st.dataframe(latest_climate_df, hide_index=True)

st.title('Latest Land Usage')
min_lu_year = data_utils.get_min_land_usage_year(st.session_state['sql_connection'], region_id)
max_lu_year = data_utils.get_max_land_usage_year(st.session_state['sql_connection'], region_id)
st.header(f'Data available from {min_lu_year} to {max_lu_year}')
latest_land_df = data_utils.get_latest_region_land_use(st.session_state['sql_connection'], region_id)
st.dataframe(latest_land_df, hide_index=True)

# Input Container
with st.container(border=True):

    st.title('Input More Data:')
    # Input Choices
    input_choice = st.radio(
        "What would you like to input?",
        [":star: Nothing :star:", "Climate Marker :earth_americas:", "Land Usage :seedling:"],
        captions=[
            "Nothing to input!",
            "CO2 and Deforestation",
            "Land Use by Type",
        ],
    )

    if input_choice == "Climate Marker :earth_americas:":
        # Input Zone
        st.title('Yearly Climate Marker Input')
        with st.form("region_climate_marker_yearly_input"):

            # Grab region_id from above
            # year
            MIN_YEAR = 1900
            MAX_YEAR = int(datetime.today().year)
            year = st.number_input('year', value=MAX_YEAR, max_value=MAX_YEAR, 
                            min_value=MIN_YEAR, help='year for input', step=1)
            # co2 emission
            co2 = st.number_input('CO2-Emissions', value=0.0, min_value=0.0, max_value=999.999, step=0.0001,
                            help='CO2-Emissions in metric tons')
            # deforestation
            deforest = st.number_input('Deforestation Acres', value=0.0, min_value=0.0, max_value=999.999, step=0.0001,
                            help='Deforestation in Acres')
            cm_submit = st.form_submit_button("Add Yearly Climate Data")

        if cm_submit:
            st.write('Inserting data...')
            data_utils.insert_climate_marker(st.session_state['sql_connection'], df)
            st.rerun()

        st.title('Yearly Climate Marker Delete')
        with st.form("region_climate_marker_yearly_delete"):

            # Grab region_id from above
            # year
            MIN_YEAR = 1900
            MAX_YEAR = int(datetime.today().year)
            year = st.number_input('year', value=MAX_YEAR, max_value=MAX_YEAR, 
                            min_value=MIN_YEAR, help='year for input', step=1)
            delete_cm_submit = st.form_submit_button("Delete Yearly Climate Data")

        if delete_cm_submit:
            st.write('Deleting data...')
            data_utils.delete_climate_marker(st.session_state['sql_connection'], region_id, year)
            st.rerun()

    elif input_choice == "Land Usage :seedling:":
        # Input Zone
        st.title('Yearly Land Usage Input')
        with st.form("region_land_usage_yearly_input"):

            # Grab region_id from above
            # year
            MIN_YEAR = 1900
            MAX_YEAR = int(datetime.today().year)
            year = st.number_input('year', value=MAX_YEAR, max_value=MAX_YEAR, 
                            min_value=MIN_YEAR, help='year for input', step=1)
            
            land_use_descs = data_utils.get_land_use_type_descriptions(st.session_state['sql_connection'])
            # Input every single land type at once:
            land_usages = {
                data_utils.get_land_use_type_From_desc(st.session_state['sql_connection'], land_use_desc):
                    st.number_input(f'{land_use_desc}', value=0.0, min_value=0.0, 
                            max_value=100.0, step=0.01, key=f'{land_use_desc}_input')
                for land_use_desc in land_use_descs
            } # Dict of land_use_type: percent
            
            
            lu_submit = st.form_submit_button("Add Yearly Land Use Data")

        if lu_submit:
            st.write('Inserting data...')
            for land_use_type, land_use_percent in land_usages.items():
                df = {
                    'region_id': int(region_id),
                    'year': int(year),
                    'land_use_type': land_use_type,
                    'percent': float(land_use_percent),
                }
                data_utils.insert_land_usage(st.session_state['sql_connection'], df)
            st.rerun()

        st.title('Yearly Land Usage Delete')
        with st.form("region_land_usage_yearly_delete"):

            # Grab region_id from above
            # year
            MIN_YEAR = 1900
            MAX_YEAR = int(datetime.today().year)
            year = st.number_input('year', value=MAX_YEAR, max_value=MAX_YEAR, 
                            min_value=MIN_YEAR, help='year for input', step=1)
            delete_lu_submit = st.form_submit_button("Delete Yearly Land Usage Data")

        if delete_lu_submit:
            st.write('Deleting data...')
            data_utils.delete_land_usage(st.session_state['sql_connection'], region_id, year)
            st.rerun()

    else:
        pass


