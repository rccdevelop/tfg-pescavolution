import dash
from dash import dcc, html, dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date
from utils import get_opensearch_client
from repository import *
import dash_bootstrap_components as dbc
from dash.dash_table.Format import Format, Scheme
from io import StringIO
import json
from pescavolutionApp.models import FiltroUsuario

from django_plotly_dash import DjangoDash

def getColumnsAllData():
  columns= [dict(name='Año', id='year'),
            dict(name='Provincia', id='provincia'),
            dict(name='Establecimiento', id='establecimiento'),
            dict(name='Tipo Especie', id='tipoespecie'),
            dict(name='Especie', id='especie'),
            dict(name='Total Kilos (Kg)', id='kilos', type='numeric', format=Format(precision=2, scheme=Scheme.fixed).group(True)),
            dict(name='Total Euros (€)', id='euros', type='numeric', format=Format(precision=2, scheme=Scheme.fixed).group(True))]
  
  return columns

#Obtener los dashboards existententes en base de datos
dashboards_usuarios = FiltroUsuario.objects.all()

# Conexión con OpenSearch
client = get_opensearch_client()

fechaInicio = "2014-01-01"
fechaFin = "2023-12-31"
# Obtener los datos de ventas según las fechas indicadas
df = obtenerVentas(fechaInicio,fechaFin, client)

df_establecimientos = sorted(df['establecimiento'].unique())
df_provincias = sorted(df['provincia'].unique())
df_tipoespecies = sorted(df['tipoespecie'].unique())
df_especies = sorted(df['especie'].unique())

# Crear distintas consultas para extraer los datos únicos de provincias, establecimientos, especies... para usarlos en los combos (es más rápido así que agrupando el DataFrame entero)

# Obtener provincias y establecimientos únicos
df_distinct_provincias = obtenerEstablecimientos(client)

# Obtener tipos especies y especies únicas
df_distinct_especies = obtenerEspecies(client)

# Usamos la hoja de estilos de BOOTSTRAP para la aplicación Dash
external_stylesheets = [dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP]
#Generar la aplicación con Dash
app = DjangoDash('Dashboard', external_stylesheets = external_stylesheets)

