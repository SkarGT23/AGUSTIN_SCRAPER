from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def iniciar_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

# ------------------------------------------------------------------------------------------
# LINKEDIN

def obtener_ofertas_linkedin(palabra_clave='python', ubicacion='', puesto='', empresa='', salario='', tecnologia='', num_ofertas=10):
    import logging
    driver = iniciar_driver()
    url = f'https://www.linkedin.com/jobs/search?keywords={palabra_clave}&location={ubicacion}'
    driver.get(url)
    time.sleep(8)  # Aumenta el tiempo de espera

    ofertas = []
    resultados = driver.find_elements(By.CLASS_NAME, 'base-card')

    for idx, tarjeta in enumerate(resultados[:num_ofertas]):
        # Extraemos cada campo individualmente, aunque alguno falle
        try:
            titulo = tarjeta.find_element(By.CLASS_NAME, 'base-search-card__title').text.strip()
        except Exception as e:
            titulo = ''
            print(f"[DEBUG][LinkedIn] No se encontró título en la tarjeta {idx+1}: {e}")
        try:
            empresa = tarjeta.find_element(By.CLASS_NAME, 'base-search-card__subtitle').text.strip()
        except Exception as e:
            empresa = ''
            print(f"[DEBUG][LinkedIn] No se encontró empresa en la tarjeta {idx+1}: {e}")
        try:
            ubicacion = tarjeta.find_element(By.CLASS_NAME, 'job-search-card__location').text.strip()
        except Exception as e:
            ubicacion = ''
            print(f"[DEBUG][LinkedIn] No se encontró ubicación en la tarjeta {idx+1}: {e}")
        try:
            url_oferta = tarjeta.find_element(By.TAG_NAME, 'a').get_attribute('href')
        except Exception as e:
            url_oferta = ''
            print(f"[DEBUG][LinkedIn] No se encontró url en la tarjeta {idx+1}: {e}")
        # Solo añadimos si hay al menos título o empresa o url
        if titulo or empresa or url_oferta:
            print(f"[DEBUG][LinkedIn] Oferta extraída: Título='{titulo}', Empresa='{empresa}', Ubicación='{ubicacion}', URL='{url_oferta}'")
            ofertas.append({
                'titulo': titulo,
                'empresa': empresa,
                'ubicacion': ubicacion,
                'salario': '',
                'tecnologia': tecnologia if tecnologia else '',
                'fecha_publicacion': '',
                'url_oferta': url_oferta,
                'portal': 'LinkedIn'
            })
        else:
            print(f"[DEBUG][LinkedIn] Oferta descartada por falta de datos en la tarjeta {idx+1}")

    driver.quit()
    return ofertas
