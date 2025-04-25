from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def iniciar_driver():
    options = Options()
    # options.add_argument('--headless')  # Descomenta para headless, comenta para ver el navegador
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

# ------------------------------------------------------------------------------------------
# TECNOEMPLEO

def obtener_ofertas_tecnoempleo_alternativo(palabra_clave='python', ubicacion='', puesto='', empresa='', salario='', tecnologia='', num_ofertas=10):
    """
    Scraper robusto para Tecnoempleo: mapea nombre/value de provincia, elimina selectores obsoletos y muestra logs claros.
    """
    try:
        from selenium.webdriver.support.ui import Select
        import time
        # Mapeo nombre de provincia a value
        provincia_map = {
            'a coruña': '231', 'álava': '232', 'albacete': '233', 'alicante': '234', 'almería': '235', 'asturias': '236',
            'ávila': '237', 'badajoz': '238', 'baleares': '239', 'barcelona': '240', 'bizkaia': '241', 'burgos': '242',
            'cáceres': '243', 'cádiz': '244', 'cantabria': '245', 'castellón': '246', 'ceuta': '247', 'ciudad real': '248',
            'córdoba': '249', 'cuenca': '250', 'gipuzkoa': '251', 'girona': '252', 'granada': '253', 'guadalajara': '254',
            'huelva': '255', 'huesca': '256', 'jaén': '257', 'la rioja': '258', 'las palmas': '259', 'león': '260',
            'lleida': '262', 'lugo': '261', 'madrid': '263', 'málaga': '264', 'melilla': '265', 'murcia': '266',
            'navarra': '267', 'ourense': '268', 'palencia': '269', 'pontevedra': '270', 'salamanca': '271', 'segovia': '273',
            'sevilla': '274', 'soria': '275', 'sta. cruz de tenerife': '272', 'tarragona': '276', 'teruel': '277',
            'toledo': '278', 'valencia': '279', 'valladolid': '280', 'zamora': '281', 'zaragoza': '282'
        }
        provincia_val = ''
        if ubicacion:
            if ubicacion.isdigit():
                provincia_val = ubicacion
            else:
                ubicacion_lower = ubicacion.strip().lower()
                provincia_val = provincia_map.get(ubicacion_lower, '')
                if not provincia_val:
                    print(f"[TECNOEMPLEO-ALT][ADVERTENCIA] Provincia '{ubicacion}' no reconocida. Se omite la selección de provincia.")
        print("[TECNOEMPLEO-ALT] Iniciando scraping de Tecnoempleo...")
        driver = iniciar_driver()
        # Construir URL directa a los resultados de ofertas
        # Solo palabra clave y provincia en la URL
        url = f"https://www.tecnoempleo.com/ofertas-trabajo/?te={palabra_clave}"
        if provincia_val:
            url += f"&pr={provincia_val}"
        print(f"[TECNOEMPLEO-ALT] Navegando directamente a la URL de resultados: {url}")
        driver.get(url)

        # Espera explícita a que aparezcan las ofertas
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.col-10.col-md-9.col-lg-7'))
            )
            print("[TECNOEMPLEO-ALT] ¡Ofertas localizadas en la página!")
        except Exception as e:
            print(f"[TECNOEMPLEO-ALT][ERROR] Timeout esperando las ofertas: {e}")

        print(f"[TECNOEMPLEO-ALT] Búsqueda realizada con palabra clave: {palabra_clave} y provincia: {provincia_val}")

        # Imprimir el HTML recibido tras la búsqueda (primeros 2000 caracteres)
        print("[TECNOEMPLEO-ALT] HTML tras búsqueda (primeros 2000 caracteres):\n" + driver.page_source[:2000])

        ofertas = []
        total_extraidas = 0
        pagina = 1

        # Extraer número de ofertas encontradas
        try:
            num_ofertas_elem = driver.find_element(By.CSS_SELECTOR, 'h1.h4.h6-xs.text-center.my-4')
            num_ofertas_text = num_ofertas_elem.text
            print(f"[TECNOEMPLEO-ALT] Número de ofertas encontradas: {num_ofertas_text}")
        except Exception as e:
            print(f"[TECNOEMPLEO-ALT][ERROR] No se pudo extraer el número de ofertas: {e}")

        while total_extraidas < num_ofertas:
            print(f"[TECNOEMPLEO-ALT] Extrayendo ofertas de la página {pagina}...")
            ofertas_divs = driver.find_elements(By.CSS_SELECTOR, 'div.col-10.col-md-9.col-lg-7')
            if not ofertas_divs:
                print("[TECNOEMPLEO-ALT][ADVERTENCIA] No se encontraron ofertas con el selector principal. Probando selector alternativo...")
                # Selector alternativo: buscar cards de oferta por clase común
                ofertas_divs = driver.find_elements(By.CSS_SELECTOR, 'div.card.card-job')
            if not ofertas_divs:
                print("[TECNOEMPLEO-ALT][ERROR] No se encontraron ofertas con ningún selector. Volcando HTML de la página para depuración:")
                print(driver.page_source[:3000])
                break
            for div in ofertas_divs:
                if total_extraidas >= num_ofertas:
                    break
                try:
                    titulo_elem = div.find_element(By.CSS_SELECTOR, 'h3.fs-5.mb-2 a')
                    titulo = titulo_elem.text.strip()
                    enlace = titulo_elem.get_attribute('href')
                    empresa = div.find_element(By.CSS_SELECTOR, 'a.text-primary.link-muted').text.strip()
                    ubicacion_fecha = div.find_element(By.CSS_SELECTOR, 'span.d-block.d-lg-none.text-gray-800').text.strip()
                    descripcion = div.find_element(By.CSS_SELECTOR, 'span.hidden-md-down.text-gray-800').text.strip()
                    oferta = {
                        'titulo': titulo,
                        'empresa': empresa,
                        'ubicacion': ubicacion_fecha,  # Puedes dividir si quieres separar ubicación y fecha
                        'salario': '',
                        'tecnologia': tecnologia if tecnologia else '',
                        'fecha_publicacion': '',  # Si puedes extraer la fecha, ponla aquí
                        'url_oferta': enlace,
                        'portal': 'Tecnoempleo'
                    }
                    ofertas.append(oferta)
                    total_extraidas += 1
                    print(f"\n{'='*40}\n[Título] {titulo}\n[Enlace] {enlace}\n[Empresa] {empresa}\n[Ubicación y fecha] {ubicacion_fecha}\n[Descripción] {descripcion[:120]}...\n{'='*40}")
                except Exception as e:
                    print(f"[TECNOEMPLEO-ALT][ERROR] Error extrayendo una oferta: {e}")

            # Intentar ir a la página siguiente
            if total_extraidas < num_ofertas:
                try:
                    enlace_siguiente = driver.find_element(By.XPATH, '//li[@class="page-item"]/a[contains(text(),"siguiente")]')
                    siguiente_url = enlace_siguiente.get_attribute('href')
                    print(f"[TECNOEMPLEO-ALT] Siguiente página: {siguiente_url}")
                    driver.get(siguiente_url)
                    time.sleep(3)
                    pagina += 1
                except Exception as e:
                    print(f"[TECNOEMPLEO-ALT] No hay más páginas o no se pudo avanzar: {e}")
                    break

        print(f"[TECNOEMPLEO-ALT] Total de ofertas extraídas: {len(ofertas)}")
        return ofertas

    except Exception as e:
        print(f"[TECNOEMPLEO-ALT][FATAL] {e}")
        return []

# ------------------------------------------------------------------------------------------
# TECNOEMPLEO (original)