app.layout = dbc.Container([
  html.Div([
    dcc.Input(id='user_id', persistence=False, value="test", style={'display': 'none'}), #Input no visible para guardar el id de usuario autenticado
    dbc.Card([
      dbc.CardHeader("Cargar y Guardar Dashboards"),
        dbc.CardBody([
          dbc.Row(
            [
              dbc.Col([
                html.Div("Cargar Dashboards"),
                dcc.Dropdown(id='filters-dropdown', 
                            options = [{'label': f.nombreFiltro, 'value': f.id} for f in dashboards_usuarios],
                            placeholder="Selecciona un dashboard"),
                html.P(),
                dbc.Button("Cargar Dashboard", color="success", className="me-1", id='btnAplicarFiltro'),
                
              ]),
              dbc.Col([
                html.Div("Guardar Dashboard"),
                dcc.Input(id='filter-name', type='text', placeholder="Introduce nombre del nuevo Dashboard", style={'width': '100%'}),
                html.P(),
                dbc.Button("Guardar Dashboard", color="success", className="me-1", id='save-filter-btn'),
                html.P(),
                html.Div(id='lblSaveFilter')
              ])
            ]
          ),  
        ])
      ], color="success", outline=True),
    ], style={'marginTop': '1', 'marginBottom': '1', 'padding':'1rem', 'margin':'1rem'}),
  html.Div(
    [
      dbc.Card([
        dbc.CardHeader("Filtros"),
        dbc.CardBody([
          html.Div("Por defecto se muestran los datos de los años 2014 a 2023"),
          dbc.Row(
            [
              dbc.Col([html.Label('Rango de fechas:', style={'color': 'green', 'font-size': 20, 'font-weight': 'bold'}), html.Br(),
                       dcc.DatePickerSingle(id="start_date", clearable=True, display_format="YYYY-MM-DD", placeholder="Inicio:", min_date_allowed=date(2000, 1, 1), max_date_allowed=date(2023, 12, 31), initial_visible_month=date(2013, 1, 1)),
                       dcc.DatePickerSingle(id="end_date", clearable=True, display_format="YYYY-MM-DD", placeholder="Fin:", min_date_allowed=date(2000, 1, 1), max_date_allowed=date(2023, 12, 31), initial_visible_month=date(2023, 12, 1))
              ], align="center"),
        
              dbc.Col([html.Label('Provincia:', style={'color': 'green', 'font-size': 20, 'font-weight': 'bold'}),
                dcc.Dropdown(
                      id="provincias",
                      options = [{'label': i, 'value': i} for i in df_provincias],
                      clearable=True,
                      multi = True,
                      style={'color': 'green', 'font-size': 15, 'font-family': 'system-ui'},
                      placeholder="Selecciona Provincia..."
              )], align="center"),
              
              dbc.Col([html.Label('Establecimiento:', style={'color': 'green', 'font-size': 20, 'font-weight': 'bold'}),
                dcc.Dropdown(
                      id="lonjas",
                      clearable=True,
                      multi = True,
                      style={'color': 'green', 'font-size': 15, 'font-family': 'system-ui'},
                      placeholder="Selecciona Establecimiento...",
                      options=[{'label': i, 'value': i} for i in df_establecimientos]
              )], align="center"),
              
              dbc.Col([html.Label('Tipo especie:', style={'color': 'green', 'font-size': 20, 'font-weight': 'bold'}),
                dcc.Dropdown(
                      id="tipoespecies",
                      options = [{'label': i, 'value': i} for i in df_tipoespecies],
                      clearable=True,
                      multi = True,
                      style={'color': 'green', 'font-size': 15, 'font-family': 'system-ui'},
                      placeholder="Selecciona Tipo de Especie..."
              )], align="center"),
              
              dbc.Col([html.Label('Especie:', style={'color': 'green', 'font-size': 20, 'font-weight': 'bold'}),
                dcc.Dropdown(
                      id="especies",
                      clearable=True,
                      multi = True,
                      style={'color': 'green', 'font-size': 15, 'font-family': 'system-ui'},
                      placeholder="Selecciona Especie...",
                      options=[{'label': i, 'value': i} for i in df_especies]
              )], align="center"),
            ]
          )
        ])
      ], color="success", outline=True)
    ], style={'marginTop': '2', 'marginBottom': '2', 'padding':'1rem', 'margin':'1rem'}
  ), 
  html.Div([
    html.Div([
      html.H3(id='textoDefecto'),
      dbc.Row([
        dbc.Col([
          dbc.Card([
            dbc.CardHeader("Resumen"),
            dbc.CardBody([
              dcc.Loading(dcc.Graph(id='line-chart', config={'displayModeBar': False}))  
            ])
          ], color="success", outline=True)
        ], width=10),
        dbc.Col([
          dbc.Card([
            dbc.CardHeader("Totales"),
            dbc.CardBody([
              html.H5('Total Kilos', style={'color': 'green', 'font-size': 20, 'font-weight': 'bold'}, className="card-title"),
              html.P(id='lblTotalKilos', style={'font-size': 18, 'font-weight': 'bold'}),
              html.H5('Total Euros', style={'color': 'green', 'font-size': 20, 'font-weight': 'bold'}, className="card-title"),
              html.P(id='lblTotalEuros', style={'font-size': 18, 'font-weight': 'bold'}),
              html.H5('Precio Medio', style={'color': 'green', 'font-size': 20, 'font-weight': 'bold'}, className="card-title"),
              html.P(id='lblPrecio', style={'font-size': 18, 'font-weight': 'bold'})
            ])
          ], color="success", outline=True)
        ], width=2, align="center")
      ])
    ], style={'marginTop': '5', 'marginBottom': '5', 'padding':'1rem', 'margin':'1rem'}),
    html.Div([
      dbc.Row([
        dbc.Col([
          dbc.Card([
            dbc.CardHeader("Principales especies"),
            dbc.CardBody([
              dcc.Tabs([
                dcc.Tab(label='Según Peso (Kg)', children=[
                  dash_table.DataTable(id='ordenKilos',
                                       columns= [
                                        dict(id='especie', name='Especie'),
                                        dict(id='kilos', name='Total Kilos (Kg)', type='numeric', format=Format(precision=2, scheme=Scheme.fixed).group(True))
                                      ],
                                      style_header={'color': 'white', 'font-size': 15, 'font-family': 'verdana', 'fontWeight': 'bold', 'background':'green'},
                                      style_cell={'padding': '5px', 'textAlign': 'left'},
                                      cell_selectable=True), 
                ]),
                dcc.Tab(label='Según Valor (€)', children=[
                  dash_table.DataTable(id='ordenEuros',
                                      columns= [
                                        dict(id='especie', name='Especie'),
                                        dict(id='euros', name='Total Euros (€)', type='numeric', format=Format(precision=2, scheme=Scheme.fixed).group(True))
                                      ],
                                      style_header={'color': 'white', 'font-size': 15, 'font-family': 'verdana', 'fontWeight': 'bold', 'background':'green'},
                                      style_cell={'padding': '5px', 'textAlign': 'left'})
                ]),
              ], colors={"primary": "green", "border": "white", "background": "#f5fcf1"}, style={'font-weight': 'bold'})
            ])
          ], color="success", outline=True)
        ], width=7),
        dbc.Col([
          dbc.Card([
            dbc.CardHeader("Tipos de Especie"),
            dbc.CardBody([
              dcc.Loading(dcc.Graph(id='pie-chart', config={'displayModeBar': False}, style={'height': '405px'}))
            ])
          ], color="success", outline=True)
        ], width=5)
      ])
    ], style={'marginTop': '5', 'marginBottom': '5', 'padding':'1rem', 'margin':'1rem'}),
    html.Div([
      dbc.Card([
        dbc.CardHeader("Tabla Datos"),
        dbc.CardBody([
          dash_table.DataTable(
            id='tabladatos', 
            # columns=[{'name': i, 'id': i} for i in df.columns],
            columns = getColumnsAllData(),
            style_header={'color': 'white', 'font-size': 15, 'font-family': 'verdana', 'fontWeight': 'bold', 'background':'green'},
            page_size=20,
            fixed_rows={'headers': True},
            style_table={'overflowY': 'auto'}),
          html.Div([
            dbc.Button("Exportar a CSV", color="success", className="me-1", id='btn-export'),
            dcc.Download(id='download-csv')  
          ], className="col d-flex justify-content-center", style={'marginTop': '1', 'marginBottom': '1'})
        ])
      ], color="success", outline=True)
    ], style={'marginTop': '5', 'marginBottom': '5', 'padding':'1rem', 'margin':'1rem'})
    
])], fluid=True)

