# TrafficTamer 🦾

## 🚀 Inicio Rápido
```bash
pip install -r requirements.txt

# CLI
sudo python3 traffic_tamer.py -i eth0 -b 10

# GUI
python3 traffic_tamer_gui.py

# API
python3 traffic_tamer_api.py

🚀 Cómo usarlo todo junto

1. Iniciar la GUI
python3 traffic_tamer_gui.py
# o en Windows: python traffic_tamer_gui.py

2. Iniciar la API (desde otra terminal)
python3 traffic_tamer_api.py

3. Abrir el dashboard web
Abre web_dashboard/index.html en tu navegador o súbelo a un servidor web.

4. Control remoto desde cualquier dispositivo
# Desde otro PC en la misma red
curl http://192.168.1.100:5000/api/status

# Límite de banda
curl -X POST http://192.168.1.100:5000/api/bandwidth \
  -H "Content-Type: application/json" \
  -d '{"interface":"eth0","rate":10}'

🌐 API Endpoints

    GET /api/status - Estado del sistema

    POST /api/bandwidth - Limitar ancho de banda

    POST /api/latency - Añadir latencia

    POST /api/loss - Pérdida de paquetes

    POST /api/corruption - Corrupción de paquetes

    POST /api/reset - Resetear reglas

    GET /api/policies - Listar políticas

📱 Control Remoto

curl http://localhost:5000/api/status
