from opensearchpy import OpenSearch, exceptions, helpers
from django.conf import settings
import pandas as pd

# Crear una conexión con Opensearch
def get_opensearch_client():
    # Inicializar el cliente de OpenSearch
    try:
        client = OpenSearch(
            hosts=[{'host': settings.OPENSEARCH_HOST, 'port': settings.OPENSEARCH_PORT}],
            http_auth=settings.OPENSEARCH_AUTH,
            use_ssl=True,  # Cambia esto si no estás usando SSL
            verify_certs=False,  # Cambia esto si necesitas verificar los certificados
            ssl_show_warn=False
        )
        return client   
    except exceptions.ConnectionTimeout as e:
        # Manejar el error de conexión
        print(f"Error connecting to OpenSearch: {e}")
        return None
  
# Cargar fichero CSV en el índice de Opensearch        
def cargarCSV(csv_file):
    index_name = settings.OPENSEARCH_INDEX
    # Leer el archivo CSV con Pandas
    columnas_mapping = mapearColumnas()
    dateFormat = "%d/%m/%Y" # formato Fecha en el fichero CSV
    df = pd.read_csv(csv_file, encoding="utf-8", delimiter=";", parse_dates=['FECHA_VENTA'], date_format=dateFormat)
    # renombrar las columnas tal como las hemos definido en el mapeo, para coincidir con los nombres del índice en Opensearch
    df = df.rename(columns=columnas_mapping)
    # formatear kilos y euros
    df['kilos'] = df['kilos'].str.replace(',','.')
    df['euros'] = df['euros'].str.replace(',','.')
    df['kilos'] = pd.to_numeric(df['kilos'])
    df['euros'] = pd.to_numeric(df['euros'])
    # convertir el DataFrame a un diccionario de documentos OpenSearch
    documentos = df.to_dict(orient="records")
    print("Se van a cargar: " + str(len(documentos)) + " registros")
        
    cliente = get_opensearch_client()
    try:
        res = helpers.bulk(cliente, generadorDatos(df, index_name))
        print("Respuesta: ", res)
    except Exception as e:
        print(e)
        pass
        
# procedimiento auxiliar para mapear los nombres de las columnas del CSV a leer
def mapearColumnas():
    columnas_mapping = {
        "FECHA_VENTA": "fechaventa",
        "PROVINCIA": "provincia",
        "NUMREG": "numreg",
        "ESTABLECIMIENTO": "establecimiento",
        "TIPOESPECIE": "tipoespecie",
        "FAO": "fao",
        "NOMBRE_ESPECIE": "especie",
        "TOTAL_KILOS": "kilos",
        "TOTAL_EUROS": "euros",
    }
    return columnas_mapping

# Generar bloques de datos a cargar en opensearch
def generadorDatos(df, index_name):
    # for c, line in enumerate(df):
    for _,row in df.iterrows():
        yield {
            "_index": index_name,
            "_source": row.to_dict()
        }


          