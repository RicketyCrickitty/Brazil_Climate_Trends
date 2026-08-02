import pandas as pd
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config
import os

assert "DBX_SQL_WAREHOUSE" in os.environ, "DBX_SQL_WAREHOUSE is not set! Required for querying data!"
sql_warehouse_id = os.getenv("DBX_SQL_WAREHOUSE")

cfg = Config()

# Use app service principal authentication
def get_connection():
    server_hostname = cfg.host
    if server_hostname.startswith('https://'):
        server_hostname = server_hostname.replace('https://', '')
    elif server_hostname.startswith('http://'):
        server_hostname = server_hostname.replace('http://', '')
    return sql.connect(
        server_hostname=server_hostname,
        http_path=f'/sql/1.0/warehouses/{sql_warehouse_id}',
        credentials_provider=lambda: cfg.authenticate,
        _use_arrow_native_complex_types=False,
    )

# Read data from a Unity Catalog table and return it as a pandas DataFrame
def read_table(table_name: str, conn) -> pd.DataFrame:
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall_arrow().to_pandas()

table_name = st.text_input(
    "Specify a Unity Catalog table name:", placeholder="catalog.schema.table"
)

# Display the result in a Streamlit DataFrame
if table_name:
    conn = get_connection()
    df = read_table(table_name, conn)
    st.dataframe(df)
else:
    st.warning("Provide both the warehouse path and a table name to load data.")