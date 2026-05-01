# TrafficTamer 🦾

Cross-platform CLI tool to shape and control network traffic on **Linux** and **Windows**.

## Features
- 📉 Bandwidth limiting (Mbps)
- ⏱️ Artificial latency (ms)
- 📦 Packet loss simulation (%)
- 🔄 Reset all rules
- 📊 Show current configuration

## Installation
```bash
git clone https://github.com/Falconmx1/TrafficTamer.git
cd TrafficTamer
pip install -r requirements.txt  # optional
chmod +x traffic_tamer.py

Usage
Linux (needs sudo)
sudo python3 traffic_tamer.py -i eth0 -b 10        # Limit to 10 Mbps
sudo python3 traffic_tamer.py -i eth0 -d 100       # Add 100ms latency
sudo python3 traffic_tamer.py -i eth0 -l 5         # 5% packet loss
sudo python3 traffic_tamer.py -i eth0 --reset      # Clean everything

Windows (needs Admin)
python traffic_tamer.py -i "Ethernet" -b 10
python traffic_tamer.py -i "Wi-Fi" --status

📦 Ejemplos de uso en Windows
# QoS por aplicación - Limitar Firefox a 5 Mbps
python traffic_tamer.py --app "C:\Program Files\Mozilla Firefox\firefox.exe" --app-rate 5

# Prioridad alta para Discord (DSCP 46 = Expedited Forwarding)
python traffic_tamer.py --app "C:\Users\%USERNAME%\AppData\Local\Discord\app-1.0\Discord.exe" --app-dscp 46

# Limitar puerto 443 (HTTPS) a 2 Mbps
python traffic_tamer.py --port 443 --port-rate 2

# Desactivar TCP Autotuning para estabilidad en gaming [citation:1]
python traffic_tamer.py --tcp-autotuning disabled

# Limitar Windows Updates a 10 Mbps background
python traffic_tamer.py --update-bg 10

# Ver todas las políticas activas
python traffic_tamer.py --list-policies

# Limpiar todo
python traffic_tamer.py --clear-policies

🔧 Corrupción y pérdida en Windows (con Clumsy)
# Instalar Clumsy (solo una vez)
# Ve a https://github.com/jagt/clumsy/releases, descarga clumsy-0.3.exe

# Corromper 5% de paquetes a puerto 443
python traffic_tamer.py --clumsy-corrupt "tcp.DstPort == 443" 0.05

# Perder 10% de paquetes a un IP específico
python traffic_tamer.py --clumsy-loss "tcp.DstPort == 80 and ip.DstAddr == 192.168.1.100" 0.1

🐧 Ejemplos nuevos en Linux
# Corromper 5% de paquetes
sudo python3 traffic_tamer.py -i eth0 --corrupt 5

# Duplicar 10% de paquetes
sudo python3 traffic_tamer.py -i eth0 --duplicate 10

# Reordenar 20% de paquetes con 50ms de delay
sudo python3 traffic_tamer.py -i eth0 --delay 50 --reorder 20

# Jitter: 100ms base ±20ms
sudo python3 traffic_tamer.py -i eth0 --delay 100 --jitter 20
