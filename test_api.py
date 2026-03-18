import requests
import json

def probar_api_rag(pregunta, manual):
    url = "http://localhost:8000/preguntar"  # Asegúrate de que coincida con tu endpoint
    payload = {
        "pregunta": pregunta,
        "manual": manual
    }
    headers = {'Content-Type': 'application/json'}

    try:
        print(f"\n--- Enviando consulta para el manual: {manual} ---")
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Respuesta del LLM:\n{data['respuesta']}")
            print("\nFuentes detectadas:")
            for f in data['fuentes']:
                print(f"- {f}")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"No se pudo conectar con la API: {e}")

if __name__ == "__main__":
    # Prueba 1: Consulta sobre MZ 9.4
    probar_api_rag("¿Cómo se configura un Analysis Agent?", "md94")
    
    # Prueba 2: Consulta sobre UECE
    probar_api_rag("¿Cuáles son los pasos para el despliegue en la nube?", "uepe_cloud")