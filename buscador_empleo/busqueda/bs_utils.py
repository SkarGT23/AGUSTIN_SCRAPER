import requests
from bs4 import BeautifulSoup

def obtener_ofertas_tecnoempleo_bs(palabra_clave='python', ubicacion='', puesto='', empresa='', salario='', tecnologia=''):
    url = f'https://www.tecnoempleo.com/ofertas-trabajo/{palabra_clave}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    print(f"[BS][TECNOEMPLEO] URL: {url}")
    resp = requests.get(url, headers=headers, timeout=10)
    ofertas = []
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Buscar tarjetas de oferta modernas (article.card, div.card, etc.)
        cards = soup.find_all(['article', 'div'], class_=lambda c: c and 'card' in c)
        print(f"[BS][TECNOEMPLEO] Tarjetas encontradas: {len(cards)}")
        for card in cards:
            try:
                # Título y URL
                a_tag = card.find('a', href=True)
                if a_tag:
                    titulo = a_tag.get_text(strip=True)
                    url_oferta = a_tag['href']
                    if not url_oferta.startswith('http'):
                        url_oferta = 'https://www.tecnoempleo.com' + url_oferta
                else:
                    titulo = ''
                    url_oferta = ''
                # Empresa
                empresa_tag = card.find(['span', 'div'], class_=lambda c: c and ('emp' in c or 'empresa' in c))
                empresa = empresa_tag.get_text(strip=True) if empresa_tag else ''
                # Ubicación
                ubicacion_tag = card.find(['span', 'div'], class_=lambda c: c and ('localidad' in c or 'ubicacion' in c))
                ubicacion_val = ubicacion_tag.get_text(strip=True) if ubicacion_tag else ''
                # Fecha de publicación (opcional)
                fecha_tag = card.find(['span', 'div'], class_=lambda c: c and 'fecha' in c)
                fecha_publicacion = fecha_tag.get_text(strip=True) if fecha_tag else ''
                ofertas.append({
                    'titulo': titulo,
                    'empresa': empresa,
                    'ubicacion': ubicacion_val,
                    'salario': '',
                    'tecnologia': tecnologia if tecnologia else '',
                    'fecha_publicacion': fecha_publicacion,
                    'url_oferta': url_oferta,
                    'portal': 'Tecnoempleo (BS)'
                })
            except Exception as e:
                print(f"[BS][TECNOEMPLEO][ERROR] {e}")
                continue
    else:
        print(f"[BS][TECNOEMPLEO][ERROR] Código de estado HTTP: {resp.status_code}")
    print(f"[BS][TECNOEMPLEO] Total ofertas extraídas: {len(ofertas)}")
    return ofertas
