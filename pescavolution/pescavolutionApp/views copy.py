from django.shortcuts import render, HttpResponse
from utils import get_opensearch_client
from django.conf import settings


# Definición de páginas (vistas) de la aplicación.

    
def home(request):
    client = get_opensearch_client()

    # Realizar una búsqueda en el índice
    user_query = "adra"
    query = {
        "size": 5,
        "query": {
            "multi_match": {"query": user_query, "fields": ["lonja"]}
        },
    }
    
    response = client.search(index=settings.OPENSEARCH_INDEX, body=query)
    
    print(response)
    
    # Procesar los resultados de la búsqueda y extraer los datos que nos interesan
    data = []
    for hit in response["hits"]["hits"]:
        data.append({
            "anio": hit["_source"]["anio"],
            "lonja": hit["_source"]["lonja"],
            "especie": hit["_source"]["especie"],
            "kilos": hit["_source"]["kilos"],
            "euros": hit["_source"]["euros"]
    })

    print (data)
    
    # Pasar la lista de datos al contexto
    context = {
        "data": data
    }
    return render(request, 'pescavolutionApp/home.html', context,)
