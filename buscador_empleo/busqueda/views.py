from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


from .scraping import obtener_ofertas_infojobs, obtener_ofertas_tecnoempleo, obtener_ofertas_linkedin
from .models import OfertaLaboral

from django.contrib.auth import logout

from .scraping_linkedin import obtener_ofertas_linkedin
from .scraping_infojobs import obtener_ofertas_infojobs
from .scraping_tecnoempleo import obtener_ofertas_tecnoempleo_alternativo

from .models import OfertaLaboral, NotaPersonal, Habilidad
from .ia_utils import recomendar_ofertas, predecir_tendencia_habilidades
import base64
import matplotlib.pyplot as plt
from io import BytesIO

from django.utils import timezone
from django.http import HttpResponseRedirect

@login_required
def calendario(request):
    usuario = request.user
    notas = NotaPersonal.objects.filter(usuario=usuario).order_by('-fecha')
    mensaje = ''
    # Crear o editar nota
    if request.method == 'POST':
        nota_id = request.POST.get('nota_id')
        fecha = request.POST.get('fecha')
        texto = request.POST.get('nota')
        if 'eliminar' in request.POST:
            # Eliminar nota
            if nota_id:
                NotaPersonal.objects.filter(id=nota_id, usuario=usuario).delete()
                mensaje = 'Nota eliminada.'
        elif nota_id:
            # Editar nota existente
            nota = NotaPersonal.objects.get(id=nota_id, usuario=usuario)
            nota.fecha = fecha
            nota.texto = texto
            nota.save()
            mensaje = 'Nota actualizada.'
        elif fecha and texto:
            # Crear nueva
            NotaPersonal.objects.create(usuario=usuario, fecha=fecha, texto=texto)
            mensaje = 'Nota guardada.'
        return HttpResponseRedirect(request.path_info)
    # Generar calendario del mes actual
    import calendar
    from datetime import date
    hoy = date.today()
    cal = calendar.Calendar(firstweekday=0)  # Lunes
    mes = hoy.month
    anio = hoy.year
    semanas = cal.monthdayscalendar(anio, mes)
    # Crear un dict {dia: [notas]}
    notas_por_dia = {}
    for nota in notas:
        if nota.fecha.month == mes and nota.fecha.year == anio:
            d = nota.fecha.day
            if d not in notas_por_dia:
                notas_por_dia[d] = []
            notas_por_dia[d].append(nota.texto)
    return render(request, 'calendario.html', {
        'notas': notas,
        'mensaje': mensaje,
        'calendario': semanas,
        'notas_por_dia': notas_por_dia,
        'mes': mes,
        'anio': anio
    })

# Vista de perfil (solo muestra plantilla)
@login_required
def perfil(request):
    return render(request, 'perfil.html')