# Implementación de callback para cargar los dashboards del usuario auntenticado
# @app.callback(
#     dash.dependencies.Output('filters-dropdown', 'options'),
#     dash.dependencies.Input('filters-dropdown', 'value'),
#     dash.dependencies.State('user_id', 'value')
# )
# def cargar_dashboards(value,state_value):
#   filtrosUsuario = FiltroUsuario.objects.filter(usuario_id=state_value)
#   options = [{'label': f.nombreFiltro, 'value': f.id} for f in filtrosUsuario]
#   return options                                  

# @app.callback(
#     dash.dependencies.Output('filter-data-store', 'data'),
#     dash.dependencies.Input('filters-dropdown', 'value')
# )
# def load_filter_data(selected_filter_id):
#   if not selected_filter_id:
#     return {}
    
#   # Buscar el filtro seleccionado
#   user_filter = FiltroUsuario.objects.get(id=selected_filter_id)
#   # Extraer el campo datosFiltro y almacenarlo en el store
#   datos_filtro = json.dumps(user_filter.datosFiltro)
#   datosJSON = json.loads(datos_filtro)
#   provincia = datosJSON.get('provincia', [])
#   establecimiento = datosJSON.get('establecimiento', [])
#   tipoespecie = datosJSON.get('tipoespecie', [])
#   especie = datosJSON.get('especie', [])
#   return datosJSON

# Implementación de callback para cargar el dashboard seleccionado y aplicar los filtros
@app.callback(
    dash.dependencies.Output('provincias', 'value'),
    dash.dependencies.Output('lonjas', 'value'),
    dash.dependencies.Output('tipoespecies', 'value'),
    dash.dependencies.Output('especies', 'value'),
    dash.dependencies.Input('btnAplicarFiltro', 'n_clicks'),
    dash.dependencies.State('filters-dropdown', 'value')
)
def aplicar_filtros_update(n_clicks, filtro_id):
  if n_clicks and filtro_id:
    #Buscamos el dashboard en base de datos
    user_filter = FiltroUsuario.objects.get(id=filtro_id)
    datos_filtro = json.dumps(user_filter.datosFiltro)
    datosJSON = json.loads(datos_filtro)
    provincia = datosJSON.get('provincia', [])
    establecimiento = datosJSON.get('establecimiento', [])
    tipoespecie = datosJSON.get('tipoespecie', [])
    especie = datosJSON.get('especie', [])
    def normalize_value(value):
        if isinstance(value, list):
            return value
        elif value:
            return [value]  # Convierte en lista si es un solo valor
        return None
    return (
        normalize_value(provincia),
        normalize_value(establecimiento),
        normalize_value(tipoespecie),
        normalize_value(especie)
    )
  # raise PreventUpdate #Si no se carga un dashboard, no actualizamos nada

