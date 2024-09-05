from django.conf import settings
import pandas as pd

# Obtener provincias y establecimientos únicos
def obtenerEstablecimientos(client):
    query = {
    "size": 0,
    "aggs": {
        "distinct_provincias": {
        "terms": {
            "field": "provincia.keyword",
            "size": 10
        },
        "aggs": {
            "distinct_establecimientos": {
            "terms": {
                "field": "establecimiento.keyword",
                "size": 50
            }
            }
        }
        }
    }
    }

    response = client.search(index=settings.OPENSEARCH_INDEX, body=query)
    all_data = response['aggregations']['distinct_provincias']['buckets']
    data = []

    for result in all_data:
        provincia = result['key']
        for establecimiento in result['distinct_establecimientos']['buckets']:
            d_establecimiento = establecimiento['key']
            data.append([provincia, d_establecimiento])

    df = pd.DataFrame(data, columns=['provincia', 'establecimiento']).sort_values(by='establecimiento')
    return df

# Obtener tipos especies y especies únicas
def obtenerEspecies(client):
    query = {
    "size": 0,
    "aggs": {
        "distinct_tiposespecies": {
        "terms": {
            "field": "tipoespecie.keyword",
            "size": 5
        },
        "aggs": {
            "distinct_especies": {
            "terms": {
                "field": "especie.keyword",
                "size": 1000
            }
            }
        }
        }
    }
    }

    response = client.search(index=settings.OPENSEARCH_INDEX, body=query)
    all_data = response['aggregations']['distinct_tiposespecies']['buckets']
    data = []

    for result in all_data:
        d_tipoespecie = result['key']
        for especie in result['distinct_especies']['buckets']:
            d_especie = especie['key']
            data.append([d_tipoespecie, d_especie])
        
    df = pd.DataFrame(data, columns=['tipoespecie', 'especie']).sort_values(by='especie')
    return df

#Obtener datos brutos de ventas según fecha de inicio y fin
def obtenerVentas(fechaInicio, fechaFin, client):
    query = {
        "size": 0,
        "query": {
            "range": {
            "fechaventa": {
                "gte": fechaInicio,
                "lte": fechaFin
            }
            }
        }, 
        "aggs": {
            "by_year": {
            "terms": {
                "size": 50,
                "script": {
                "source": "doc['fechaventa'].value.year"
                }
            },
            "aggs": {
                "by_provincia": {
                "terms": {
                    "field": "provincia.keyword",
                    "size": 10
                },
                "aggs": {
                    "by_establecimiento": {
                    "terms": {
                        "field": "establecimiento.keyword",
                        "size": 30
                    },
                    "aggs": {
                        "by_tipoespecie": {
                        "terms": {
                            "field": "tipoespecie.keyword"
                        },
                        "aggs": {
                            "by_especie": {
                            "terms": {
                                "field": "especie.keyword",
                                "size": 1000
                            },
                            "aggs": {
                                "total_kilos": {
                                "sum": {
                                    "field": "kilos"
                                }
                                },
                                "total_euros": {
                                "sum": {
                                    "field": "euros"
                                }
                                }
                            }
                            }
                        }
                        }
                    }
                    }
                }
                }
            }
            }
        }
    }

    response = client.search(index=settings.OPENSEARCH_INDEX, body=query)
    all_data = response['aggregations']['by_year']['buckets']

    #Crear un DataFrame con pandas con los resultados obtenidos
    data = []
    for result in all_data:
        year = result['key']
        for provincia in result['by_provincia']['buckets']:
            tipo_provincia = provincia['key']
            for establecimiento in provincia['by_establecimiento']['buckets']:
                tipo_establecimiento = establecimiento['key']
                for tipoespecie in establecimiento['by_tipoespecie']['buckets']:
                    tipo_especie = tipoespecie['key']
                    for especie in tipoespecie['by_especie']['buckets']:
                        data.append({
                            'year': year,
                            'provincia': tipo_provincia,
                            'establecimiento': tipo_establecimiento,
                            'tipoespecie': tipo_especie,
                            'especie': especie['key'],
                            'kilos': especie['total_kilos']['value'],
                            'euros': especie['total_euros']['value']
                        })
                        
    df = pd.DataFrame(data)
    
    return df

   

