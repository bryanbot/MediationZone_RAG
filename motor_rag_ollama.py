from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
# IMPORTACIÓN NUEVA: Traemos ChatOllama en lugar de ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

def configurar_motor_busqueda_local(nombre_doc):
    print(f"--- Configurando Motor RAG para: {nombre_doc} ---")

    # 1. DETERMINAR EL PRODUCTO DINÁMICAMENTE
    # Esto asegura que Llama 3 sepa exactamente sobre qué software está hablando.
    if "md94" in nombre_doc.lower():
        producto = "MediationZone 9.4 (On-Premise)"
    elif "uece" in nombre_doc.lower() or "uece" in nombre_doc.lower():
        producto = "Usage Engine Cloud Edition (UECE)"
    elif "uepe" in nombre_doc.lower() or "uepe" in nombre_doc.lower():
        producto = "Usage Engine Private Edition (UEPE)"
    else:
        producto = "DigitalRoute Software"

    # 1. CARGAR LA BASE DE DATOS Y EMBEDDINGS LOCALES
    #modelo_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    modelo_embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    directorio_db = f"./bases_vectoriales/{nombre_doc}"
    
    print(f"Cargando base de datos: {directorio_db}")
    
    vectorstore = Chroma(
        collection_name=nombre_doc, # NUEVO: Le da un ID interno único
        persist_directory=directorio_db, 
        embedding_function=modelo_embeddings
    )
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

    # 2. CONFIGURAR EL LLM LOCAL (OLLAMA)
    # Aquí es donde ocurre la magia del cambio. 
    # Le decimos a LangChain que se conecte al servicio de Ollama que corre en tu máquina.
    llm = ChatOllama(
        model="llama3",
        temperature=0, # Mantenemos temperatura 0 para respuestas técnicas precisas
        num_ctx=4096,
    )

    # 3. CREAR EL SYSTEM PROMPT (Se mantiene igual)
    system_prompt = (
        f"Eres un asistente técnico experto en {producto}. "
        "Tu objetivo es ayudar a ingenieros de mediación con configuraciones, APL y despliegue. "
        "Utiliza ÚNICAMENTE los siguientes fragmentos de contexto recuperados de la documentación oficial "
        "para responder a la pregunta. "
        f"Si la información no está presente, indica que no se encuentra en los manuales de {producto}. "
        "Mantén un tono profesional y proporciona ejemplos de código o comandos si están disponibles."
        "\n\n"
        "Contexto:\n{context}"
    )

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # 4. UNIR TODO EN UNA CADENA
    question_answer_chain = create_stuff_documents_chain(llm, prompt_template)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    print(f"✅ Motor para {producto} cargado correctamente.\n")
    return rag_chain

# ==========================================
# EJECUCIÓN DE PRUEBA
# ==========================================
if __name__ == "__main__":
    # Prueba rápida con MZ 9.4
    motor = configurar_motor_busqueda_local(nombre_doc="md94")
    pregunta = "¿Cómo configurar un Agent Group en MZ?"
    respuesta = motor.invoke({"input": pregunta})
    print(f"Respuesta: {respuesta['answer']}")
    
    print("\n✅ ¡Sistema 100% Local listo! Escribe 'salir' para terminar.")
    
    while True:
        pregunta = input("\nPregunta sobre la instalación: ")
        if pregunta.lower() in ['salir', 'exit', 'quit']:
            break
            
        print("Consultando base vectorial y procesando con Llama 3 (esto depende de la velocidad de tu PC)...")
        
        # Ejecutamos la consulta
        respuesta = motor.invoke({"input": pregunta})
        
        print("\n--- RESPUESTA (LLAMA 3) ---")
        print(respuesta["answer"])
        
        print("\n--- FUENTES UTILIZADAS ---")
        for i, doc in enumerate(respuesta["context"]):
            metadata = doc.metadata
            print(f"- Fuente {i+1}: {metadata}")