#!/usr/bin/env python3
"""
TrafficTamer API REST - Control remoto desde cualquier dispositivo
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import platform
import json
import threading

app = Flask(__name__)
CORS(app)  # Permitir acceso desde cualquier origen

# Estado global
os_type = platform.system()

def run_capture(cmd):
    """Ejecutar comando y capturar salida"""
    try:
        if isinstance(cmd, list):
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        else:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=5)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/api/status', methods=['GET'])
def get_status():
    """Estado general del sistema"""
    interface = request.args.get('interface', 'eth0')
    
    status = {
        "os": os_type,
        "interface": interface,
        "api_version": "2.0",
        "features": {
            "bandwidth": True,
            "latency": os_type == "Linux",
            "loss": os_type == "Linux",
            "corruption": os_type == "Linux",
            "qos_by_app": os_type == "Windows"
        }
    }
    
    # Obtener reglas actuales en Linux
    if os_type == "Linux":
        result = run_capture(f"tc qdisc show dev {interface}")
        if result["success"]:
            status["current_rules"] = result["stdout"]
    
    return jsonify(status)

@app.route('/api/bandwidth', methods=['POST'])
def set_bandwidth():
    """Limitar ancho de banda"""
    data = request.json
    interface = data.get('interface', 'eth0')
    rate_mbps = data.get('rate')
    
    if not rate_mbps:
        return jsonify({"error": "Falta parámetro 'rate' (Mbps)"}), 400
    
    if os_type == "Linux":
        # Usar sudo con tc
        cmd = f"tc qdisc add dev {interface} root handle 1: htb default 30 && tc class add dev {interface} parent 1: classid 1:1 htb rate {rate_mbps}mbit"
        result = run_capture(f"sudo {cmd}")
    else:
        # Windows QoS policy
        cmd = f"powershell -Command \"New-NetQosPolicy -Name 'API_TrafficTamer_{rate_mbps}' -ThrottleRateActionBitsPerSecond {rate_mbps * 1000000}\""
        result = run_capture(cmd)
    
    return jsonify(result)

@app.route('/api/latency', methods=['POST'])
def set_latency():
    """Añadir latencia"""
    data = request.json
    interface = data.get('interface', 'eth0')
    delay_ms = data.get('delay')
    
    if not delay_ms:
        return jsonify({"error": "Falta parámetro 'delay' (ms)"}), 400
    
    if os_type == "Linux":
        cmd = f"tc qdisc add dev {interface} root netem delay {delay_ms}ms"
        result = run_capture(f"sudo {cmd}")
    else:
        result = {"success": False, "error": "Latency not supported natively on Windows"}
    
    return jsonify(result)

@app.route('/api/loss', methods=['POST'])
def set_loss():
    """Añadir pérdida de paquetes"""
    data = request.json
    interface = data.get('interface', 'eth0')
    loss_percent = data.get('loss')
    
    if not loss_percent:
        return jsonify({"error": "Falta parámetro 'loss' (%)"}), 400
    
    if os_type == "Linux":
        cmd = f"tc qdisc add dev {interface} root netem loss {loss_percent}%"
        result = run_capture(f"sudo {cmd}")
    else:
        result = {"success": False, "error": "Packet loss not supported natively on Windows"}
    
    return jsonify(result)

@app.route('/api/corruption', methods=['POST'])
def set_corruption():
    """Añadir corrupción de paquetes"""
    data = request.json
    interface = data.get('interface', 'eth0')
    corrupt_percent = data.get('corrupt')
    
    if not corrupt_percent:
        return jsonify({"error": "Falta parámetro 'corrupt' (%)"}), 400
    
    if os_type == "Linux":
        cmd = f"tc qdisc add dev {interface} root netem corrupt {corrupt_percent}%"
        result = run_capture(f"sudo {cmd}")
    else:
        result = {"success": False, "error": "Corruption requires Clumsy on Windows"}
    
    return jsonify(result)

@app.route('/api/reset', methods=['POST'])
def reset_rules():
    """Resetear todas las reglas de tráfico"""
    data = request.json
    interface = data.get('interface', 'eth0')
    
    if os_type == "Linux":
        cmd = f"tc qdisc del dev {interface} root"
        result = run_capture(f"sudo {cmd}")
    else:
        # Limpiar políticas QoS de Windows
        cmd = "powershell -Command \"Get-NetQosPolicy | Where-Object {$_.Name -like 'API_*'} | Remove-NetQosPolicy\""
        result = run_capture(cmd)
    
    return jsonify(result)

@app.route('/api/policies', methods=['GET'])
def list_policies():
    """Listar políticas QoS (Windows) o reglas tc (Linux)"""
    if os_type == "Windows":
        cmd = "powershell -Command \"Get-NetQosPolicy | Select-Object Name, AppPathName, ThrottleRate\""
        result = run_capture(cmd)
    else:
        interface = request.args.get('interface', 'eth0')
        cmd = f"tc qdisc show dev {interface}"
        result = run_capture(cmd)
    
    return jsonify(result)

@app.route('/api/qos/app', methods=['POST'])
def qos_by_app():
    """Configurar QoS por aplicación (solo Windows)"""
    if os_type != "Windows":
        return jsonify({"error": "QoS by app only on Windows"}), 400
    
    data = request.json
    app_path = data.get('app_path')
    rate_mbps = data.get('rate')
    dscp = data.get('dscp')
    
    if not app_path:
        return jsonify({"error": "Falta 'app_path'"}), 400
    
    cmd = "powershell -Command \""
    if rate_mbps:
        bits = rate_mbps * 1000000
        cmd += f"New-NetQosPolicy -Name 'API_App_{app_path.split(chr(92))[-1]}' -AppPathNameMatchCondition '{app_path}' -ThrottleRateActionBitsPerSecond {bits}; "
    if dscp:
        cmd += f"New-NetQosPolicy -Name 'API_App_{app_path.split(chr(92))[-1]}_DSCP' -AppPathNameMatchCondition '{app_path}' -DSCPAction {dscp}; "
    cmd += "\""
    
    result = run_capture(cmd)
    return jsonify(result)

@app.route('/api/qos/port', methods=['POST'])
def qos_by_port():
    """Configurar QoS por puerto (Windows)"""
    if os_type != "Windows":
        return jsonify({"error": "QoS by port only on Windows"}), 400
    
    data = request.json
    port = data.get('port')
    rate_mbps = data.get('rate')
    
    if not port:
        return jsonify({"error": "Falta 'port'"}), 400
    
    cmd = f"powershell -Command \"New-NetQosPolicy -Name 'API_Port{port}' -IPPortMatchCondition {port} -ThrottleRateActionBitsPerSecond {rate_mbps * 1000000}\""
    result = run_capture(cmd)
    return jsonify(result)

def run_api_server(port=5000):
    """Iniciar servidor API"""
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

if __name__ == "__main__":
    print("🌐 TrafficTamer API Server")
    print("📡 Escuchando en todas las interfaces")
    print("📍 Puerto: 5000")
    print("\nEjemplos de uso:")
    print("  curl http://localhost:5000/api/status")
    print('  curl -X POST http://localhost:5000/api/bandwidth -H "Content-Type: application/json" -d \'{"interface":"eth0","rate":10}\'')
    print('  curl -X POST http://localhost:5000/api/latency -H "Content-Type: application/json" -d \'{"interface":"eth0","delay":100}\'')
    print("\nPresiona Ctrl+C para detener\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
