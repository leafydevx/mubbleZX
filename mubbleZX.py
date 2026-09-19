import tkinter as tk
import math
import subprocess
import threading
import re

class mubbleZX:
    def __init__(self, root):
        self.root = root
        self.root.title("mubbleZX - Radar Scanner v4.0 PORT SCAN")
        self.root.geometry("950x950")
        self.root.configure(bg="black")
        
        self.canvas = tk.Canvas(root, bg="black", width=950, height=950, highlightthickness=0)
        self.canvas.pack()
        
        self.center_x, self.center_y = 475, 475
        self.pulse_radius = 0
        self.devices = []
        self.scanning = False
        self.port_scanning = False
        self.scan_status = "READY - HOLD SPACE TO SCAN"
        self.target_network = "192.168.1.0/24"
        self.space_pressed = False
        
        self.draw_static()
        self.animate_pulse()
        self.update_scanned_devices()
        
        self.root.bind("<KeyPress-space>", self.on_space_press)
        self.root.bind("<KeyRelease-space>", self.on_space_release)
    
    def on_space_press(self, event):
        """When SPACE is pressed"""
        if not self.space_pressed and not self.scanning:
            self.space_pressed = True
            print("\n[!] SPACE PRESSED - Starting network scan...")
            self.scan_status = "SCANNING NETWORK (HOLD SPACE)..."
            
            scan_thread = threading.Thread(target=self.run_nmap_scan, args=(self.target_network,))
            scan_thread.daemon = True
            scan_thread.start()
    
    def on_space_release(self, event):
        """When SPACE is released"""
        self.space_pressed = False
    
    def run_nmap_scan(self, target):
        """Network discovery scan"""
        self.scanning = True
        self.devices = []
        
        try:
            print(f"[*] Running: sudo nmap -sn {target}")
            
            cmd = f"sudo nmap -sn {target}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            
            print("[*] NMAP OUTPUT:")
            print(result.stdout)
            
            # Parse network devices
            self.parse_nmap_output(result.stdout)
            
            print(f"\n[+] Found {len(self.devices)} devices!")
            print("[*] Starting port scan on all devices...")
            self.scan_status = f"FOUND {len(self.devices)} DEVICES - PORT SCANNING..."
            
            # Now scan ports on each device
            self.scan_ports_on_devices()
            
            self.scan_status = f"COMPLETE - {len(self.devices)} devices with port info"
            
        except Exception as e:
            print(f"[-] Error: {e}")
            self.scan_status = f"ERROR: {str(e)}"
        
        self.scanning = False
    
    def parse_nmap_output(self, nmap_output):
        """Parse network discovery results"""
        print("\n[*] Parsing network devices...")
        
        lines = nmap_output.split('\n')
        
        for line in lines:
            if 'Nmap scan report for' in line:
                print(f"[DEBUG] {line}")
                
                ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', line)
                if ip_match:
                    ip = ip_match.group()
                    
                    hostname = "Unknown"
                    if '(' in line:
                        hostname = line.split('(')[-1].split(')')[0]
                    
                    angle = math.radians(len(self.devices) * 30)
                    distance = 100 + (len(self.devices) % 3) * 80
                    x = self.center_x + distance * math.cos(angle)
                    y = self.center_y + distance * math.sin(angle)
                    
                    last_octet = int(ip.split('.')[-1])
                    if last_octet == 1 or last_octet == 254:
                        device_type = 'ROUTER'
                        color = 'lime'
                    else:
                        device_type = 'DEVICE'
                        color = 'yellow'
                    
                    device = {
                        'x': x,
                        'y': y,
                        'ip': ip,
                        'hostname': hostname,
                        'device_type': device_type,
                        'scanned': False,
                        'color': color,
                        'open_ports': []
                    }
                    
                    self.devices.append(device)
                    print(f"[+] {ip} - {hostname} ({device_type})")
    
    def scan_ports_on_devices(self):
        """Scan ports on each discovered device"""
        self.port_scanning = True
        
        for i, device in enumerate(self.devices):
            print(f"\n[*] Port scanning {i+1}/{len(self.devices)}: {device['ip']}")
            self.scan_status = f"PORT SCANNING: {device['ip']} ({i+1}/{len(self.devices)})"
            
            try:
                # Scan common ports (faster than all 65535)
                cmd = f"sudo nmap -p 21,22,80,443,3306,5432,8080,8443 {device['ip']}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                
                # Parse open ports
                self.parse_port_results(device, result.stdout)
                
            except Exception as e:
                print(f"[-] Port scan error: {e}")
        
        self.port_scanning = False
        print("\n[+] Port scanning complete!")
    
    def parse_port_results(self, device, nmap_output):
        """Extract open ports from nmap output"""
        lines = nmap_output.split('\n')
        
        for line in lines:
            # Look for lines like "80/tcp   open  http"
            if 'open' in line:
                parts = line.split()
                if len(parts) >= 2:
                    port_info = parts[0]  # e.g., "80/tcp"
                    
                    if '/' in port_info:
                        port = port_info.split('/')[0]
                        
                        # Get service name if available
                        service = "unknown"
                        if len(parts) >= 3:
                            service = parts[2]
                        
                        device['open_ports'].append({
                            'port': port,
                            'service': service
                        })
                        
                        print(f"    [+] Open port: {port} ({service})")
    
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
        
        self.canvas.create_text(475, 40, text="mubbleZX RADAR v4.0", fill="cyan", font=("Arial", 18, "bold"))
        self.canvas.create_text(475, 920, text="HOLD SPACE TO SCAN NETWORK + PORTS", fill="lime", font=("Arial", 11, "bold"), tags="status")
    
    def draw_devices(self):
        """Draw devices with port info"""
        self.canvas.delete("device", "info")
        
        for device in self.devices:
            x, y = device['x'], device['y']
            
            # Change color if ports found
            if device['open_ports']:
                dot_color = 'red'  # Red if services found
            else:
                dot_color = device['color']
            
            # Device dot
            self.canvas.create_oval(
                x - 8, y - 8,
                x + 8, y + 8,
                fill=dot_color,
                outline="white",
                width=2,
                tags="device"
            )
            
            # Device info
            if device['scanned']:
                # IP
                self.canvas.create_text(
                    x + 20, y - 15,
                    text=f"IP: {device['ip']}",
                    fill=dot_color,
                    font=("Arial", 7, "bold"),
                    tags="info",
                    anchor="w"
                )
                
                # Type
                self.canvas.create_text(
                    x + 20, y - 5,
                    text=f"{device['device_type']}",
                    fill=dot_color,
                    font=("Arial", 7),
                    tags="info",
                    anchor="w"
                )
                
                # Open ports
                if device['open_ports']:
                    ports_str = ", ".join([p['port'] for p in device['open_ports']])
                    self.canvas.create_text(
                        x + 20, y + 5,
                        text=f"Ports: {ports_str}",
                        fill="red",
                        font=("Arial", 7, "bold"),
                        tags="info",
                        anchor="w"
                    )
    
    def animate_pulse(self):
        """Pulse animation"""
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
        for device in self.devices:
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

if __name__
