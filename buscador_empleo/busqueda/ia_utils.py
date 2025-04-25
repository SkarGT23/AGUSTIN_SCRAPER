import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from datetime import datetime
import pandas as pd

# --- RECOMENDACIÓN DE OFERTAS SEGÚN HABILIDADES ---
def recomendar_ofertas(usuario_habilidades, ofertas):
    '''
    usuario_habilidades: lista de strings con habilidades del usuario
    ofertas: lista de dicts con clave 'titulo', 'habilidades', etc
    Retorna: lista ordenada de ofertas recomendadas
    '''
    vectorizer = CountVectorizer().fit([" ".join(usuario_habilidades)] + [" ".join(o.get('habilidades', [])) for o in ofertas])
    user_vec = vectorizer.transform([" ".join(usuario_habilidades)])
    ofertas_vecs = vectorizer.transform([" ".join(o.get('habilidades', [])) for o in ofertas])
    sims = cosine_similarity(user_vec, ofertas_vecs)[0]
    ofertas_recomendadas = [ofertas[i] for i in np.argsort(sims)[::-1]]
    return ofertas_recomendadas

# --- PREDICCIÓN DE TENDENCIAS DE HABILIDADES ---
def predecir_tendencia_habilidades(ofertas_historicas):
    '''
    ofertas_historicas: lista de dicts con 'fecha_publicacion', 'habilidades'
    Retorna: pandas DataFrame con tendencia de habilidades por mes
    '''
    data = []
    for oferta in ofertas_historicas:
        fecha = oferta.get('fecha_publicacion')
        if not fecha:
            continue
        if isinstance(fecha, str):
            fecha = fecha[:7]  # yyyy-mm
        habilidades = oferta.get('habilidades', [])
        for hab in habilidades:
            data.append({'mes': fecha, 'habilidad': hab})
    df = pd.DataFrame(data)
    # Protección: si no hay datos o columnas necesarias
    if df.empty or not set(['mes', 'habilidad']).issubset(df.columns):
        return pd.DataFrame()  # DataFrame vacío seguro
    try:
        tendencia = df.groupby(['mes', 'habilidad']).size().unstack(fill_value=0)
    except Exception:
        tendencia = pd.DataFrame()
    return tendencia