# Callback para guardar los filtros seleccionados por el usuario como un nuevo dashboard
@app.callback(
    dash.dependencies.Output('lblSaveFilter', 'children'),
    dash.dependencies.Output('filters-dropdown', 'options'),
    dash.dependencies.Input('save-filter-btn', 'n_clicks'),
    dash.dependencies.Input('filter-name', 'value'),
    dash.dependencies.State('provincias', 'value'),
    dash.dependencies.State('lonjas', 'value'),
    dash.dependencies.State('tipoespecies', 'value'),
    dash.dependencies.State('especies', 'value'),
    dash.dependencies.State('user_id', 'value')  # Estado para obtener el usuario conectado
)
def save_dashboard(n_clicks, filter_name, selected_provincia,selected_lonja,selected_tipoespecie, selected_especie, user_data):
  if n_clicks:
    
    # Preparar el JSON con los valores de los filtros seleccionados
    datos_filtro = {
      "provincia": selected_provincia or "", # Usar lista vacía si no hay valor seleccionado
      "establecimiento": selected_lonja or "",
      "tipoespecie": selected_tipoespecie or "",
      "especie": selected_especie or "", 
    }
    # Convertir el diccionario a JSON
    datos_filtro_json = json.dumps(datos_filtro)
    datosJSON = json.loads(datos_filtro_json)

    # Crear y guardar el nuevo filtro en la base de datos
    new_filter = FiltroUsuario(
      nombreFiltro=filter_name,
      datosFiltro=datosJSON,
      usuario_id=user_data
    )
    
    new_filter.save()
    
    #actualizar los dashboards seleccionables con el último creado
    dashboards = FiltroUsuario.objects.all()
    options = [{'label': f.nombreFiltro, 'value': f.id} for f in dashboards]

    # Devolver los datos para confirmar que se ha guardado (opcional)
    return "Dashboard creado correctamente",options
  raise PreventUpdate

# Implementación de varios callbacks para hacer que los listados (Dropdowns) se actualicen según el valor seleccionado en el Dropdown anterior

# Provincias y establecimientos
@app.callback(
    dash.dependencies.Output('lonjas', 'options'),
    dash.dependencies.Input('provincias', 'value')
)
def update_lonjas(selected_provincia):
    if selected_provincia is None:
      return [{'label': i, 'value': i} for i in df_establecimientos]
    filtered_df = df_distinct_provincias[df_distinct_provincias['provincia'].isin(selected_provincia)]
    if (len(filtered_df)== 0):
      return [{'label': i, 'value': i} for i in df_establecimientos]
    return [{'label': i, 'value': i} for i in filtered_df['establecimiento']]

# Tipos de especie y especies
@app.callback(
    dash.dependencies.Output('especies', 'options'),
    dash.dependencies.Input('tipoespecies', 'value')
)
def update_especies(selected_tipoespecie):
    if selected_tipoespecie is None:
      return [{'label': i, 'value': i} for i in df_especies]
    filtered_df = df_distinct_especies[df_distinct_especies['tipoespecie'].isin(selected_tipoespecie)]
    if (len(filtered_df)== 0):
      return [{'label': i, 'value': i} for i in df_especies]
    return [{'label': i, 'value': i} for i in filtered_df['especie']]
  
# Callback para exportar los datos a CSV
@app.callback(
    dash.dependencies.Output('download-csv', 'data'),
    dash.dependencies.Input('btn-export', 'n_clicks'),
    dash.dependencies.State('tabladatos', 'data')
)
def generate_csv(n_clicks, data):
    if n_clicks is None:
        return None

    df = pd.DataFrame(data)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    return dict(content=StringIO(csv_string).getvalue(), filename="pescavolution.csv")

