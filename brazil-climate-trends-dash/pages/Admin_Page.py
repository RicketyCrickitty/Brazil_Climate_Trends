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

st.markdown("# !! WARNING: ADMIN ONLY - USED FOR MANAGER MANAGEMENT !!")
st.markdown("---")
st.markdown("## Use at your own risk")

with st.container(border=True):
    st.markdown('### Regions with Managers:')
    df = data_utils.get_regions_with_managers(st.session_state['sql_connection'])
    st.dataframe(df, hide_index=True)

with st.form('Manager Update Form'):
    st.markdown('**Update Managers Here**')
    regions = data_utils.get_region_list(st.session_state['sql_connection'])
    region_name = st.selectbox('region_select', regions)
    region_id = data_utils.get_region_id_from_name(st.session_state['sql_connection'], region_name)
    m_first_name = st.text_input('manager_first_name')
    m_last_name = st.text_input('manager_last_name')
    m_submit = st.form_submit_button("Update Region Manager")

    if m_submit:
        data_utils.update_region_manager(st.session_state['sql_connection'], region_id, m_first_name, m_last_name)
        st.rerun()
