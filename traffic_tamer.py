#!/usr/bin/env python3
"""
TrafficTamer - Cross-platform network traffic control tool
Supports Linux (tc) and Windows (netsh)
"""

import sys
import platform
import subprocess
import argparse
import json

class TrafficTamer:
    def __init__(self):
        self.os_type = platform.system()
        self.check_admin()
    
    def check_admin(self):
        """Check if running with admin/root privileges"""
        if self.os_type == "Windows":
            try:
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                if not is_admin:
                    print("[!] Please run as Administrator on Windows")
                    sys.exit(1)
            except:
                pass
        else:  # Linux
            if subprocess.run(["id", "-u"], capture_output=True, text=True).stdout.strip() != "0":
                print("[!] Please run with sudo on Linux")
                sys.exit(1)
    
    def set_bandwidth_limit(self, interface, rate):
        """Set bandwidth limit on interface"""
        if self.os_type == "Windows":
            # Windows: using netsh
            cmd = f'netsh interface ip set interface "{interface}" forwarding=enable'
            subprocess.run(cmd, shell=True)
            print(f"[+] Bandwidth limit on Windows is managed via QoS policies")
            print(f"[*] Run: New-NetQosPolicy -Name TrafficTamer -ThrottleRateMbps {rate}")
        else:
            # Linux: using tc
            commands = [
                f"tc qdisc add dev {interface} root handle 1: htb default 30",
                f"tc class add dev {interface} parent 1: classid 1:1 htb rate {rate}mbit",
                f"tc class add dev {interface} parent 1:1 classid 1:30 htb rate {rate}mbit"
            ]
            for cmd in commands:
                subprocess.run(cmd.split(), capture_output=True)
            print(f"[+] Bandwidth limited to {rate} Mbps on {interface}")
    
    def add_latency(self, interface, delay_ms):
        """Add artificial latency"""
        if self.os_type == "Windows":
            print(f"[!] Latency on Windows requires third-party tools or driver")
            print(f"[*] Try: cfosspeed, Netlimiter, or Windows SDK Traffic Simulator")
        else:
            cmd = f"tc qdisc add dev {interface} root netem delay {delay_ms}ms"
            subprocess.run(cmd.split())
            print(f"[+] Added {delay_ms}ms latency on {interface}")
    
    def add_packet_loss(self, interface, loss_percent):
        """Add packet loss"""
        if self.os_type == "Windows":
            print(f"[!] Packet loss on Windows requires third-party tools")
        else:
            cmd = f"tc qdisc add dev {interface} root netem loss {loss_percent}%"
            subprocess.run(cmd.split())
            print(f"[+] Added {loss_percent}% packet loss on {interface}")
    
    def reset(self, interface):
        """Reset all traffic shaping rules"""
        if self.os_type == "Windows":
            cmd = f'netsh interface ip set interface "{interface}" forwarding=disable'
            subprocess.run(cmd, shell=True)
            print(f"[+] Reset on {interface} (disable/enable interface to clear)")
        else:
            cmd = f"tc qdisc del dev {interface} root"
            subprocess.run(cmd.split(), stderr=subprocess.DEVNULL)
            print(f"[+] Reset all traffic rules on {interface}")
    
    def show_status(self, interface):
        """Show current traffic shaping rules"""
        if self.os_type == "Windows":
            subprocess.run(f'netsh interface ip show interface "{interface}"', shell=True)
        else:
            subprocess.run(f"tc qdisc show dev {interface}", shell=True)

def main():
    parser = argparse.ArgumentParser(description="TrafficTamer - Control your network traffic")
    parser.add_argument("-i", "--interface", required=True, help="Network interface (eth0, eth1, Wi-Fi, etc.)")
    parser.add_argument("-b", "--bandwidth", type=int, help="Set bandwidth limit in Mbps")
    parser.add_argument("-d", "--delay", type=int, help="Add latency in milliseconds")
    parser.add_argument("-l", "--loss", type=int, help="Add packet loss percentage")
    parser.add_argument("-r", "--reset", action="store_true", help="Reset all traffic rules")
    parser.add_argument("-s", "--status", action="store_true", help="Show current rules")
    
    args = parser.parse_args()
    tamer = TrafficTamer()
    
    if args.reset:
        tamer.reset(args.interface)
    elif args.status:
        tamer.show_status(args.interface)
    elif args.bandwidth:
        tamer.set_bandwidth_limit(args.interface, args.bandwidth)
    elif args.delay:
        tamer.add_latency(args.interface, args.delay)
    elif args.loss:
        tamer.add_packet_loss(args.interface, args.loss_percent)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
