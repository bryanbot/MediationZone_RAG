import json
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

def cargar_datos_locales(ruta_archivo):
    """
    Lee el archivo JSON guardado en el Paso 1.
    """
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
            print(f"✅ Archivo '{ruta_archivo}' cargado correctamente.")
            return datos
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo en la ruta '{ruta_archivo}'.")
        return None

def procesar_chunks_markdown(datos_json):
    """
    Divide el contenido Markdown en chunks e inyecta los metadatos de Atlassian.
    """
    headers_to_split_on = [
        ("#", "Título Principal"),
        ("##", "Subtítulo Nivel 1"),
        ("###", "Subtítulo Nivel 2"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, 
        chunk_overlap=250,
        separators=["\n\n", "\n", " ", "", "\n## ", "\n### "]
    )

    chunks_finales = []

    # Iterar sobre cada documento guardado
    for item in datos_json:
        texto_md = item.get("contenido_markdown", "")
        # Extraemos los metadatos personalizados que guardó el extractor
        titulo = item.get("titulo_pagina", "Sin Título")
        ruta = item.get("ruta_completa", "Desconocida")

        if not texto_md:
            continue
            
        # A. Cortar por títulos
        splits_por_titulos = markdown_splitter.split_text(texto_md)
        
        # NUEVO: Inyectar la metadata de Atlassian a cada pedacito
        for split in splits_por_titulos:
            split.metadata["titulo_pagina"] = titulo
            split.metadata["ruta_original"] = ruta

        # B. Aplicar red de seguridad por tamaño
        splits_finales = text_splitter.split_documents(splits_por_titulos)
        
        chunks_finales.extend(splits_finales)

    return chunks_finales

# ==========================================
# EJECUCIÓN DEL PASO 2
# ==========================================
if __name__ == "__main__":
    print("=== Iniciando Paso 2: Chunking ===")
    
    # NUEVO: Le pasamos una ruta de prueba (ej. UEPE) para cuando corras el script directamente
    ruta_prueba = "data_output/datos_uepe.json"

    # 1. Cargar el JSON del disco duro
    datos = cargar_datos_locales(ruta_prueba)
    
    if datos:
        print(f"Se cargaron {len(datos)} páginas limpias desde el archivo local.")
        
        # 2. Generar los chunks
        mis_chunks = procesar_chunks_markdown(datos)
        
        print(f"✅ Éxito: Se generaron {len(mis_chunks)} fragmentos estructurados listos para vectorizar.")
        
        # Opcional: ver un ejemplo
        if len(mis_chunks) > 0:
            print("\n--- MUESTRA DEL PRIMER CHUNK ---")
            print(f"Metadatos: {mis_chunks[0].metadata}")
            print(f"Contenido: {mis_chunks[0].page_content[:200]}...")