# Dashboard IA
@login_required
def dashboard_ia(request):
    usuario = request.user
    respuesta_ia = None
    # Procesar consulta directa a la IA
    import unicodedata
    def limpiar_texto(texto):
        return ''.join(c for c in unicodedata.normalize('NFD', texto.lower()) if unicodedata.category(c) != 'Mn')

    if request.method == 'POST' and 'pregunta_ia' in request.POST:
        pregunta = limpiar_texto(request.POST.get('pregunta_ia', '').strip())
        # Respuestas más flexibles y variadas
        if ('habilidad' in pregunta or 'skill' in pregunta) and ('demandad' in pregunta or 'buscad' in pregunta):
            from .models import DatoMercado
            datos = DatoMercado.objects.all()
            if datos.exists():
                top = datos.values('habilidad').annotate(total=models.Sum('cantidad')).order_by('-total').first()
                respuesta_ia = f"¡Hola! Soy AGUSTIN 😊. La habilidad más demandada actualmente es: {top['habilidad']} (total: {top['total']}). Si quieres ver ofertas relacionadas, visita la sección de empleo." if top else "No hay datos suficientes para responder, pero puedes buscar ofertas en la sección de empleo."
            else:
                respuesta_ia = "No hay datos de mercado para analizar."
        elif ('tecnologia' in pregunta or 'tecnología' in pregunta) and ('buscad' in pregunta or 'demandad' in pregunta or 'trabajador' in pregunta):
            from .models import InscripcionOferta
            inscripciones = InscripcionOferta.objects.select_related('oferta').all()
            data = []
            for i in inscripciones:
                for hab in i.oferta.habilidades.all():
                    data.append(hab.nombre)
            if data:
                from collections import Counter
                top = Counter(data).most_common(1)[0]
                respuesta_ia = f"¡Hola! Soy AGUSTIN 😊. La tecnología más demandada por los trabajadores es: {top[0]} (total inscripciones: {top[1]}). Si quieres ver ofertas relacionadas, puedes ir a la sección de empleo."
            else:
                respuesta_ia = "No hay inscripciones suficientes para analizar."
        elif 'portal' in pregunta and ('oferta' in pregunta or 'publica' in pregunta or 'empleo' in pregunta):
            from .models import DatoMercado
            datos = DatoMercado.objects.all()
            if datos.exists() and 'portal' in datos.values()[0]:
                top = datos.values('portal').annotate(total=models.Sum('cantidad')).order_by('-total').first()
                respuesta_ia = f"¡Hola! Soy AGUSTIN 😊. El portal con más ofertas registradas es: {top['portal']} (total: {top['total']}). Si quieres ver oportunidades, visita la sección de empleo." if top else "No hay datos suficientes para responder, pero puedes buscar oportunidades en la sección de empleo."
            else:
                respuesta_ia = "No hay datos de mercado para analizar."
        elif any(p in pregunta for p in ['tendencia', 'tendencias', 'evolucion', 'evolución']):
            respuesta_ia = "¡Hola! Soy AGUSTIN 😊. Puedes consultar el gráfico de tendencias en el panel superior. Si buscas empleo, recuerda que tienes la sección de ofertas disponible."
        elif pregunta:
            respuesta_ia = "¡Hola! Soy AGUSTIN 😊. No he entendido tu consulta. Ejemplos que puedes probar: '¿Cuáles son las habilidades más demandadas?', '¿Qué tecnología buscan más los trabajadores?', '¿Qué portal publica más ofertas?'. Y si quieres, puedes ir directamente a la sección de empleo para ver todas las ofertas."
    # Obtener habilidades del usuario
    usuario_habilidades = list(usuario.habilidad_set.values_list('nombre', flat=True)) if hasattr(usuario, 'habilidad_set') else []
    # Obtener ofertas recientes
    ofertas_qs = OfertaLaboral.objects.all().order_by('-fecha_publicacion')[:100]
    ofertas = []
    for o in ofertas_qs:
        habilidades = list(o.habilidades.values_list('nombre', flat=True))
        ofertas.append({
            'titulo': o.titulo,
            'empresa': o.empresa,
            'portal': o.portal,
            'habilidades': habilidades,
            'fecha_publicacion': str(o.fecha_publicacion) if o.fecha_publicacion else '',
        })
    # Recomendaciones
    recomendaciones = recomendar_ofertas(usuario_habilidades, ofertas)[:5] if usuario_habilidades else []
    # Tendencias
    tendencias_df = predecir_tendencia_habilidades(ofertas)
    tendencias_img = None
    if not tendencias_df.empty:
        fig, ax = plt.subplots(figsize=(6,3))
        tendencias_df.tail(6).plot(ax=ax)
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        tendencias_img = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
    return render(request, 'dashboard.html', {
        'recomendaciones': recomendaciones,
        'tendencias': tendencias_img,
        'respuesta_ia': respuesta_ia
    })

# Vista de análisis de mercado laboral
@login_required
def analisis_mercado(request):
    import matplotlib.pyplot as plt
    from .models import DatoMercado, InscripcionOferta, OfertaLaboral
    import base64
    from io import BytesIO
    import pandas as pd

    # 1. Habilidades más demandadas por región
    datos = DatoMercado.objects.all()
    df = pd.DataFrame(list(datos.values('region', 'habilidad', 'cantidad')))
    grafico_habilidades_region = None
    if not df.empty:
        pivot = df.pivot_table(index='habilidad', columns='region', values='cantidad', aggfunc='sum', fill_value=0)
        top = pivot.sum(axis=1).sort_values(ascending=False).head(5).index
        pivot = pivot.loc[top]
        fig, ax = plt.subplots(figsize=(6,3))
        pivot.plot(kind='bar', ax=ax)
        plt.title('Top 5 habilidades por región')
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        grafico_habilidades_region = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)

    # 2. Comparativa de tendencias entre portales
    df_portal = pd.DataFrame(list(datos.values('fecha', 'portal', 'cantidad')))
    grafico_portales = None
    if not df_portal.empty:
        pivot = df_portal.pivot_table(index='fecha', columns='portal', values='cantidad', aggfunc='sum', fill_value=0)
        # Solo graficar si hay datos numéricos
        if not pivot.tail(6).empty and any(pivot.tail(6).select_dtypes(include='number').columns):
            fig, ax = plt.subplots(figsize=(6,3))
            pivot.tail(6).plot(ax=ax)
            plt.title('Tendencias por portal')
            plt.tight_layout()
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            grafico_portales = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
        else:
            grafico_portales = None

    # 3. Inscripciones y tecnologías más demandadas
    inscripciones = InscripcionOferta.objects.select_related('oferta').all()
    data = []
    for i in inscripciones:
        for hab in i.oferta.habilidades.all():
            data.append(hab.nombre)
    grafico_inscripciones = None
    if data:
        series = pd.Series(data)
        top = series.value_counts().head(7)
        fig, ax = plt.subplots(figsize=(6,3))
        top.plot(kind='bar', ax=ax, color='#2d7be5')
        plt.title('Tecnologías más demandadas por los trabajadores')
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        grafico_inscripciones = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)

    return render(request, 'analisis.html', {
        'grafico_habilidades_region': grafico_habilidades_region,
        'grafico_portales': grafico_portales,
        'grafico_inscripciones': grafico_inscripciones
    })


