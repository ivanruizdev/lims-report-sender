from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Inicializamos la aplicación FastAPI
app = FastAPI(title="LIMS-Bridge API")

# ==========================================
# Configuración CORS (¡Crítico para Vue!)
# ==========================================
# Permite que el panel de Vue (en el puerto 5173) 
# pueda hacerle peticiones a Python (en el puerto 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # URL de tu servidor de desarrollo Vue
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Estado en Memoria (Simulado temporalmente)
# ==========================================
bot_state = {
    "running": False,
    "enviadosHoy": 47
}

queue_data = [
    { "id": "99801", "paciente": "Roberto Sánchez", "status": "pending", "time": "14:10 PM", "channels": ["whatsapp"] },
    { "id": "99802", "paciente": "Lucía Méndez", "status": "pending", "time": "14:15 PM", "channels": ["telegram"] }
]

history_data = [
    { "id": "99799", "paciente": "Fernando Gómez", "status": "success", "time": "13:50 PM", "channels": ["whatsapp"] }
]

# ==========================================
# Rutas de la API (Endpoints)
# ==========================================

@app.get("/api/status")
def get_system_status():
    """Devuelve el estado general del bot y las estadísticas."""
    return {
        "botRunning": bot_state["running"],
        "apiStatus": {
            "telegram": "conectado",
            "whatsapp": "conectado"
        },
        "stats": {
            "enviadosHoy": bot_state["enviadosHoy"],
            "pendientes": len(queue_data)
        }
    }

@app.get("/api/queue")
def get_queue():
    """Devuelve la lista de estudios pendientes de envío."""
    return queue_data

@app.get("/api/history")
def get_history():
    """Devuelve el historial de los últimos envíos exitosos."""
    return history_data

@app.post("/api/bot/toggle")
def toggle_bot():
    """Enciende o apaga el motor de envíos"""
    bot_state["running"] = not bot_state["running"]
    return {"botRunning": bot_state["running"]}

@app.delete("/api/queue/{item_id}")
def delete_queue_item(item_id: str):
    """Elimina un elemento específico de la cola"""
    global queue_data
    queue_data = [item for item in queue_data if item["id"] != item_id]
    return {"message": "Eliminado correctamente", "pendientes": len(queue_data)}

# Ruta de prueba simple
@app.get("/")
def read_root():
    return {"mensaje": "LIMS-Report-Sender API está funcionando correctamente"}

static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_path, "assets")), name="assets")

# 2. Servir el index.html de Vue en la ruta raíz
@app.get("/")
def serve_vue_app():
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"mensaje": "API funcionando, pero no se encontró el frontend de Vue (index.html)"}