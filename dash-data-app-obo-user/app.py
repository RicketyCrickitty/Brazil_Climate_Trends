import os
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from databricks.sdk.core import Config
import flask  # for request context

# Ensure environment variable is set correctly
assert os.getenv('DATABRICKS_WAREHOUSE_ID'), "DATABRICKS_WAREHOUSE_ID must be set in app.yaml."

# Databricks config
cfg = Config()

# Query the SQL warehouse with the user credentials
def sql_query(query: str) -> pd.DataFrame:
    """Execute a SQL query and return the result as a pandas DataFrame."""
    user_token = flask.request.headers.get('X-Forwarded-Access-Token')
    with sql.connect(
        server_hostname=cfg.host,
        http_path=f"/sql/1.0/warehouses/{cfg.warehouse_id}",
        access_token=user_token  # Pass the user token into the SQL connect to query on behalf of user
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall_arrow().to_pandas()

def load_regions_data() -> pd.DataFrame:
    """Load regions data joined with managers and region types."""
    try:
        query = """
        SELECT 
            r.region_id,
            r.region_name,
            r.region_type,
            rt.description as type_description,
            rt.region_weaknesses,
            rm.m_first_name,
            rm.m_last_name
        FROM brazil_db.mini_world.regions r
        LEFT JOIN brazil_db.mini_world.region_types rt ON r.region_type = rt.region_type
        LEFT JOIN brazil_db.mini_world.region_managers rm ON r.region_id = rm.region_id
        ORDER BY r.region_id
        """
        return sql_query(query)
    except Exception as e:
        print(f"Regions data load failed: {str(e)}")
        return pd.DataFrame()

def load_region_types_data() -> pd.DataFrame:
    """Load region types data."""
    try:
        query = "SELECT * FROM brazil_db.mini_world.region_types"
        return sql_query(query)
    except Exception as e:
        print(f"Region types data load failed: {str(e)}")
        return pd.DataFrame()

def load_land_use_types_data() -> pd.DataFrame:
    """Load land use types data."""
    try:
        query = "SELECT * FROM brazil_db.mini_world.land_use_types ORDER BY land_use_type"
        return sql_query(query)
    except Exception as e:
        print(f"Land use types data load failed: {str(e)}")
        return pd.DataFrame()

# Initialize the Dash app with Bootstrap styling
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout
app.layout = dbc.Container([
    dcc.Store(id='page-load-trigger', data=0),
    dbc.Row([dbc.Col(html.H1("Brazilian Ecological Regions Dashboard"), width=12)], className="mb-4"),
    
    # First row: Region Types Chart and Stats
    dbc.Row([
        dbc.Col([
            html.H4("Region Types Distribution"),
            dcc.Graph(id='region-types-chart', style={'height': '400px'})
        ], width=6),
        dbc.Col([
            html.H4("Key Statistics"),
            html.Div(id='stats-display', style={'padding': '20px'})
        ], width=6)
    ], className="mb-4"),
    
    # Second row: Regions with Managers Table
    dbc.Row([
        dbc.Col([
            html.H4("Regions with Managers and Types"),
            dag.AgGrid(
                id='regions-grid',
                style={'height': '400px'},
                className="ag-theme-alpine"
            )
        ], width=12)
    ], className="mb-4"),
    
    # Third row: Land Use Types
    dbc.Row([
        dbc.Col([
            html.H4("Land Use Types"),
            dag.AgGrid(
                id='land-use-grid',
                style={'height': '400px'},
                className="ag-theme-alpine"
            )
        ], width=12)
    ])
], fluid=True)

# Callback to load data and populate all visualizations
@app.callback(
    Output('region-types-chart', 'figure'),
    Output('stats-display', 'children'),
    Output('regions-grid', 'rowData'),
    Output('regions-grid', 'columnDefs'),
    Output('land-use-grid', 'rowData'),
    Output('land-use-grid', 'columnDefs'),
    Input('page-load-trigger', 'data')
)
def update_visuals(_):
    # Load all data
    regions_data = load_regions_data()
    region_types_data = load_region_types_data()
    land_use_data = load_land_use_types_data()
    
    # Create region types chart
    if not region_types_data.empty:
        fig = px.bar(
            region_types_data,
            x='region_type',
            y=[1] * len(region_types_data),  # Count of 1 for each type
            title='Brazilian Ecological Region Types',
            labels={'region_type': 'Region Type', 'y': 'Count'},
            color='region_type',
            text='region_type'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
    else:
        fig = px.bar(title='No data available')
    
    # Create stats display
    stats = [
        html.Div([
            html.H5(f"Total Regions: {len(regions_data)}"),
            html.H5(f"Total Region Types: {len(region_types_data)}"),
            html.H5(f"Total Land Use Types: {len(land_use_data)}"),
            html.Hr(),
            html.H6("Regions at Risk:"),
            html.Ul([
                html.Li(f"{row['region_type']}: {row['region_weaknesses']}")
                for _, row in region_types_data.iterrows()
                if row['region_weaknesses'] and row['region_weaknesses'].lower() != 'nothing'
            ])
        ])
    ]
    
    # Regions grid configuration
    regions_columns = [
        {"headerName": "Region ID", "field": "region_id", "width": 100},
        {"headerName": "Region Name", "field": "region_name", "width": 150},
        {"headerName": "Region Type", "field": "region_type", "width": 200},
        {"headerName": "Description", "field": "type_description", "width": 250},
        {"headerName": "Weaknesses", "field": "region_weaknesses", "width": 300},
        {"headerName": "Manager First Name", "field": "m_first_name", "width": 150},
        {"headerName": "Manager Last Name", "field": "m_last_name", "width": 150}
    ]
    
    # Land use grid configuration
    land_use_columns = [
        {"headerName": "Land Use Type", "field": "land_use_type", "width": 150},
        {"headerName": "Description", "field": "description", "width": 600}
    ]
    
    return (
        fig,
        stats,
        regions_data.to_dict('records') if not regions_data.empty else [],
        regions_columns,
        land_use_data.to_dict('records') if not land_use_data.empty else [],
        land_use_columns
    )

if __name__ == "__main__":
    app.run(debug=True)