from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from utils import *
from django.conf import settings
import plotly.graph_objects as go
from plotly.offline import plot
from .models import FiltroUsuario
import json

import pandas as pd

# Definición de páginas (vistas) de la aplicación.
    
def home(request):
    return render(request, 'pescavolutionApp/home.html', {'user_id': request.user.id,
                                                          "dash_context": {"user_id": {"value": request.user.id}
                                                                           }})

def cargaDatos(request):
    if request.method == "POST":
        csv_file = request.FILES["csv_file"]
        cargarCSV(csv_file)
        message = "Datos cargados correctamente."
    else:
        message = "Selecciona un fichero"
        
    return render(request, "pescavolutionApp/cargaDatos.html", {"message": message})

# Definición de la vista "Mis Filtros"
def misFiltros(request):
    filtros_usuario = FiltroUsuario.objects.filter(usuario=request.user)
    return render(request, 'pescavolutionApp/misFiltros.html', {'filtros_usuario': filtros_usuario})

# Exportar filtro a JSON
def export_filter(request, filter_id):
    user_filter = get_object_or_404(FiltroUsuario, id=filter_id, usuario=request.user)
    response = HttpResponse(json.dumps(user_filter.datosFiltro), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename={user_filter.nombreFiltro}.json'
    return response

# Importar filtro desde un archivo JSON
def import_filter(request):
    if request.method == 'POST':
        try:
            json_file = request.FILES.get('json_file')
            filter_data = json.load(json_file)
            filter_name = request.POST.get('nombreFiltro')
            FiltroUsuario.objects.create(usuario=request.user, nombreFiltro=filter_name, datosFiltro=filter_data)
            return redirect ('/misFiltros')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Archivo JSON inválido'}, status=400)
    return JsonResponse({'message': 'Método no permitido'}, status=405)