# Vista de registro de usuario
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect('buscar_todos')

            return redirect('buscar_todos')

    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# Vista de login de usuario
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            return redirect('buscar_todos')

            return redirect('buscar_todos')

        else:
            return render(request, 'login.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'login.html')


# Vista de búsqueda de empleo
@login_required
def buscar_empleo(request):
    if request.method == 'POST':
        palabra = request.POST.get('palabra', '')  # Palabra clave
        ubicacion = request.POST.get('ubicacion', '')  # Ubicación
        puesto = request.POST.get('puesto', '')  # Puesto de trabajo
        empresa = request.POST.get('empresa', '')  # Empresa
        salario = request.POST.get('salario', '')  # Salario
        tecnologia = request.POST.get('tecnologia', '')  # Tecnología

        # Llamadas a las funciones de scraping con los filtros
        ofertas_infojobs = obtener_ofertas_infojobs(palabra, ubicacion, puesto, empresa, salario, tecnologia)
        ofertas_tecno = obtener_ofertas_tecnoempleo(palabra, ubicacion, puesto, empresa, salario, tecnologia)
        ofertas_linkedin = obtener_ofertas_linkedin(palabra, ubicacion, puesto, empresa, salario, tecnologia)

        # Combinamos todas las ofertas obtenidas
        todas = ofertas_infojobs + ofertas_tecno + ofertas_linkedin

        # Renderizamos los resultados
        return render(request, 'resultados.html', {'ofertas': todas})
    
# Vista para cerrar sesión
@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

# Vista de búsqueda de empleo
@login_required
def buscar_linkedin(request):
    if request.method == 'POST':
        palabra = request.POST.get('palabra', '')
        ubicacion = request.POST.get('ubicacion', '')
        puesto = request.POST.get('puesto', '')
        empresa = request.POST.get('empresa', '')
        salario = request.POST.get('salario', '')
        tecnologia = request.POST.get('tecnologia', '')
    try:
        num_ofertas = int(request.POST.get('num_ofertas', 10))
        if num_ofertas <= 0:
            num_ofertas = 10
    except (TypeError, ValueError):
        num_ofertas = 10
        ofertas = obtener_ofertas_linkedin(palabra, ubicacion, puesto, empresa, salario, tecnologia, num_ofertas)
        print(f"[DEBUG] LinkedIn: {len(ofertas)} ofertas. Primer resultado: {ofertas[0] if ofertas else 'Ninguna'}")
        # Normaliza campos
        for oferta in ofertas:
            oferta.setdefault('titulo', '')
            oferta.setdefault('empresa', '')
            oferta.setdefault('ubicacion', '')
            oferta.setdefault('salario', '')
            oferta.setdefault('tecnologia', '')
            oferta.setdefault('fecha_publicacion', '')
            oferta.setdefault('url_oferta', '')
            oferta.setdefault('portal', 'LinkedIn')
        return render(request, 'resultados.html', {'ofertas': ofertas, 'portal': 'LinkedIn'})
    return render(request, 'buscar.html')

@login_required
def buscar_tecnoempleo(request):
    if request.method == 'POST':
        palabra = request.POST.get('palabra', '')
        ubicacion = request.POST.get('ubicacion', '')
        puesto = request.POST.get('puesto', '')
        empresa = request.POST.get('empresa', '')
        salario = request.POST.get('salario', '')
        tecnologia = request.POST.get('tecnologia', '')
    try:
        num_ofertas = int(request.POST.get('num_ofertas', 10))
        if num_ofertas <= 0:
            num_ofertas = 10
    except (TypeError, ValueError):
        num_ofertas = 10
        ofertas = obtener_ofertas_tecnoempleo_alternativo(palabra, ubicacion, puesto, empresa, salario, tecnologia, num_ofertas)
        print(f"[DEBUG] Tecnoempleo: {len(ofertas)} ofertas. Primer resultado: {ofertas[0] if ofertas else 'Ninguna'}")
        for oferta in ofertas:
            oferta.setdefault('titulo', '')
            oferta.setdefault('empresa', '')
            oferta.setdefault('ubicacion', '')
            oferta.setdefault('salario', '')
            oferta.setdefault('tecnologia', '')
            oferta.setdefault('fecha_publicacion', '')
            oferta.setdefault('url_oferta', '')
            oferta.setdefault('portal', 'Tecnoempleo')
        return render(request, 'resultados.html', {'ofertas': ofertas, 'portal': 'Tecnoempleo'})
    return render(request, 'buscar.html')

@login_required
def buscar_infojobs(request):
    if request.method == 'POST':
        palabra = request.POST.get('palabra', '')
        ubicacion = request.POST.get('ubicacion', '')
        puesto = request.POST.get('puesto', '')
        empresa = request.POST.get('empresa', '')
        salario = request.POST.get('salario', '')
        tecnologia = request.POST.get('tecnologia', '')
    try:
        num_ofertas = int(request.POST.get('num_ofertas', 10))
        if num_ofertas <= 0:
            num_ofertas = 10
    except (TypeError, ValueError):
        num_ofertas = 10
        ofertas = obtener_ofertas_infojobs(palabra, ubicacion, puesto, empresa, salario, tecnologia, num_ofertas)
        print(f"[DEBUG] InfoJobs: {len(ofertas)} ofertas. Primer resultado: {ofertas[0] if ofertas else 'Ninguna'}")
        for oferta in ofertas:
            oferta.setdefault('titulo', '')
            oferta.setdefault('empresa', '')
            oferta.setdefault('ubicacion', '')
            oferta.setdefault('salario', '')
            oferta.setdefault('tecnologia', '')
            oferta.setdefault('fecha_publicacion', '')
            oferta.setdefault('url_oferta', '')
            oferta.setdefault('portal', 'InfoJobs')
        return render(request, 'resultados.html', {'ofertas': ofertas, 'portal': 'InfoJobs'})
    return render(request, 'buscar.html')

@login_required
def buscar_todos(request):
    if request.method == 'POST':
        palabra = request.POST.get('palabra', '')
        ubicacion = request.POST.get('ubicacion', '')
        puesto = request.POST.get('puesto', '')
        empresa = request.POST.get('empresa', '')
        salario = request.POST.get('salario', '')
        tecnologia = request.POST.get('tecnologia', '')
    try:
        num_ofertas = int(request.POST.get('num_ofertas', 10))
        if num_ofertas <= 0:
            num_ofertas = 10
    except (TypeError, ValueError):
        num_ofertas = 10
        ofertas_linkedin = obtener_ofertas_linkedin(palabra, ubicacion, puesto, empresa, salario, tecnologia, num_ofertas)
        ofertas_tecno = obtener_ofertas_tecnoempleo_alternativo(palabra, ubicacion, puesto, empresa, salario, tecnologia, num_ofertas)
        ofertas_infojobs = obtener_ofertas_infojobs(palabra, ubicacion, puesto, empresa, salario, tecnologia, num_ofertas)
        print(f"[DEBUG] LinkedIn: {len(ofertas_linkedin)} | Tecnoempleo: {len(ofertas_tecno)} | InfoJobs: {len(ofertas_infojobs)}")
        todas = ofertas_linkedin + ofertas_tecno + ofertas_infojobs
        for oferta in todas:
            oferta.setdefault('titulo', '')
            oferta.setdefault('empresa', '')
            oferta.setdefault('ubicacion', '')
            oferta.setdefault('salario', '')
            oferta.setdefault('tecnologia', '')
            oferta.setdefault('fecha_publicacion', '')
            oferta.setdefault('url_oferta', '')
            oferta.setdefault('portal', 'Todos')
        if todas:
            print(f"[DEBUG] Primera oferta global: {todas[0]}")
        return render(request, 'resultados.html', {'ofertas': todas, 'portal': 'Todos'})

    return render(request, 'buscar.html')

# Buscar ofertas en la base de datos
def buscar_ofertas(request):
    ofertas = OfertaLaboral.objects.all()  # Obtiene todas las ofertas desde la base de datos
    return render(request, 'buscar.html', {'ofertas': ofertas})

def home(request):
    return render(request, 'home.html')
