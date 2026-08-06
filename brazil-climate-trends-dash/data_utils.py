from databricks import sql
from databricks.sdk.core import Config
import pandas as pd
import os


assert "DBX_SQL_WAREHOUSE" in os.environ, "DBX_SQL_WAREHOUSE is not set! Required for querying data!"
sql_warehouse_id = os.getenv("DBX_SQL_WAREHOUSE")

regions_table = os.getenv('REGIONS_TABLE')
region_managers_table = os.getenv('REGION_MANAGERS_TABLE')
region_types_table = os.getenv('REGION_TYPES_TABLE')
land_use_types_table = os.getenv('LAND_USE_TYPES_TABLE')
land_usage_table = os.getenv('LAND_USAGE_TABLE')
climate_markers_table = os.getenv('CLIMATE_MARKERS_TABLE')

cfg = Config()

def get_connection():
    sql_connection = sql.connect(
            server_hostname=cfg.host,
            http_path=f'/sql/1.0/warehouses/{sql_warehouse_id}',
            credentials_provider=lambda: cfg.authenticate,
            _use_arrow_native_complex_types=False,
    )
    return sql_connection
    

    

# Read data from a Unity Catalog table and return it as a pandas DataFrame
def sql_query(conn, query: str) -> pd.DataFrame:
    with conn.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall_arrow().to_pandas()

###
# READ FUNCTIONS
###

def get_regions_with_managers(conn) -> pd.DataFrame:
    query = f"""
    select r.region_id, region_name, region_type, concat_ws(' ', m_first_name, m_last_name) as manager
    from {regions_table} r
    join {region_managers_table} m on r.region_id = m.region_id
    order by region_id asc
    """
    df = sql_query(conn, query)
    return df

def get_region_list(conn) -> list[str]:
    df = sql_query(conn, f"SELECT region_name FROM {regions_table}")
    return df['region_name'].tolist()

def get_region_id_from_name(conn, region_name) -> str:
    df = \
    sql_query(conn, f"SELECT region_id FROM {regions_table} WHERE region_name = '{region_name}'")
    return df['region_id'].tolist()[0]

def get_region_info(conn, region_id) -> pd.DataFrame:
    query = f"""
    select r.region_id, region_name, r.region_type, concat_ws(' ', m_first_name, m_last_name) as manager,
    t.description, t.region_weaknesses
    from {regions_table} r
    join {region_managers_table} m on r.region_id = m.region_id
    join {region_types_table} t on r.region_type = t.region_type
    where r.region_id = '{region_id}'
    """
    return sql_query(conn, query)

def get_land_use_type_descriptions(conn) -> list[str]:
    df = sql_query(conn, f"SELECT description FROM {land_use_types_table}")
    return df['description'].tolist()

def get_land_use_type_From_desc(conn, desc) -> str:
    df = sql_query(conn, f"SELECT land_use_type FROM {land_use_types_table} WHERE description = '{desc}'")
    return df['land_use_type'].tolist()[0]

def get_latest_region_markers(conn, region_id) -> pd.DataFrame:
    query = f"""
    select year, region_id, co2_emission, deforestation
    from {climate_markers_table}
    where region_id = '{region_id}'
    order by year desc
    limit 5
    """
    return sql_query(conn, query)

def get_latest_region_land_use(conn, region_id) -> pd.DataFrame:
    query = f"""
    select year, region_id, lut.description as land_use, percent
    from {land_usage_table} lu
    join {land_use_types_table} lut on lu.land_use_type = lut.land_use_type
    where region_id = '{region_id}'
    and lu.year = (select max(year) as year from {land_usage_table})
    """
    return sql_query(conn, query)

def get_min_climate_marker_year(conn, region_id) -> int:
    query = f"""
    select min(year) from {climate_markers_table}
    where region_id = '{region_id}'
    """
    df = sql_query(conn, query)
    return df['min(year)'].tolist()[0]

def get_max_climate_marker_year(conn, region_id) -> int:
    query = f"""
    select max(year) from {climate_markers_table}
    where region_id = '{region_id}'
    """
    df = sql_query(conn, query)
    return df['max(year)'].tolist()[0]

def get_min_land_usage_year(conn, region_id) -> int:
    query = f"""
    select min(year) from {land_usage_table}
    where region_id = '{region_id}'
    """
    df = sql_query(conn, query)
    return df['min(year)'].tolist()[0]

def get_max_land_usage_year(conn, region_id) -> int:
    query = f"""
    select max(year) from {land_usage_table}
    where region_id = '{region_id}'
    """
    df = sql_query(conn, query)
    return df['max(year)'].tolist()[0]

def get_total_yearly_emissions(conn, year) -> int:
    query = f"""
    select sum(co2_emission) as total_emissions
    from {climate_markers_table}
    where year = {year}
    """
    df = sql_query(conn, query)
    return df['total_emissions'].tolist()[0]

def get_total_yearly_deforestation(conn, year) -> int:
    query = f"""
    select sum(deforestation) as total_deforestation
    from {climate_markers_table}
    where year = {year}
    """
    df = sql_query(conn, query)
    return df['total_deforestation'].tolist()[0]

def get_average_yearly_percent_land_usage(conn, year) -> pd.DataFrame:
    query = f"""
    select lut.description, sum(lu.percent)/9 as average_percent
    from {land_usage_table} lu
    join {land_use_types_table} lut on lu.land_use_type = lut.land_use_type
    where year = {year}
    group by lut.description
    """
    df = sql_query(conn, query)
    return df

def get_latest_clim_year(conn) -> int:
    query = f"""
    select min(sub.year) as latest_total_year 
    from
    (select max(year) as year, region_id from {climate_markers_table} group by region_id) as sub
    """
    df = sql_query(conn, query)
    return df['latest_total_year'].tolist()[0]

def get_latest_land_year(conn) -> int:
    query = f"""
    select min(sub.year) as latest_total_year 
    from
    (select max(year) as year, region_id from {land_usage_table} group by region_id) as sub
    """
    df = sql_query(conn, query)
    return df['latest_total_year'].tolist()[0]

###
# WRITE FUNCTIONS
###

def insert_climate_marker(conn, row_df):
    query = f"""
    insert into {climate_markers_table} (year, region_id, co2_emission, deforestation)
    values ({row_df['year']}, '{row_df['region_id']}', {row_df['co2_emission']}, {row_df['deforestation']})
    """
    sql_query(conn, query)

def insert_land_usage(conn, row_df):
    query = f"""
    insert into {land_usage_table} (year, region_id, land_use_type, percent)
    values ({row_df['year']}, '{row_df['region_id']}', '{row_df['land_use_type']}', {row_df['percent']})
    """
    sql_query(conn, query)

def update_region_manager(conn, region_id, m_first_name, m_last_name):
    query = f"""
    update {region_managers_table}
    set m_first_name = '{m_first_name}', m_last_name = '{m_last_name}'
    where region_id = '{region_id}'
    """
    sql_query(conn, query)

###
# DELETE FUNCTIONS
###
def delete_climate_marker(conn, region_id, year):
    query = f"""
    delete from {climate_markers_table}
    where year = {year} and region_id = '{region_id}'
    """
    sql_query(conn, query)

def delete_land_usage(conn, region_id, year):
    query = f"""
    delete from {land_usage_table}
    where year = {year} and region_id = '{region_id}'
    """
    sql_query(conn, query)

