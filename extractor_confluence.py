import requests
import json
import os
import time
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from markdownify import markdownify
import re

# Lista global donde guardaremos todo
documentos_totales_rag = []

# ==========================================
# 1. FUNCIONES DE LIMPIEZA
# ==========================================
def limpiar_html_a_markdown(html_content):
    """Limpia el HTML de Atlassian y lo pasa a Markdown."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
        tag.decompose()
    texto_md = markdownify(str(soup), heading_style="ATX")
	
	# Limpieza Regex
    texto_md = re.sub(r'^[ \t]+', '', texto_md, flags=re.MULTILINE)
    texto_md = re.sub(r'\n{3,}', '\n\n', texto_md)
    texto_md = texto_md.strip()
	
    return texto_md.strip()

# ==========================================
# 2. FUNCIONES DE RED CON REINTENTOS (RATE LIMITING)
# ==========================================
def obtener_pagina_completa(page_id, max_reintentos=4):
    headers = {"Accept": "application/json"}
    url_pagina = f"https://infozone.atlassian.net/wiki/rest/api/content/{page_id}?expand=body.view"
    
    for intento in range(max_reintentos):
        try:
            response = requests.get(url_pagina, headers=headers, timeout=15)
            if response.status_code == 429:
                espera = 5 * (intento + 1)
                print(f"  ⚠️ Rate limit en página {page_id}. Pausando {espera}s...")
                time.sleep(espera)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error al obtener página {page_id}: {e}")
            time.sleep(3)
    return None

def obtener_hijos_de_pagina(page_id, max_reintentos=4):
    headers = {"Accept": "application/json"}
    url_hijos = f"https://infozone.atlassian.net/wiki/rest/api/content/{page_id}/child/page"
    
    for intento in range(max_reintentos):
        try:
            response = requests.get(url_hijos, headers=headers, timeout=15)
            if response.status_code == 429:
                espera = 5 * (intento + 1)
                print(f"  ⚠️ Rate limit buscando hijos de {page_id}. Pausando {espera}s...")
                time.sleep(espera)
                continue
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error al buscar hijos de {page_id}: {e}")
            time.sleep(3)
    return []

# ==========================================
# 3. EL MOTOR RECURSIVO
# ==========================================
def descargar_arbol_recursivo(page_id, ruta_padre=""):
    print(f"\n🔄 Consultando ID: {page_id}...")
    
    # A. Extraer la página actual
    pagina = obtener_pagina_completa(page_id)
    if not pagina:
        return

    titulo = pagina.get("title", "Sin_Titulo")
    ruta_actual = f"{ruta_padre} > {titulo}" if ruta_padre else titulo
    print(f"  📖 Procesando: {ruta_actual}")

    html = pagina.get("body", {}).get("view", {}).get("value", "")
    if html:
        md_texto = limpiar_html_a_markdown(html)
        if md_texto:
            # Guardamos el título como metadato y el texto procesado
            documentos_totales_rag.append({
                "titulo_pagina": titulo,
                "ruta_completa": ruta_actual,
                "contenido_markdown": md_texto
            })
    else:
        print(f"  ℹ️ '{titulo}' es un contenedor vacío, sin texto propio.")

    # B. Buscar y procesar hijos
    hijos = obtener_hijos_de_pagina(page_id)
    if hijos:
        print(f"  👉 '{titulo}' tiene {len(hijos)} sub-páginas. Entrando...")
        for hijo in hijos:
            time.sleep(1) # Pausa de respeto para Atlassian
            descargar_arbol_recursivo(hijo["id"], ruta_actual)

# ==========================================
# 4. EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    # --- CONFIGURACIÓN ---
    print("=== ASISTENTE DE EXTRACCIÓN DE ATLASSIAN ===")

    # El sistema te pregunta los datos en vivo
    ROOT_PAGE_ID = input("👉 Ingresa el ID de la página raíz (ej. 352104956): ").strip()
    NOMBRE_PROYECTO = input("👉 Ingresa un nombre corto y sin espacios para este manual (ej. md94): ").strip()
    # ROOT_PAGE_ID = "233635842" # ID de "User Documentation 9.4"
    # NOMBRE_PROYECTO = "uepe" # NUEVO: Ponle un nombre corto sin espacios
    
    # Creamos la carpeta de salida si no existe
    os.makedirs("data_output", exist_ok=True)

    print(f"=== Iniciando Descarga Masiva de {NOMBRE_PROYECTO} ===")
    
    descargar_arbol_recursivo(ROOT_PAGE_ID)
    
    print(f"\n=== ¡Descarga Finalizada! ===")
    print(f"Se extrajeron {len(documentos_totales_rag)} páginas con contenido.")

    # Guardar en JSON
    if documentos_totales_rag:
        ruta_salida = f"data_output/datos_{NOMBRE_PROYECTO}.json"
        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(documentos_totales_rag, f, ensure_ascii=False, indent=4)
        print(f"✅ Datos guardados exitosamente en: {ruta_salida}")