# Callback general
@app.callback(
    dash.dependencies.Output('textoDefecto', 'children'),
    dash.dependencies.Output('line-chart', 'figure'),
    dash.dependencies.Output('line-chart', 'style'),
    dash.dependencies.Output('lblTotalKilos', 'children'),
    dash.dependencies.Output('lblTotalEuros', 'children'),
    dash.dependencies.Output('lblPrecio', 'children'),
    dash.dependencies.Output('pie-chart', 'figure'),
    dash.dependencies.Output('pie-chart', 'style'),
    dash.dependencies.Output('ordenKilos', 'data'),
    dash.dependencies.Output('ordenEuros', 'data'),
    dash.dependencies.Output('tabladatos', 'data'),
    dash.dependencies.Input('provincias', 'value'),
    dash.dependencies.Input('lonjas', 'value'),
    dash.dependencies.Input('tipoespecies', 'value'),
    dash.dependencies.Input('especies', 'value'),
    dash.dependencies.Input('start_date', 'date'),
    dash.dependencies.Input('end_date', 'date')
)

def update_graphs(provincias,lonjas,tipoespecies,especies,start_date,end_date):
    # start_date_object = date.fromisoformat(start_date)
    # end_date_object = date.fromisoformat(end_date)
    # diff_dias = end_date - start_date
    # if not selected_lonja:
        # return {}, {}  # Si no se selecciona ninguna lonja, devuelve figuras vacías
    if not provincias and not lonjas and not tipoespecies and not especies:
      return "Selecciona un elemento de los filtros para mostrar resultados",{'data': []},{'visibility': 'hidden'}, "N/A", "N/A", "N/A", {},{'visibility': 'hidden'}, None, None, None
    
    if start_date and end_date:
      df_ventas = obtenerVentas(start_date,end_date, client)
    else:
      df_ventas = df
      
    filtered_df = df_ventas
    
    
    #Filtrar los resultados
    if provincias:
      filtered_df = filtered_df[filtered_df['provincia'].isin(provincias)]
    if lonjas:
      filtered_df = filtered_df[filtered_df['establecimiento'].isin(lonjas)]
    if tipoespecies:
      filtered_df = filtered_df[filtered_df['tipoespecie'].isin(tipoespecies)]
    if especies:
      filtered_df = filtered_df[filtered_df['especie'].isin(especies)]
      
    
    df_years = filtered_df.groupby(['year']).sum().reset_index()
    df_years['precio'] = df_years['euros']/df_years['kilos']
    
    # Obtener los totales y guardarlos formateados para mostrarlos en la página
    fKilos = df_years['kilos'].sum()
    txtKilos = "{:,.2f}".format(fKilos) + " Kg"
    fEuros = df_years['euros'].sum()
    txtEuros = "{:,.2f}".format(fEuros) + " €"
    fPrecio = fEuros/fKilos
    txtPrecio = "{:,.2f}".format(fPrecio) + " €/Kg"
    
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    # fig1 = go.Figure()
    fig1.add_trace(go.Scatter(name='kilos', x=df_years['year'], y=df_years['kilos'], fill="tonexty", mode='lines+markers', line_shape='spline', line=dict(width=3)), secondary_y=False)
    fig1.add_trace(go.Scatter(name='euros', x=df_years['year'], y=df_years['euros'], fill="tonexty", mode='lines+markers', line_shape='spline', line=dict(width=3)), secondary_y=False)
    fig1.add_trace(go.Scatter(name='precio medio', x=df_years['year'], y=df_years['precio'], fill="none", mode='lines+markers', line_shape='spline', line=dict(color='#9614b2', width=3)), secondary_y=True)
    
    # Establecer los títulos de los ejes de coordenadas
    fig1.update_yaxes(title_text="Total de kilos y euros", secondary_y=False)
    fig1.update_yaxes(title_text="Precio medio", secondary_y=True)
    
    #Gráfico de tarta
    fig2 = px.pie(filtered_df.groupby('tipoespecie')['kilos'].sum().reset_index(), values='kilos', names='tipoespecie', hole=0.4)
    
    # Tabla con top 10 especies ordenadas por kilos y euros
    top10Kilos = filtered_df.groupby('especie')['kilos'].sum().sort_values(ascending=False).head(10).reset_index()
    tableKilos = top10Kilos.to_dict('records')
    top10Euros = filtered_df.groupby('especie')['euros'].sum().sort_values(ascending=False).head(10).reset_index()
    tableEuros = top10Euros.to_dict('records')
    #Tabla de datos
    all_data = filtered_df.to_dict('records')
    
    return "", fig1,{}, txtKilos, txtEuros, txtPrecio, fig2,{}, tableKilos, tableEuros, all_data
