from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def iniciar_driver():
    options = Options()
    # options.add_argument('--headless')  # Quitamos headless para ver el navegador
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 ...')
    return webdriver.Chrome(options=options)

# ------------------------------------------------------------------------------------------
# INFOJOBS

def obtener_ofertas_infojobs(palabra_clave='python', ubicacion='', puesto='', empresa='', salario='', tecnologia='', num_ofertas=10):
    print(f"[INFOJOBS] Buscando ofertas con palabra_clave={palabra_clave}, ubicacion={ubicacion}, puesto={puesto}, empresa={empresa}")
    driver = iniciar_driver()
    # Nueva URL correcta para InfoJobs
    # Diccionario de provincias (solo las más comunes, puedes ampliarlo)
    provincias = {
        'asturias': '6', 'madrid': '33', 'barcelona': '9', 'valencia': '49', 'sevilla': '43',
        'alicante': '4', 'vizcaya': '51', 'malaga': '34', 'murcia': '36', 'zaragoza': '53',
        'baleares': '26', 'valladolid': '50', 'coruña': '28', 'granada': '18', 'cádiz': '12',
        'santa cruz de tenerife': '46', 'pontevedra': '40', 'toledo': '48', 'almería': '5',
        'guipúzcoa': '23', 'burgos': '10', 'córdoba': '17', 'cantabria': '13', 'asturias': '6'
    }
    provincia_codigo = ''
    if ubicacion:
        ubicacion_normalizada = ubicacion.strip().lower()
        provincia_codigo = provincias.get(ubicacion_normalizada, '')
    # Construir la URL de búsqueda
    url = 'https://www.infojobs.net/jobsearch/search-results/list.xhtml?'
    parametros = []
    if palabra_clave:
        parametros.append(f'keyword={palabra_clave}')
    if provincia_codigo:
        parametros.append(f'province={provincia_codigo}')
    if parametros:
        url += '&'.join(parametros)
    print(f"[INFOJOBS] URL generada: {url}")
    driver.get(url)
    # Esperar explícitamente a que cargue al menos una tarjeta de oferta
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    try:
        # Esperar a que cargue el main (React)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'main.ij-Box.ij-TemplateAdsPage-main'))
        )
        # Esperar a que aparezca al menos un enlace de oferta
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.ij-OfferCardContent-description-title-link'))
        )
        # Simular scroll para forzar la carga dinámica
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
        import time
        time.sleep(2)
        # Imprimir parte del HTML para depuración
        print("[INFOJOBS][DEPURACION] HTML parcial:\n", driver.page_source[:2000])
    except Exception as e:
        print(f"[INFOJOBS][ADVERTENCIA] No se encontró ninguna oferta tras esperar: {e}")

    ofertas = []
    try:
        tarjetas = driver.find_elements(By.CSS_SELECTOR, 'div.ij-OfferCardContent-description')
        print(f"[INFOJOBS] Tarjetas encontradas con 'div.ij-OfferCardContent-description': {len(tarjetas)}")
        if len(tarjetas) == 0:
            print("[INFOJOBS][ADVERTENCIA] No se encontraron tarjetas de ofertas. Puede que el selector haya cambiado.")

        for tarjeta in tarjetas[:num_ofertas]:
            try:
                # Título y enlace
                try:
                    titulo_elem = tarjeta.find_element(By.CSS_SELECTOR, 'h2.ij-OfferCardContent-description-title a.ij-OfferCardContent-description-title-link')
                    titulo = titulo_elem.text.strip()
                    url_oferta = titulo_elem.get_attribute('href')
                    if url_oferta and url_oferta.startswith('//'):
                        url_oferta = 'https:' + url_oferta
                except Exception as e:
                    print(f"[INFOJOBS][ERROR] No se pudo extraer título/enlace: {e}")
                    continue
                # Empresa
                try:
                    empresa = tarjeta.find_element(By.CSS_SELECTOR, 'h3.ij-OfferCardContent-description-subtitle a').text.strip()
                except:
                    empresa = ''
                # Ubicación
                try:
                    ubicacion_oferta = tarjeta.find_element(By.CSS_SELECTOR, 'li.ij-OfferCardContent-description-list-item').text.strip()
                except:
                    ubicacion_oferta = ''
                # Salario (opcional)
                try:
                    salario = tarjeta.find_element(By.CSS_SELECTOR, 'span.ij-OfferCardContent-description-salary-info').text.strip()
                except:
                    salario = ''
                ofertas.append({
                    'titulo': titulo,
                    'empresa': empresa,
                    'ubicacion': ubicacion_oferta,
                    'salario': salario,
                    'tecnologia': tecnologia if tecnologia else '',
                    'fecha_publicacion': '',
                    'url_oferta': url_oferta,
                    'portal': 'InfoJobs'
                })
                # Empresa
                try:
                    empresa = tarjeta.find_element(By.CSS_SELECTOR, 'h3.ij-OfferCardContent-description-subtitle a').text.strip()
                except:
                    empresa = ''
                # Ubicación
                try:
                    ubicacion = tarjeta.find_element(By.CSS_SELECTOR, 'li.ij-OfferCardContent-description-list-item').text.strip()
                except:
                    ubicacion = ''
                # Salario (opcional)
                try:
                    salario = tarjeta.find_element(By.CSS_SELECTOR, 'span.ij-OfferCardContent-description-salary-info').text.strip()
                except:
                    salario = ''
                ofertas.append({
                    'titulo': titulo,
                    'empresa': empresa,
                    'ubicacion': ubicacion,
                    'salario': salario,
                    'tecnologia': tecnologia if tecnologia else '',
                    'fecha_publicacion': '',
                    'url_oferta': url_oferta,
                    'portal': 'InfoJobs'
                })
            except Exception as e:
                print(f"[INFOJOBS][ERROR] Error extrayendo datos de una tarjeta: {e}")
                continue
    except Exception as e:
        print(f"[INFOJOBS][ERROR] Error general en el scraping: {e}")
    finally:
        driver.quit()
    print(f"[INFOJOBS] Total ofertas extraídas: {len(ofertas)}")
    return ofertas
