from django.shortcuts import render, HttpResponse
from utils import *
from django.conf import settings
import plotly.graph_objects as go
from plotly.offline import plot

import pandas as pd

# Definición de páginas (vistas) de la aplicación.
    
def home(request):
    client = get_opensearch_client()

    # Consulta con agregaciones
    query = {
        "size": 0,
        "aggs": {
            "by_year": {
                "date_histogram": {
                    "field": "fechaventa",
                    "interval": "year",
                    "format": "yyyy"
                },
                "aggs": {
                    "total_kilos": {"sum": {"field": "kilos", "format": "#,###.00"}},
                    "total_euros": {"sum": {"field": "euros", "format": "#,###.00"}}
                }
            }
        }
    }

    # Ejecutar la consulta
    response = client.search(index=settings.OPENSEARCH_INDEX, body=query)

    # Procesar los resultados
    buckets = response['aggregations']['by_year']['buckets']
    years = []
    total_kilos = []
    total_euros = []

    for bucket in buckets:
        year = bucket['key_as_string'] # usar el key_as_string para que muestre el año
        years.append(year)
        total_kilos.append(bucket['total_kilos']['value'])
        total_euros.append(bucket['total_euros']['value'])
        
    # Preparar los datos del gráfico
    trace1 = go.Bar(
        x=years,
        y=total_kilos,
        name='Total Kilos'
    )
    trace2 = go.Bar(
        x=years,
        y=total_euros,
        name='Total Euros'
    )
    
    data = [trace1, trace2]
    
    # Crear un gráfico de líneas
    layout = go.Layout(
        title='Total Kilos y Euros por Año',
        xaxis={'title': 'Año', 'type': 'category'}, #type category para mostrar el título de todos los elementos
        yaxis={'title': 'Total'},
        barmode='group'
    )
    
    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', config={'displayModeBar': False}) #displayModelBar: para desactivar la barra de navegación de plotly


    user_query = "adra"
    query = {
        "size": 5,
        "query": {
            "multi_match": {"query": user_query, "fields": ["establecimiento"]}
        },
    }
    response = client.search(index=settings.OPENSEARCH_INDEX, body=query)
    data = []
    for hit in response["hits"]["hits"]:
        data.append({
            "fechaventa": hit["_source"]["fechaventa"],
            "lonja": hit["_source"]["establecimiento"],
            "especie": hit["_source"]["especie"],
            "kilos": hit["_source"]["kilos"],
            "euros": hit["_source"]["euros"]
    })
        
    df = pd.DataFrame(data)
    # print(pd.unique(df["lonja"]))
    # Pasar los datos agregados al contexto
    context = {
        "data": data,
        "plot_div": plot_div
    }   
    return render(request, 'pescavolutionApp/home.html', context)

def cargaDatos(request):
    if request.method == "POST":
        csv_file = request.FILES["csv_file"]
        cargarCSV(csv_file)
        message = "Datos cargados correctamente."
    else:
        message = "Selecciona un fichero"
        
    return render(request, "pescavolutionApp/cargaDatos.html", {"message": message})

def filtros(request):
    return render(request, "pescavolutionApp/filtros.html")

def agrupaciones(request):
    return render(request, "pescavolutionApp/agrupaciones.html")
