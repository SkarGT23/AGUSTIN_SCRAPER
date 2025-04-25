import feedparser

def obtener_ofertas_tecnoempleo_rss(palabra_clave='python', ubicacion='', puesto='', empresa='', salario='', tecnologia=''):
    # Puedes adaptar el feed RSS según la tecnología/keyword si Tecnoempleo lo permite
    # Ejemplo de feed general: https://www.tecnoempleo.com/rss/empleo-tecnologias.xml
    feed_url = 'https://www.tecnoempleo.com/rss/empleo-tecnologias.xml'
    d = feedparser.parse(feed_url)
    ofertas = []
    for entry in d.entries:
        # Se buscan los campos en el título y descripción
        titulo = entry.title if hasattr(entry, 'title') else ''
        descripcion = entry.summary if hasattr(entry, 'summary') else ''
        autor = entry.get('author', '')
        ubicacion_rss = entry.get('location', '')
        publicado = entry.get('published', '')
        # Filtros: todos los campos deben coincidir si están presentes
        if palabra_clave and palabra_clave.lower() not in titulo.lower() and palabra_clave.lower() not in descripcion.lower():
            continue
        if puesto and puesto.lower() not in titulo.lower() and puesto.lower() not in descripcion.lower():
            continue
        if empresa and empresa.lower() not in autor.lower() and empresa.lower() not in titulo.lower() and empresa.lower() not in descripcion.lower():
            continue
        if ubicacion and ubicacion.lower() not in ubicacion_rss.lower() and ubicacion.lower() not in descripcion.lower():
            continue
        if tecnologia and tecnologia.lower() not in titulo.lower() and tecnologia.lower() not in descripcion.lower():
            continue
        # El salario no suele estar en RSS, pero si el usuario lo introduce, intentamos filtrar por texto
        if salario:
            if salario not in titulo and salario not in descripcion:
                continue
        ofertas.append({
            'titulo': titulo,
            'empresa': autor,
            'ubicacion': ubicacion_rss,
            'salario': '',
            'tecnologia': tecnologia if tecnologia else '',
            'fecha_publicacion': publicado,
            'url_oferta': entry.link,
            'portal': 'Tecnoempleo (RSS)'
        })
    return ofertas
