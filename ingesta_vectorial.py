import os
# Importamos la integración de HuggingFace para embeddings locales
from langchain_huggingface import HuggingFaceEmbeddings
# Importamos ChromaDB, nuestra base de datos vectorial
from langchain_community.vectorstores import Chroma
from tqdm import tqdm

# 1. IMPORTAMOS TUS FUNCIONES DEL PASO 2 (El Orquestador)
from procesador_chunks import cargar_datos_locales, procesar_chunks_markdown

def construir_base_vectorial(nombre_doc, ruta_json):
    """
    Ejecuta el flujo completo: lee el JSON, hace el chunking, 
    calcula los embeddings y los guarda en ChromaDB.
    """
    print("=== Iniciando Ingesta Vectorial ===")
    
    # --- PASO 1 Y 2: Obtener los Chunks ---
    datos_json = cargar_datos_locales(ruta_json)
    
    if not datos_json:
        print("Deteniendo proceso: No hay datos para ingerir.")
        return None

    print("Cortando el texto en fragmentos lógicos...")
    mis_chunks = procesar_chunks_markdown(datos_json)
    print(f"Obtenidos {len(mis_chunks)} chunks para procesar.\n")

    # --- PASO 3: Configurar el Modelo de Embeddings ---
    # La primera vez que ejecutes esto, descargará el modelo (~80MB) a tu máquina.
    # Las siguientes veces será instantáneo.
    print("Cargando modelo de Embeddings local (BAAI/bge-m3)...")
    #modelo_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    modelo_embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

    # --- PASO 4: Ingesta en la Base de Datos Vectorial ---
    # Definimos la carpeta donde Chroma guardará los datos físicamente
    directorio_db = f"./bases_vectoriales/{nombre_doc}"
    os.makedirs(directorio_db, exist_ok=True) # Crea la carpeta si no existe
    tamano_lote = 150 # Procesaremos de 150 en 150 chunks

    print(f"\nIniciando vectorización en lotes de {tamano_lote}...")

    print(f"Convirtiendo texto a vectores y guardando en {directorio_db} (esto puede tomar unos segundos)...")
    
    # Esta única línea hace toda la magia: 
    # Recorre tus chunks, los pasa por el modelo matemático y los guarda en disco.
    vectorstore = Chroma(
        collection_name=nombre_doc, # NUEVO: Le da un ID interno único
        persist_directory=directorio_db,
        embedding_function=modelo_embeddings
    )

    print(f"\nIniciando vectorización de {len(mis_chunks)} chunks en lotes de {tamano_lote}...")

    # Iteramos usando tqdm para ver una hermosa barra de progreso en la terminal
    for i in tqdm(range(0, len(mis_chunks), tamano_lote), desc="Progreso de Ingesta"):
        lote_actual = mis_chunks[i : i + tamano_lote]
        
        # Agregamos solo este pequeño lote a la base de datos
        vectorstore.add_documents(lote_actual)

    print("\n✅ ¡Ingesta completada con éxito!")
    print(f"Tus instrucciones de instalación ahora viven como vectores matemáticos en la carpeta '{directorio_db}'.")
    
    return vectorstore

# ==========================================
# EJECUCIÓN DEL SCRIPT
# ==========================================
if __name__ == "__main__":
    construir_base_vectorial(nombre_doc="uepe", ruta_json="data_output/datos_uepe.json")