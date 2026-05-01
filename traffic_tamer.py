#!/usr/bin/env python3
"""
TrafficTamer 2.0 - Control de tráfico profesional en Linux y Windows
Features: Bandwidth limit, latency, packet loss, corruption, QoS por aplicación
"""

import sys
import platform
import subprocess
import argparse
import json
import os
from pathlib import Path

class TrafficTamer:
    def __init__(self):
        self.os_type = platform.system()
        self.check_admin()
        
    def check_admin(self):
        """Verificar permisos de administrador/root"""
        if self.os_type == "Windows":
            try:
                import ctypes
                if not ctypes.windll.shell32.IsUserAnAdmin():
                    print("[!] Ejecuta como Administrador en Windows")
                    print("[*] Haz right-click -> Run as Administrator")
                    sys.exit(1)
            except:
                pass
        else:
            if subprocess.run(["id", "-u"], capture_output=True, text=True).stdout.strip() != "0":
                print("[!] Usa sudo en Linux")
                sys.exit(1)
    
    # ============ WINDOWS QOS POLICIES (POR APLICACIÓN) ============
    def windows_qos_by_app(self, app_path, rate_mbps=None, dscp_value=None):
        """
        Crea política QoS para una aplicación específica en Windows
        - rate_mbps: límite de ancho de banda
        - dscp_value: prioridad (0-63, valores altos = más prioridad)
        """
        policy_name = f"TrafficTamer_{Path(app_path).stem}"
        
        if rate_mbps:
            # ThrottleRateAction en bits por segundo
            bits_per_sec = rate_mbps * 1_000_000
            cmd = [
                "powershell", "-Command",
                f"New-NetQosPolicy -Name '{policy_name}' "
                f"-AppPathNameMatchCondition '{app_path}' "
                f"-ThrottleRateActionBitsPerSecond {bits_per_sec}"
            ]
            subprocess.run(cmd, capture_output=True)
            print(f"[+] App '{app_path}' limitada a {rate_mbps} Mbps")
            
        if dscp_value:
            cmd = [
                "powershell", "-Command",
                f"New-NetQosPolicy -Name '{policy_name}_DSCP' "
                f"-AppPathNameMatchCondition '{app_path}' "
                f"-DSCPAction {dscp_value}"
            ]
            subprocess.run(cmd, capture_output=True)
            print(f"[+] App '{app_path}' tiene prioridad DSCP {dscp_value}")
    
    def windows_qos_by_port(self, port, rate_mbps=None, dscp_value=None):
        """Política QoS por puerto TCP/UDP"""
        policy_name = f"TrafficTamer_Port{port}"
        
        if rate_mbps:
            bits_per_sec = rate_mbps * 1_000_000
            cmd = [
                "powershell", "-Command",
                f"New-NetQosPolicy -Name '{policy_name}' "
                f"-IPPortMatchCondition {port} "
                f"-ThrottleRateActionBitsPerSecond {bits_per_sec}"
            ]
            subprocess.run(cmd, capture_output=True)
            print(f"[+] Puerto {port} limitado a {rate_mbps} Mbps")
            
        if dscp_value:
            cmd = [
                "powershell", "-Command",
                f"New-NetQosPolicy -Name '{policy_name}_DSCP' "
                f"-IPPortMatchCondition {port} "
                f"-DSCPAction {dscp_value}"
            ]
            subprocess.run(cmd, capture_output=True)
            print(f"[+] Puerto {port} tiene prioridad DSCP {dscp_value}")
    
    def windows_qos_by_ip(self, ip, rate_mbps=None, dscp_value=None):
        """Política QoS por IP destino"""
        policy_name = f"TrafficTamer_IP_{ip.replace('.', '_')}"
        
        if rate_mbps:
            bits_per_sec = rate_mbps * 1_000_000
            cmd = [
                "powershell", "-Command",
                f"New-NetQosPolicy -Name '{policy_name}' "
                f"-IPDstPrefixMatchCondition '{ip}/32' "
                f"-ThrottleRateActionBitsPerSecond {bits_per_sec}"
            ]
            subprocess.run(cmd, capture_output=True)
            print(f"[+] IP {ip} limitada a {rate_mbps} Mbps")
    
    def windows_list_policies(self):
        """Listar todas las políticas QoS activas"""
        cmd = ["powershell", "-Command", "Get-NetQosPolicy | Select-Object Name, AppPathName, ThrottleRate, DSCPAction"]
        subprocess.run(cmd)
    
    def windows_clear_policies(self):
        """Eliminar todas las políticas QoS de TrafficTamer"""
        cmd = ["powershell", "-Command", "Get-NetQosPolicy | Where-Object {$_.Name -like 'TrafficTamer*'} | Remove-NetQosPolicy"]
        subprocess.run(cmd)
        print("[+] Todas las políticas QoS de TrafficTamer eliminadas")
    
    # ============ WINDOWS TCP OPTIMIZATIONS ============
    def windows_tcp_autotuning(self, level="disabled"):
        """
        Ajustar autotuning de TCP en Windows
        levels: disabled, highlyrestricted, restricted, normal, experimental
        """
        valid_levels = ["disabled", "highlyrestricted", "restricted", "normal", "experimental"]
        if level.lower() not in valid_levels:
            print(f"[!] Nivel inválido. Usa: {valid_levels}")
            return
        
        cmd = f"netsh int tcp set global autotuninglevel={level.lower()}"
        subprocess.run(cmd, shell=True)
        print(f"[+] TCP Auto-Tuning level cambiado a: {level}")
        
        # Mostrar estado actual
        subprocess.run("netsh int tcp show global", shell=True)
    
    def windows_tcp_rss(self, enable=True):
        """Habilitar/deshabilitar Receive Side Scaling"""
        state = "enabled" if enable else "disabled"
        cmd = f"netsh int tcp set global rss={state}"
        subprocess.run(cmd, shell=True)
        print(f"[+] TCP RSS {state}")
    
    # ============ WINDOWS BANDWIDTH (Delivery Optimization) ============
    def windows_update_bandwidth(self, background_mbps=None, foreground_mbps=None):
        """
        Limitar ancho de banda de Windows Updates [citation:4]
        """
        if background_mbps:
            # Convertir Mbps a kilobytes/segundo
            kb_s = background_mbps * 125
            cmd = [
                "powershell", "-Command",
                f"New-Item -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DeliveryOptimization' -Force | Out-Null; "
                f"Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DeliveryOptimization' -Name 'DOMaxBackgroundDownloadBandwidth' -Value {kb_s}"
            ]
            subprocess.run(cmd, shell=True)
            print(f"[+] Windows Updates background limit: {background_mbps} Mbps")
        
        if foreground_mbps:
            kb_s = foreground_mbps * 125
            cmd = [
                "powershell", "-Command",
                f"Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DeliveryOptimization' -Name 'DOMaxForegroundDownloadBandwidth' -Value {kb_s}"
            ]
            subprocess.run(cmd, shell=True)
            print(f"[+] Windows Updates foreground limit: {foreground_mbps} Mbps")
    
    # ============ INTEGRACIÓN CON CLUMSY / FUMBLE ============
    def install_clumsy(self):
        """Instalar Clumsy/Fumble para features avanzadas [citation:3][citation:10]"""
        print("[*] Para corrupción de paquetes, necesitas Clumsy o Fumble")
        print("[*] Descarga Clumsy: https://github.com/jagt/clumsy/releases")
        print("[*] O Fumble (Rust rewrite): https://github.com/bornacvitanic/fumble")
        print("[*] Una vez instalado, úsalo con:")
        print('    clumsy --filter "tcp.DstPort == 80" --drop 0.1 --delay 100')
    
    def windows_clumsy_corruption(self, filter_expr, corruption_percent):
        """
        Simular corrupción de paquetes con Clumsy
        clumsy --filter "tcp.DstPort == 80" --corrupt 0.05
        """
        cmd = f'clumsy --filter "{filter_expr}" --corrupt {corruption_percent}'
        print(f"[*] Ejecuta en otra terminal: {cmd}")
        print(f"[!] La corrupción de paquetes simula datos corruptos en transmisión [citation:3]")
    
    def windows_clumsy_loss(self, filter_expr, loss_percent):
        """Pérdida de paquetes con Clumsy"""
        cmd = f'clumsy --filter "{filter_expr}" --drop {loss_percent}'
        print(f"[*] Ejecuta: {cmd}")
    
    # ============ LINUX TC (COMPLETO) ============
    def linux_tc_corruption(self, interface, corrupt_percent):
        """Corrupción de paquetes en Linux"""
        cmd = f"tc qdisc add dev {interface} root netem corrupt {corrupt_percent}%"
        subprocess.run(cmd.split())
        print(f"[+] {corrupt_percent}% de paquetes corruptos en {interface}")
    
    def linux_tc_duplicate(self, interface, dup_percent):
        """Duplicación de paquetes (muy útil para testing)"""
        cmd = f"tc qdisc add dev {interface} root netem duplicate {dup_percent}%"
        subprocess.run(cmd.split())
        print(f"[+] {dup_percent}% de paquetes duplicados en {interface}")
    
    def linux_tc_reorder(self, interface, delay_ms, reorder_percent):
        """Reordenamiento de paquetes"""
        cmd = f"tc qdisc add dev {interface} root netem delay {delay_ms}ms reorder {reorder_percent}% 50%"
        subprocess.run(cmd.split())
        print(f"[+] Paquetes reordenados en {interface} con {reorder_percent}% probabilidad")
    
    def linux_tc_jitter(self, interface, base_delay_ms, jitter_ms):
        """Jitter (variación de latencia)"""
        cmd = f"tc qdisc add dev {interface} root netem delay {base_delay_ms}ms {jitter_ms}ms distribution normal"
        subprocess.run(cmd.split())
        print(f"[+] Jitter de {jitter_ms}ms sobre {base_delay_ms}ms base")
    
    def linux_tc_rate_limit(self, interface, rate_mbps, burst_kb=32):
        """Rate limiting avanzado con burst"""
        commands = [
            f"tc qdisc add dev {interface} root handle 1: htb default 30",
            f"tc class add dev {interface} parent 1: classid 1:1 htb rate {rate_mbps}mbit burst {burst_kb}k",
            f"tc class add dev {interface} parent 1:1 classid 1:30 htb rate {rate_mbps}mbit"
        ]
        for cmd in commands:
            subprocess.run(cmd.split(), stderr=subprocess.DEVNULL)
        print(f"[+] Rate limit {rate_mbps} Mbps en {interface}")

