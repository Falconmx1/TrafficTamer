#!/usr/bin/env python3
"""
TrafficTamer GUI - Interfaz gráfica para control de tráfico
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import json
import platform
import os

class TrafficTamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TrafficTamer - Control de Tráfico Profesional")
        self.root.geometry("900x700")
        self.root.configure(bg='#1e1e1e')
        
        self.os_type = platform.system()
        self.current_interface = tk.StringVar(value="eth0" if self.os_type == "Linux" else "Ethernet")
        
        self.setup_styles()
        self.create_widgets()
        self.check_admin()
    
    def setup_styles(self):
        """Configurar estilos modernos"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', foreground='#00ff00', background='#1e1e1e', font=('Arial', 16, 'bold'))
        style.configure('Status.TLabel', foreground='#ffffff', background='#1e1e1e', font=('Consolas', 10))
        style.configure('TLabelframe', background='#2d2d2d', foreground='#ffffff')
        style.configure('TLabelframe.Label', foreground='#00ff00', background='#2d2d2d', font=('Arial', 10, 'bold'))
        style.configure('TButton', background='#3c3c3c', foreground='#ffffff', font=('Arial', 10))
        style.map('TButton', background=[('active', '#005500')])
    
    def check_admin(self):
        """Verificar permisos de administrador"""
        if self.os_type == "Linux":
            if os.geteuid() != 0:
                messagebox.showwarning("Permisos", "Ejecuta con sudo para funcionalidad completa en Linux")
        elif self.os_type == "Windows":
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                messagebox.showwarning("Permisos", "Ejecuta como Administrador para QoS y control de tráfico")
    
    def create_widgets(self):
        """Crear toda la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title = ttk.Label(main_frame, text="🦾 TRAFFICTAMER - Control Total de tu Red", style='Title.TLabel')
        title.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Notebook (pestañas)
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Crear pestañas
        self.create_tab_basic(notebook)
        self.create_tab_advanced(notebook)
        self.create_tab_qos(notebook)
        self.create_tab_status(notebook)
        self.create_tab_api(notebook)
    
    def create_tab_basic(self, notebook):
        """Pestaña básica: bandwidth, delay, loss"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📊 Básico")
        
        row = 0
        # Interfaz
        ttk.Label(tab, text="Interfaz de Red:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(tab, textvariable=self.current_interface, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Bandwidth limit
        ttk.Label(tab, text="Límite de Ancho de Banda (Mbps):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.bw_entry = ttk.Entry(tab, width=15)
        self.bw_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Button(tab, text="Aplicar", command=self.apply_bandwidth).grid(row=row, column=2, padx=10)
        row += 1
        
        # Latency
        ttk.Label(tab, text="Latencia (ms):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.latency_entry = ttk.Entry(tab, width=15)
        self.latency_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Button(tab, text="Aplicar", command=self.apply_latency).grid(row=row, column=2, padx=10)
        row += 1
        
        # Packet loss
        ttk.Label(tab, text="Pérdida de Paquetes (%):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.loss_entry = ttk.Entry(tab, width=15)
        self.loss_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Button(tab, text="Aplicar", command=self.apply_loss).grid(row=row, column=2, padx=10)
        row += 1
        
        # Botones de acción
        ttk.Separator(tab, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        row += 1
        
        ttk.Button(tab, text="🔄 RESET TODO", command=self.reset_all).grid(row=row, column=0, pady=10, padx=5)
        ttk.Button(tab, text="📊 Ver Estado", command=self.show_status).grid(row=row, column=1, pady=10, padx=5)
    
    def create_tab_advanced(self, notebook):
        """Pestaña avanzada: corruption, duplicate, reorder, jitter"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="⚙️ Avanzado")
        
        row = 0
        
        # Corrupción
        ttk.Label(tab, text="Corrupción de Paquetes (%):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.corrupt_entry = ttk.Entry(tab, width=15)
        self.corrupt_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Button(tab, text="Aplicar", command=self.apply_corruption).grid(row=row, column=2, padx=10)
        row += 1
        
        # Duplicación
        ttk.Label(tab, text="Duplicación de Paquetes (%):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.duplicate_entry = ttk.Entry(tab, width=15)
        self.duplicate_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Button(tab, text="Aplicar", command=self.apply_duplicate).grid(row=row, column=2, padx=10)
        row += 1
        
        # Reordenamiento
        ttk.Label(tab, text="Reordenamiento (% probabilidad):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.reorder_entry = ttk.Entry(tab, width=15)
        self.reorder_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Button(tab, text="Aplicar", command=self.apply_reorder).grid(row=row, column=2, padx=10)
        row += 1
        
        # Jitter
        ttk.Label(tab, text="Jitter (ms, requiere delay):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.jitter_entry = ttk.Entry(tab, width=15)
        self.jitter_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Button(tab, text="Aplicar", command=self.apply_jitter).grid(row=row, column=2, padx=10)
        row += 1
        
        # Nota para Windows
        if self.os_type == "Windows":
            ttk.Label(tab, text="⚠️ En Windows, estas funciones requieren Clumsy", 
                     foreground="#ffaa00").grid(row=row, column=0, columnspan=3, pady=20)
    
    def create_tab_qos(self, notebook):
        """Pestaña QoS por aplicación (Windows)"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="🎯 QoS por App")
        
        row = 0
        
        ttk.Label(tab, text="Ruta del ejecutable:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.qos_app_path = ttk.Entry(tab, width=50)
        self.qos_app_path.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Label(tab, text="Límite (Mbps):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.qos_rate = ttk.Entry(tab, width=15)
        self.qos_rate.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Label(tab, text="Prioridad DSCP (0-63):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.qos_dscp = ttk.Entry(tab, width=15)
        self.qos_dscp.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Button(tab, text="Aplicar QoS", command=self.apply_qos_app).grid(row=row, column=0, columnspan=2, pady=20)
        row += 1
        
        ttk.Button(tab, text="Listar Políticas", command=self.list_policies).grid(row=row, column=0, pady=5)
        ttk.Button(tab, text="Limpiar Políticas", command=self.clear_policies).grid(row=row, column=1, pady=5)
        
        if self.os_type == "Linux":
            ttk.Label(tab, text="ℹ️ QoS por app es nativo en Windows. En Linux usa CLI.", 
                     foreground="#00ff00").grid(row=row+1, column=0, columnspan=2, pady=20)
    
    def create_tab_status(self, notebook):
        """Pestaña de estado y logs"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📈 Estado")
        
        # Text area para logs
        self.log_text = scrolledtext.ScrolledText(tab, height=20, width=80, bg='#1e1e1e', fg='#00ff00', font=('Consolas', 9))
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Botón refresh
        ttk.Button(tab, text="🔄 Refrescar Estado", command=self.refresh_status).pack(pady=5)
    
    def create_tab_api(self, notebook):
        """Pestaña para control API REST"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="🌐 API REST")
        
        row = 0
        
        ttk.Label(tab, text="Estado API:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.api_status = ttk.Label(tab, text="Detenida", foreground="red")
        self.api_status.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Label(tab, text="Puerto API:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.api_port = ttk.Entry(tab, width=10)
        self.api_port.insert(0, "5000")
        self.api_port.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Button(tab, text="▶️ Iniciar API", command=self.start_api).grid(row=row, column=0, pady=10, padx=5)
        ttk.Button(tab, text="⏹️ Detener API", command=self.stop_api).grid(row=row, column=1, pady=10, padx=5)
        row += 1
        
        ttk.Label(tab, text="Endpoints disponibles:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=10)
        row += 1
        
        endpoints = """
        GET  /api/status           - Estado del sistema
        POST /api/bandwidth        - Limitar ancho de banda {'interface':'eth0','rate':10}
        POST /api/latency          - Añadir latencia {'interface':'eth0','delay':100}
        POST /api/loss             - Pérdida de paquetes {'interface':'eth0','loss':5}
        POST /api/corruption       - Corrupción {'interface':'eth0','corrupt':5}
        POST /api/reset            - Resetear reglas {'interface':'eth0'}
        GET  /api/policies  (Win)  - Listar QoS policies
        """
        
        endpoint_text = tk.Text(tab, height=10, width=60, bg='#1e1e1e', fg='#00ff00', font=('Consolas', 9))
        endpoint_text.insert('1.0', endpoints)
        endpoint_text.config(state=tk.DISABLED)
        endpoint_text.grid(row=row, column=0, columnspan=2, pady=10, padx=5)
    
    # ============ FUNCIONES DE CONTROL ============
    
    def run_command(self, cmd):
        """Ejecutar comando y loggear"""
        self.log(f"Ejecutando: {cmd}")
        try:
            if isinstance(cmd, list):
                result = subprocess.run(cmd, capture_output=True, text=True)
            else:
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log(f"✅ Éxito: {result.stdout[:200]}")
            else:
                self.log(f"❌ Error: {result.stderr[:200]}")
            return result
        except Exception as e:
            self.log(f"❌ Excepción: {str(e)}")
            return None
    
    def log(self, message):
        """Añadir mensaje al log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def apply_bandwidth(self):
        rate = self.bw_entry.get()
        if not rate:
            return
        interface = self.current_interface.get()
        
        if self.os_type == "Linux":
            self.run_command(f"sudo python3 traffic_tamer.py -i {interface} -b {rate}")
        else:
            self.run_command(f"python traffic_tamer.py --app-rate {rate}")
    
    def apply_latency(self):
        delay = self.latency_entry.get()
        if not delay:
            return
        interface = self.current_interface.get()
        
        if self.os_type == "Linux":
            self.run_command(f"sudo python3 traffic_tamer.py -i {interface} -d {delay}")
        else:
            self.log("⚠️ Latencia en Windows requiere Clumsy. Usa: python traffic_tamer.py --clumsy-loss 'true' 0.05")
    
    def apply_loss(self):
        loss = self.loss_entry.get()
        interface = self.current_interface.get()
        
        if self.os_type == "Linux":
            self.run_command(f"sudo python3 traffic_tamer.py -i {interface} -l {loss}")
        else:
            self.log(f"⚠️ Pérdida en Windows requiere Clumsy")
    
    def apply_corruption(self):
        corrupt = self.corrupt_entry.get()
        interface = self.current_interface.get()
        
        if self.os_type == "Linux":
            self.run_command(f"sudo python3 traffic_tamer.py -i {interface} --corrupt {corrupt}")
        else:
            self.log(f"⚠️ Corrupción en Windows: python traffic_tamer.py --clumsy-corrupt 'true' {float(corrupt)/100}")
    
    def apply_duplicate(self):
        dup = self.duplicate_entry.get()
        interface = self.current_interface.get()
        
        if self.os_type == "Linux":
            self.run_command(f"sudo python3 traffic_tamer.py -i {interface} --duplicate {dup}")
        else:
            self.log("⚠️ Duplicación solo en Linux")
    
    def apply_reorder(self):
        reorder = self.reorder_entry.get()
        interface = self.current_interface.get()
        
        if self.os_type == "Linux":
            self.run_command(f"sudo python3 traffic_tamer.py -i {interface} --reorder {reorder}")
        else:
            self.log("⚠️ Reordenamiento solo en Linux")
    
    def apply_jitter(self):
        jitter = self.jitter_entry.get()
        interface = self.current_interface.get()
        
        if self.os_type == "Linux":
            self.run_command(f"sudo python3 traffic_tamer.py -i {interface} --jitter {jitter}")
        else:
            self.log("⚠️ Jitter solo en Linux")
    
    def apply_qos_app(self):
        if self.os_type != "Windows":
            self.log("⚠️ QoS por app solo en Windows")
            return
        
        app_path = self.qos_app_path.get()
        rate = self.qos_rate.get()
        dscp = self.qos_dscp.get()
        
        cmd = "python traffic_tamer.py"
        if app_path:
            cmd += f" --app \"{app_path}\""
        if rate:
            cmd += f" --app-rate {rate}"
        if dscp:
            cmd += f" --app-dscp {dscp}"
        
        self.run_command(cmd)
    
    def list_policies(self):
        if self.os_type == "Windows":
            self.run_command("python traffic_tamer.py --list-policies")
        else:
            self.log("ℹ️ En Linux, las reglas se ven con: tc qdisc show")
    
    def clear_policies(self):
        if self.os_type == "Windows":
            self.run_command("python traffic_tamer.py --clear-policies")
        else:
            self.run_command(f"sudo tc qdisc del dev {self.current_interface.get()} root")
    
    def reset_all(self):
        interface = self.current_interface.get()
        if self.os_type == "Linux":
            self.run_command(f"sudo python3 traffic_tamer.py -i {interface} -r")
        else:
            self.run_command("python traffic_tamer.py --clear-policies")
            self.log("✅ Políticas QoS limpiadas")
    
    def show_status(self):
        self.refresh_status()
    
    def refresh_status(self):
        interface = self.current_interface.get()
        if self.os_type == "Linux":
            self.run_command(f"tc qdisc show dev {interface}")
        else:
            self.run_command("netsh int tcp show global")
            self.run_command("python traffic_tamer.py --list-policies")
    
    def start_api(self):
        """Iniciar servidor API en hilo separado"""
        import threading
        port = self.api_port.get()
        
        # Importar y ejecutar el módulo API
        from traffic_tamer_api import run_api_server
        self.api_thread = threading.Thread(target=run_api_server, args=(int(port),), daemon=True)
        self.api_thread.start()
        self.api_status.config(text=f"Ejecutando en puerto {port}", foreground="green")
        self.log(f"🌐 API REST iniciada en http://localhost:{port}")
    
    def stop_api(self):
        """Detener API (por marcador, requiere reinicio)"""
        self.api_status.config(text="Detenida (reinicia app para cambios)", foreground="orange")
        self.log("⚠️ Para detener completamente la API, cierra esta ventana o mata el proceso")

def main():
    root = tk.Tk()
    app = TrafficTamerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
