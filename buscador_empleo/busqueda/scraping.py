
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# ------------------------------------------------------------------------------------------
# Función común para scraping
def obtener_ofertas_generico(url, headers, contenedor_clase, titulo_clase, empresa_clase, ubicacion_clase, portal_nombre):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    ofertas = []
    contenedores = soup.find_all('div', class_=contenedor_clase)
    
    for oferta in contenedores:
        titulo_tag = oferta.find('a', class_=titulo_clase)
        if not titulo_tag:
            continue

        titulo = titulo_tag.text.strip()
        url_oferta = titulo_tag['href']
        if not url_oferta.startswith('http'):  # Para asegurar que el enlace sea absoluto
            url_oferta = f'{url}{url_oferta}'

        empresa_tag = oferta.find('div', class_=empresa_clase)
        empresa = empresa_tag.text.strip() if empresa_tag else 'Desconocida'

        ubicacion_tag = oferta.find('div', class_=ubicacion_clase)
        ubicacion = ubicacion_tag.text.strip() if ubicacion_tag else 'Sin especificar'

        ofertas.append({
            'titulo': titulo,
            'empresa': empresa,
            'ubicacion': ubicacion,
            'url': url_oferta,
            'portal': portal_nombre  # Añadido el portal
        })
    return ofertas

# ------------------------------------------------------------------------------------------
# INFOJOBS
def obtener_ofertas_infojobs(palabra_clave='', ubicacion='', puesto='', empresa='', salario='', tecnologia=''):
    url = f'https://www.infojobs.net/jobsearch/search-results/list.xhtml?keyword={palabra_clave}&province={ubicacion}&title={puesto}&company={empresa}'
    
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    return obtener_ofertas_generico(url, headers, 'ij-OfferCard', 'ij-OfferCard__titleLink', 
                                    'ij-OfferCard__company', 'ij-OfferCard__location', 'InfoJobs')

# ------------------------------------------------------------------------------------------
# TECNOEMPLEO
def obtener_ofertas_tecnoempleo(palabra_clave='python', ubicacion='', puesto='', empresa='', salario='', tecnologia=''):
    url = f'https://www.tecnoempleo.com/busqueda-empleo?q={palabra_clave}&localidad={ubicacion}&puesto={puesto}&empresa={empresa}&salario={salario}&tecnologia={tecnologia}'
    
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    return obtener_ofertas_generico(url, headers, 'oferta', 'titulooferta', 'nomempresa', 'poblacion', 'Tecnoempleo')

# ------------------------------------------------------------------------------------------
# LINKEDIN
def obtener_ofertas_linkedin(palabra_clave='python', ubicacion='España', puesto='', empresa='', salario='', tecnologia=''):
    options = Options()
    options.add_argument('--headless')  # Ejecuta sin abrir ventana
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    url = f'https://www.linkedin.com/jobs/search?keywords={palabra_clave}&location={ubicacion}'
    driver.get(url)

    time.sleep(5)  # Espera a que cargue

    ofertas = []
    resultados = driver.find_elements(By.CLASS_NAME, 'base-card')

    for tarjeta in resultados[:10]:  # Limitar a 10 resultados
        try:
            titulo = tarjeta.find_element(By.CLASS_NAME, 'base-search-card__title').text.strip()
            empresa = tarjeta.find_element(By.CLASS_NAME, 'base-search-card__subtitle').text.strip()
            ubicacion = tarjeta.find_element(By.CLASS_NAME, 'job-search-card__location').text.strip()
            url_oferta = tarjeta.find_element(By.TAG_NAME, 'a').get_attribute('href')

            ofertas.append({
                'titulo': titulo,
                'empresa': empresa,
                'ubicacion': ubicacion,
                'url': url_oferta,
                'portal': 'LinkedIn'  # Añadido el portal
            })
        except:
            continue

    driver.quit()
    return ofertas

from .scraping_linkedin import obtener_ofertas_linkedin
from .scraping_infojobs import obtener_ofertas_infojobs
from .scraping_tecnoempleo import obtener_ofertas_tecnoempleo_alternativo
from .bs_utils import obtener_ofertas_tecnoempleo_bs
import requests

# ------------------------------------------------------------------------------------------
# Diccionario que centraliza los scraping de cada portal
scraping_portales = {
    'LinkedIn': obtener_ofertas_linkedin,
    'InfoJobs': obtener_ofertas_infojobs,
    'Tecnoempleo': obtener_ofertas_tecnoempleo_alternativo,
}

# ------------------------------------------------------------------------------------------
# Función para obtener todas las ofertas, con manejo de errores y eliminación de duplicados
def obtener_todas_las_ofertas(palabra_clave='python', ubicacion='España', puesto='', empresa='', salario='', tecnologia=''):
    ofertas = []
    urls_vistas = set()  # Para evitar duplicados de ofertas basados en la URL
    
    for portal, funcion in scraping_portales.items():
        try:
            print(f"Obteniendo ofertas de {portal}...")
            ofertas_portal = funcion(palabra_clave, ubicacion, puesto, empresa, salario, tecnologia)
            
            # Eliminar duplicados si la URL ya ha sido vista
            for oferta in ofertas_portal:
                if oferta['url_oferta'] not in urls_vistas:
                    ofertas.append(oferta)
                    urls_vistas.add(oferta['url_oferta'])
                    
        except Exception as e:
            print(f"Error al obtener ofertas de {portal}: {e}")
            continue

    # Siempre intenta también BeautifulSoup para Tecnoempleo y añade sus ofertas si no están duplicadas
    try:
        print("Intentando con BeautifulSoup para Tecnoempleo (siempre, como refuerzo)...")
        ofertas_bs = obtener_ofertas_tecnoempleo_bs(palabra_clave, ubicacion, puesto, empresa, salario, tecnologia)
        for oferta in ofertas_bs:
            if oferta['url_oferta'] not in urls_vistas:
                ofertas.append(oferta)
                urls_vistas.add(oferta['url_oferta'])
    except Exception as e:
        print(f"Error con BeautifulSoup para Tecnoempleo: {e}")

    return ofertas

# ------------------------------------------------------------------------------------------
# Prueba directa (fuera de Django)
if __name__ == '__main__':
    keyword = 'python'
    ciudad = 'Madrid'
    resultados = obtener_todas_las_ofertas(keyword, ciudad)

    for oferta in resultados:
        print(f"[{oferta['portal']}] {oferta['titulo']} - {oferta['empresa']} ({oferta['ubicacion']})")
        print(f"👉 {oferta['url_oferta']}")
        print('-' * 80)


