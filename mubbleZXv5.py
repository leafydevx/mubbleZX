#!/usr/bin/env python3
import tkinter as tk
import math
import subprocess
import threading
import re
import json
from datetime import datetime

class mubbleZX:
    def __init__(self, root):
        self.root = root
        self.root.title("mubbleZX - Radar Scanner v5.0 ULTIMATE")
        self.root.geometry("950x950")
        self.root.configure(bg="black")
        
        self.canvas = tk.Canvas(root, bg="black", width=950, height=950, highlightthickness=0)
        self.canvas.pack()
        
        self.center_x, self.center_y = 475, 475
        self.pulse_radius = 0
        self.devices = []
        self.scanning = False
        self.scan_status = "READY - HOLD SPACE TO SCAN"
        self.target_network = "192.168.1.0/24"
        self.space_pressed = False
        
        self.draw_static()
        self.animate_pulse()
        self.update_scanned_devices()
        
        self.root.bind("<KeyPress-space>", self.on_space_press)
        self.root.bind("<KeyRelease-space>", self.on_space_release)
    
    def on_space_press(self, event):
        if not self.space_pressed and not self.scanning:
            self.space_pressed = True
            print("\n[!] SPACE PRESSED - Starting full network scan...")
            self.scan_status = "SCANNING NETWORK (HOLD SPACE)..."
            
            scan_thread = threading.Thread(target=self.run_full_scan, args=(self.target_network,))
            scan_thread.daemon = True
            scan_thread.start()
    
    def on_space_release(self, event):
        self.space_pressed = False
    
    def run_full_scan(self, network_range):
        """Full scan: ping + detail + ports"""
        self.scanning = True
        self.devices = []
        
        try:
            print(f"[*] Running ping scan on {network_range}")
            ping_output = subprocess.run(
                ["sudo", "nmap", "-sn", network_range],
                capture_output=True, text=True, timeout=60
            ).stdout
            
            devices = self.parse_ping_scan(ping_output)
            print(f"[+] Found {len(devices)} devices!")
            self.scan_status = f"FOUND {len(devices)} DEVICES - DETAIL SCANNING..."
            
            for i, device in enumerate(devices):
                print(f"\n[*] Scanning {device['ip']} ({i+1}/{len(devices)})")
                self.scan_status = f"DETAIL SCAN: {device['ip']} ({i+1}/{len(devices)})"
                
                detail_output = subprocess.run(
                    ["sudo", "nmap", "-sV", device['ip']],
                    capture_output=True, text=True, timeout=30
                ).stdout
                
                detail_info = self.parse_detail_scan(detail_output)
                device.update(detail_info)
                self.devices.append(device)
            
            self.save_results_json()
            self.scan_status = f"COMPLETE - {len(self.devices)} devices scanned"
            
        except Exception as e:
            print(f"[-] Error: {e}")
            self.scan_status = f"ERROR: {str(e)}"
        
        self.scanning = False
    
    def parse_ping_scan(self, output):
        """Parse ping scan for IPs and MAC addresses"""
        devices = []
        lines = output.splitlines()
        
        for i, line in enumerate(lines):
            if 'Nmap scan report for' in line:
                ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', line)
                if ip_match:
                    ip = ip_match.group()
                    
                    mac = None
                    vendor = None
                    
                    for j in range(i+1, min(i+5, len(lines))):
                        if 'MAC Address:' in lines[j]:
                            mac_match = re.search(r'MAC Address:\s+([0-9A-Fa-f:]+)\s+\((.+?)\)', lines[j])
                            if mac_match:
                                mac = mac_match.group(1)
                                vendor = mac_match.group(2)
                            break
                    
                    device = {
                        'ip': ip,
                        'mac': mac,
                        'vendor': vendor,
                        'hostname': ip,
                        'device_type': 'ROUTER' if ip.endswith('.1') or ip.endswith('.254') else 'DEVICE',
                        'ports': [],
                        'open_ports': [],
                        'scanned': False,
                        'color': 'lime' if ip.endswith('.1') or ip.endswith('.254') else 'yellow',
                        'x': 0,
                        'y': 0
                    }
                    devices.append(device)
                    print(f"[+] {ip} - {vendor}")
        
        return devices
    
    def parse_detail_scan(self, output):
        """Parse detailed nmap scan"""
        ports = []
        lines = output.splitlines()
        
        in_port_section = False
        for line in lines:
            if line.strip().startswith("PORT"):
                in_port_section = True
                continue
            if in_port_section:
                if not line.strip():
                    break
                match = re.match(r'^(\d+)/tcp\s+(\w+)\s+([\w\-\?]+)\s*(.*)$', line.strip())
                if match:
                    port = match.group(1)
                    state = match.group(2)
                    service = match.group(3)
                    extra = match.group(4).strip()
                    
                    if state == 'open':
                        ports.append({
                            'port': port,
                            'service': service,
                            'extra': extra
                        })
                        print(f"    [+] Port {port}: {service}")
        
        return {
            'ports': ports,
            'open_ports': ports
        }
    
    def save_results_json(self):
        """Save scan results to JSON"""
        timestamp = datetime.now().isoformat()
        results = {
            'scan_time': timestamp,
            'network': self.target_network,
            'devices': self.devices
        }
        
        filename = f"mubbleZX_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"[+] Saved results to {filename}")
            self.scan_status += f" | Saved to {filename}"
        except Exception as e:
            print(f"[-] Failed to save JSON: {e}")
    
    def draw_static(self):
        """Draw radar UI"""
        for i in range(1, 7):
            radius = i * 70
            self.canvas.create_oval(
                self.center_x - radius,
                self.center_y - radius,
                self.center_x + radius,
                self.center_y + radius,
                outline="lime",
                width=1.5
            )
        
        self.canvas.create_oval(
            self.center_x - 10,
            self.center_y - 10,
            self.center_x + 10,
            self.center_y + 10,
            fill="red",
            outline="yellow",
            width=2
        )
        
        self.canvas.create_line(self.center_x, 0, self.center_x, 950, fill="lime", dash=(5, 5), width=1)
        self.canvas.create_line(0, self.center_y, 950, self.center_y, fill="lime", dash=(5, 5), width=1)
        
        self.canvas.create_text(475, 40, text="mubbleZX RADAR v5.0", fill="cyan", font=("Arial", 18, "bold"))
        self.canvas.create_text(475, 920, text="HOLD SPACE TO SCAN | Results saved to JSON", fill="lime", font=("Arial", 10, "bold"), tags="status")
    
    def draw_devices(self):
        """Draw devices on radar"""
        self.canvas.delete("device", "info")
        
        for device in self.devices:
            x, y = device['x'], device['y']
            
            if device['open_ports']:
                dot_color = 'red'
            else:
                dot_color = device['color']
            
            self.canvas.create_oval(
                x - 8, y - 8,
                x + 8, y + 8,
                fill=dot_color,
                outline="white",
                width=2,
                tags="device"
            )
            
            if device['scanned']:
                display_name = device['vendor'] if device['vendor'] else "Unknown"
                self.canvas.create_text(
                    x + 20, y - 15,
                    text=display_name,
                    fill=dot_color,
                    font=("Arial", 8, "bold"),
                    tags="info",
                    anchor="w"
                )
                
                self.canvas.create_text(
                    x + 20, y - 3,
                    text=f"{device['ip']}",
                    fill=dot_color,
                    font=("Arial", 7),
                    tags="info",
                    anchor="w"
                )
                
                if device['open_ports']:
                    ports_str = ", ".join([p['port'] for p in device['open_ports']])
                    self.canvas.create_text(
                        x + 20, y + 8,
                        text=f"Ports: {ports_str}",
                        fill="red",
                        font=("Arial", 7, "bold"),
                        tags="info",
                        anchor="w"
                    )
    
    def animate_pulse(self):
        """Visual beep animation"""
        self.canvas.delete("pulse")
        
        if self.pulse_radius < 30:
            self.pulse_radius += 1
        else:
            self.pulse_radius = 0
        
        if self.pulse_radius > 0:
            self.canvas.create_oval(
                self.center_x - self.pulse_radius,
                self.center_y - self.pulse_radius,
                self.center_x + self.pulse_radius,
                self.center_y + self.pulse_radius,
                outline="cyan",
                width=2,
                tags="pulse"
            )
        
        self.draw_devices()
        self.root.after(30, self.animate_pulse)
    
    def update_scanned_devices(self):
        """Mark devices as scanned"""
        for i, device in enumerate(self.devices):
            if device['x'] == 0 and device['y'] == 0:
                angle = math.radians(i * 30)
                distance = 100 + (i % 3) * 80
                device['x'] = self.center_x + distance * math.cos(angle)
                device['y'] = self.center_y + distance * math.sin(angle)
            
            dist = math.sqrt((device['x'] - self.center_x)**2 + (device['y'] - self.center_y)**2)
            if abs(dist - self.pulse_radius) < 15:
                device['scanned'] = True
        
        self.canvas.delete("status")
        self.canvas.create_text(
            475, 920,
            text=self.scan_status,
            fill="lime",
            font=("Arial", 10),
            tags="status"
        )
        
        self.root.after(100, self.update_scanned_devices)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  mubbleZX NETWORK RADAR v5.0 ULTIMATE")
    print("  NETWORK DISCOVERY + PORT SCANNING + JSON EXPORT")
    print("="*60)
    print("\n[!] HOME NETWORK ONLY - USE ETHICALLY\n")
    
    root = tk.Tk()
    app = mubbleZX(root)
    root.mainloop()
