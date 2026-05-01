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
