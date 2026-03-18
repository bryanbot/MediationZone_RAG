import os
from motor_rag_ollama import configurar_motor_busqueda_local

class MotorRAGFactory:
    def __init__(self):
        self._motores_cacheados = {}

    def obtener_motor(self, nombre_manual: str):
        # En lugar de revisar una lista, revisamos si la carpeta existe en el disco duro
        ruta_base = f"./bases_vectoriales/{nombre_manual}"
        
        if not os.path.exists(ruta_base):
            raise ValueError(f"No se encontró la base de datos para el manual '{nombre_manual}'.")

        if nombre_manual in self._motores_cacheados:
            return self._motores_cacheados[nombre_manual]

        print(f"⚙️ Fabricando y cargando en memoria el motor para: {nombre_manual}...")
        nuevo_motor = configurar_motor_busqueda_local(nombre_doc=nombre_manual)
        self._motores_cacheados[nombre_manual] = nuevo_motor
        return nuevo_motor