def main():
    parser = argparse.ArgumentParser(
        description="TrafficTamer 2.0 - Control total de tráfico de red",
        epilog="""
Ejemplos:
  Linux:  sudo python3 traffic_tamer.py -i eth0 --bandwidth 10 --delay 100 --corrupt 5
  Windows QoS: python traffic_tamer.py --app "C:\\Program Files\\Firefox\\firefox.exe" --app-rate 5
  Windows Update: python traffic_tamer.py --update-bg 10 --update-fg 50
  Windows TCP: python traffic_tamer.py --tcp-autotuning disabled
  Clumsy: python traffic_tamer.py --clumsy-loss "tcp.DstPort == 443" 0.1
        """
    )
    
    # Interface (Linux obligatorio)
    parser.add_argument("-i", "--interface", help="Interfaz de red (Linux obligatorio)")
    
    # Linux netem features
    parser.add_argument("-b", "--bandwidth", type=int, help="Limitar ancho de banda (Mbps)")
    parser.add_argument("-d", "--delay", type=int, help="Añadir latencia (ms)")
    parser.add_argument("-l", "--loss", type=int, help="Añadir pérdida de paquetes (%)")
    parser.add_argument("-c", "--corrupt", type=int, help="Añadir corrupción de paquetes (%)")
    parser.add_argument("-dup", "--duplicate", type=int, help="Añadir duplicación de paquetes (%)")
    parser.add_argument("-j", "--jitter", type=int, help="Añadir jitter (ms, requiere --delay)")
    parser.add_argument("--reorder", type=int, help="Reordenar paquetes (% probabilidad)")
    parser.add_argument("-r", "--reset", action="store_true", help="Resetear todas las reglas")
    parser.add_argument("-s", "--status", action="store_true", help="Mostrar estado actual")
    
    # Windows QoS por aplicación
    parser.add_argument("--app", help="Ruta del ejecutable para QoS en Windows")
    parser.add_argument("--app-rate", type=int, help="Limitar app a X Mbps")
    parser.add_argument("--app-dscp", type=int, choices=range(0, 64), help="Prioridad DSCP para app (0-63)")
    
    # Windows QoS por puerto/IP
    parser.add_argument("--port", type=int, help="Puerto para limitar")
    parser.add_argument("--port-rate", type=int, help="Limitar puerto a X Mbps")
    parser.add_argument("--ip", help="IP destino para limitar")
    parser.add_argument("--ip-rate", type=int, help="Limitar IP a X Mbps")
    
    # Windows TCP optimizations
    parser.add_argument("--tcp-autotuning", choices=["disabled", "highlyrestricted", "restricted", "normal", "experimental"],
                        help="Ajustar TCP autotuning level [citation:1]")
    parser.add_argument("--tcp-rss", choices=["enable", "disable"], help="Habilitar/deshabilitar RSS")
    
    # Windows Update bandwidth
    parser.add_argument("--update-bg", type=int, help="Limitar Windows Updates background (Mbps)")
    parser.add_argument("--update-fg", type=int, help="Limitar Windows Updates foreground (Mbps)")
    
    # Clumsy integration
    parser.add_argument("--clumsy-loss", nargs=2, metavar=('FILTER', 'PERCENT'), help="Pérdida con Clumsy")
    parser.add_argument("--clumsy-corrupt", nargs=2, metavar=('FILTER', 'PERCENT'), help="Corrupción con Clumsy")
    
    # Utils
    parser.add_argument("--list-policies", action="store_true", help="Listar políticas QoS de Windows")
    parser.add_argument("--clear-policies", action="store_true", help="Limpiar políticas QoS")
    parser.add_argument("--install-clumsy", action="store_true", help="Mostrar cómo instalar Clumsy")
    
    args = parser.parse_args()
    tamer = TrafficTamer()
    os_type = platform.system()
    
    # ===== LINUX =====
    if os_type == "Linux":
        if not args.interface:
            print("[!] En Linux es obligatorio -i/--interface")
            return
        
        if args.reset:
            subprocess.run(f"tc qdisc del dev {args.interface} root".split(), stderr=subprocess.DEVNULL)
            print(f"[+] Reset en {args.interface}")
        elif args.status:
            subprocess.run(f"tc qdisc show dev {args.interface}", shell=True)
        elif args.bandwidth:
            tamer.linux_tc_rate_limit(args.interface, args.bandwidth)
        elif args.delay:
            tamer.add_latency(args.interface, args.delay)
        elif args.loss:
            tamer.add_packet_loss(args.interface, args.loss)
        elif args.corrupt:
            tamer.linux_tc_corruption(args.interface, args.corrupt)
        elif args.duplicate:
            tamer.linux_tc_duplicate(args.interface, args.duplicate)
        elif args.reorder:
            delay = args.delay if args.delay else 10
            tamer.linux_tc_reorder(args.interface, delay, args.reorder)
        else:
            parser.print_help()
    
    # ===== WINDOWS =====
    elif os_type == "Windows":
        # QoS por aplicación
        if args.app and (args.app_rate or args.app_dscp):
            tamer.windows_qos_by_app(args.app, args.app_rate, args.app_dscp)
        
        # QoS por puerto
        elif args.port and (args.port_rate or args.app_dscp):
            tamer.windows_qos_by_port(args.port, args.port_rate, args.app_dscp)
        
        # QoS por IP
        elif args.ip and args.ip_rate:
            tamer.windows_qos_by_ip(args.ip, args.ip_rate)
        
        # TCP optimizations
        elif args.tcp_autotuning:
            tamer.windows_tcp_autotuning(args.tcp_autotuning)
        elif args.tcp_rss:
            tamer.windows_tcp_rss(args.tcp_rss == "enable")
        
        # Windows Updates
        elif args.update_bg or args.update_fg:
            tamer.windows_update_bandwidth(args.update_bg, args.update_fg)
        
        # Listar/limpiar políticas
        elif args.list_policies:
            tamer.windows_list_policies()
        elif args.clear_policies:
            tamer.windows_clear_policies()
        
        # Clumsy
        elif args.install_clumsy:
            tamer.install_clumsy()
        elif args.clumsy_loss:
            tamer.windows_clumsy_loss(args.clumsy_loss[0], float(args.clumsy_loss[1]))
        elif args.clumsy_corrupt:
            tamer.windows_clumsy_corruption(args.clumsy_corrupt[0], float(args.clumsy_corrupt[1]))
        
        # Reset y status en Windows (simplificado)
        elif args.reset:
            print("[*] Para resetear en Windows:")
            print("    - Las políticas QoS se borran con --clear-policies")
            print("    - Cierra Clumsy si está corriendo")
            print("    - Los cambios de TCP revierte con --tcp-autotuning normal")
        elif args.status:
            print("\n=== Políticas QoS activas ===")
            tamer.windows_list_policies()
            print("\n=== TCP Global Settings ===")
            subprocess.run("netsh int tcp show global", shell=True)
        else:
            parser.print_help()
    
    else:
        print(f"[!] OS no soportado: {os_type}")

if __name__ == "__main__":
    main()
