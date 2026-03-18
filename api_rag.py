from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from contextlib import asynccontextmanager
import uvicorn

# Importamos tu motor RAG 100% local
from motor_rag_ollama import configurar_motor_busqueda_local

# ==========================================
# 1. VARIABLES GLOBALES
# ==========================================
# VITAL: Inicializar como diccionario vacío, NO como None
motores_rag = {}

# ==========================================
# 2. ESQUEMAS DE DATOS (Pydantic)
# ==========================================
class PreguntaRequest(BaseModel):
    pregunta: str
    manual: str # Ej: "md94" o "uepe_cloud"

class RespuestaRAG(BaseModel):
    respuesta: str
    fuentes: List[Dict[str, Any]]

# ==========================================
# 3. EVENTOS DE INICIO
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Código de Inicio (Startup) ---
    global motores_rag
    print("Iniciando servidor: Cargando el motor RAG de Llama 3 en memoria...")

    # Cargamos ambas bases de datos. Asegúrate de que los nombres de las carpetas coincidan.
    motores_rag["md94"] = configurar_motor_busqueda_local(nombre_doc="md94")
    motores_rag["uepe"] = configurar_motor_busqueda_local(nombre_doc="uepe")

    print("✅ Motores RAG cargados y listos para recibir peticiones HTTP.")
    
    yield # Aquí es donde la aplicación se queda "escuchando" peticiones
    
    # --- Código de Apagado (Shutdown) ---
    print("🛑 Apagando el servidor y liberando memoria...")
    motores_rag = {}

# ==========================================
# 4. DEFINICIÓN DE LA API Y CORS
# ==========================================
app = FastAPI(
    title="API de Documentación Atlassian",
    description="Microservicio RAG local multi-documento usando Llama 3.",
    version="1.0.0",
    lifespan=lifespan
)

# Habilitar CORS para que el index.html pueda comunicarse con esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 4. ENDPOINTS (Rutas)
# ==========================================
# Le decimos a FastAPI dónde están los archivos de la interfaz web
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Cuando alguien entre a la URL principal "/", le mostramos el index.html
@app.get("/")
async def cargar_interfaz():
    return FileResponse("frontend/index.html")

@app.post("/preguntar", response_model=RespuestaRAG)
async def procesar_pregunta(request: PreguntaRequest):
    """
    Recibe una pregunta en JSON, consulta a Llama 3 y devuelve la respuesta.
    """
    print("Iniciando servidor: Cargando los motores RAG...")
    
    if not motores_rag:
        raise HTTPException(status_code=500, detail="Los motores RAG aún no han cargado en memoria.")
    
    if request.manual not in motores_rag:
        raise HTTPException(status_code=404, detail=f"El manual '{request.manual}' no está disponible.")
    
    try:
        print(f"\n🧠 [Consulta en {request.manual}]: '{request.pregunta}'")
        motor_seleccionado = motores_rag[request.manual]

        # Ejecutamos la consulta en el motor (solo una vez)
        resultado = motor_seleccionado.invoke({"input": request.pregunta})
        
        # Extraemos la metadata
        fuentes_usadas = [doc.metadata for doc in resultado["context"]]
        
        # Devolvemos el JSON
        return RespuestaRAG(
            respuesta=resultado["answer"],
            fuentes=fuentes_usadas
        )
        
    except Exception as e:
        print(f"❌ Error procesando la consulta: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar la pregunta con el LLM.")

import os

# Agrega esto debajo de tus otras rutas
@app.get("/manuales")
async def listar_manuales_disponibles():
    """Escanea la carpeta local y devuelve los manuales que ya fueron vectorizados."""
    try:
        # Lee los nombres de las carpetas dentro de bases_vectoriales
        carpetas = [nombre for nombre in os.listdir("./bases_vectoriales") 
                    if os.path.isdir(os.path.join("./bases_vectoriales", nombre))]
        return {"manuales": carpetas}
    except FileNotFoundError:
        return {"manuales": []}

# ==========================================
# 5. PUNTO DE ENTRADA
# ==========================================
if __name__ == "__main__":
    # Ejecutamos el servidor en el puerto 8000
    uvicorn.run("api_rag:app", host="0.0.0.0", port=8000, reload=True)