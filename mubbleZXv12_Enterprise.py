#!/usr/bin/env python3
"""mubbleZX v12 - Enterprise Network Reconnaissance Framework"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import subprocess
import threading
import re
import json
import sqlite3
import csv
from datetime import datetime

# DATABASE
class MubbleDatabase:
    def __init__(self, db_path="mubbleZX_scans.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY,
                scan_id TEXT UNIQUE,
                network TEXT,
                timestamp DATETIME,
                device_count INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY,
                scan_id TEXT,
                ip TEXT,
                mac TEXT,
                vendor TEXT,
                hostname TEXT,
                device_type TEXT,
                risk_level TEXT,
                open_ports TEXT,
                FOREIGN KEY(scan_id) REFERENCES scans(scan_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_scan(self, scan_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        scan_id = scan_data['scan_id']
        network = scan_data['network']
        timestamp = datetime.now()
        device_count = len(scan_data['devices'])
        
        cursor.execute('''
            INSERT OR REPLACE INTO scans 
            (scan_id, network, timestamp, device_count)
            VALUES (?, ?, ?, ?)
        ''', (scan_id, network, timestamp, device_count))
        
        for device in scan_data['devices']:
            cursor.execute('''
                INSERT INTO devices 
                (scan_id, ip, mac, vendor, hostname, device_type, risk_level, open_ports)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scan_id,
                device['ip'],
                device.get('mac'),
                device.get('vendor'),
                device.get('hostname'),
                device.get('device_type'),
                device.get('risk_level'),
                json.dumps(device.get('open_ports', []))
            ))
        
        conn.commit()
        conn.close()

# VULNERABILITY ENGINE
class VulnerabilityEngine:
    @staticmethod
    def calculate_device_risk(device):
        risk_score = 0
        open_port_count = len(device.get('open_ports', []))
        risk_score += open_port_count * 1.5
        
        if device.get('device_type') in ['ROUTER', 'SERVER']:
            risk_score += 5
        
        if risk_score >= 9:
            return 'CRITICAL'
        elif risk_score >= 7:
            return 'HIGH'
        elif risk_score >= 4:
            return 'MEDIUM'
        elif risk_score >= 1:
            return 'LOW'
        else:
            return 'MINIMAL'

# REPORT GENERATOR
class ReportGenerator:
    @staticmethod
    def generate_html_report(scan_data, filename=None):
        if not filename:
            filename = f"mubbleZX_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>mubbleZX Scan Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .section {{ background-color: white; margin: 20px 0; padding: 20px; border-radius: 5px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #3498db; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 mubbleZX Network Reconnaissance Report</h1>
        <p>Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Network: {scan_data['network']}</p>
    </div>
    
    <div class="section">
        <h2>📊 Scan Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Devices Found</td>
                <td>{len(scan_data['devices'])}</td>
            </tr>
            <tr>
                <td>Open Ports Detected</td>
                <td>{sum(len(d.get('open_ports', [])) for d in scan_data['devices'])}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>🖥️ Devices Discovered</h2>
        <table>
            <tr><th>IP</th><th>Vendor</th><th>Type</th><th>Risk</th><th>Open Ports</th></tr>
"""
        
        for device in scan_data['devices']:
            port_count = len(device.get('open_ports', []))
            html_content += f"""
            <tr>
                <td>{device['ip']}</td>
                <td>{device.get('vendor', 'Unknown')}</td>
                <td>{device.get('device_type', 'Unknown')}</td>
                <td>{device.get('risk_level', 'UNKNOWN')}</td>
                <td>{port_count}</td>
            </tr>
"""
        
        html_content += """
        </table>
    </div>
    
    <footer style="text-align: center; margin-top: 40px; color: #7f8c8d;">
        <p>Generated by mubbleZX v12 Enterprise</p>
    </footer>
</body>
</html>
"""
        
        with open(filename, 'w') as f:
            f.write(html_content)
        
        return filename

# MAIN APPLICATION
class mubbleZX:
    def __init__(self, root):
        self.root = root
        self.root.title("mubbleZX v12 - Enterprise Framework")
        self.root.geometry("1200x700")
        self.root.configure(bg="black")
        
        self.devices = []
        self.scanning = False
        self.scan_id = None
        self.db = MubbleDatabase()
        self.current_network = "192.168.1.0/24"
        
        self.create_ui()
    
    def create_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Control Panel", padding=10)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(control_frame, text="Network:").pack(side=tk.LEFT, padx=5)
        self.network_var = tk.StringVar(value=self.current_network)
        network_combo = ttk.Combobox(control_frame, textvariable=self.network_var, width=20)
        network_combo['values'] = ["192.168.1.0/24", "192.168.0.0/24", "10.0.0.0/24"]
        network_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Start Scan (SPACE)", command=self.start_scan).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export HTML", command=self.export_html).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(control_frame, text="Ready", foreground="green")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Scan Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview
        self.tree = ttk.Treeview(results_frame, columns=('IP', 'Vendor', 'Type', 'Ports', 'Risk'), height=20)
        self.tree.heading('#0', text='Details')
        self.tree.heading('IP', text='IP Address')
        self.tree.heading('Vendor', text='Vendor')
        self.tree.heading('Type', text='Device Type')
        self.tree.heading('Ports', text='Open Ports')
        self.tree.heading('Risk', text='Risk Level')
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.root.bind('<space>', lambda e: self.start_scan())
    
    def start_scan(self):
        if self.scanning:
            return
        
        self.scanning = True
        self.current_network = self.network_var.get()
        self.scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.status_label.config(text="Scanning...", foreground="orange")
        
        thread = threading.Thread(target=self.run_scan)
        thread.daemon = True
        thread.start()
    
    def run_scan(self):
        try:
            print(f"\n[*] Starting mubbleZX v12 scan on {self.current_network}")
            
            ping_output = subprocess.run(
                ["sudo", "nmap", "-sn", self.current_network],
                capture_output=True, text=True, timeout=60
            ).stdout
            
            self.devices = self.parse_ping_scan(ping_output)
            print(f"[+] Found {len(self.devices)} devices")
            
            for i, device in enumerate(self.devices):
                print(f"[*] Scanning {device['ip']}")
                self.status_label.config(text=f"Scanning {i+1}/{len(self.devices)}")
                
                detail_output = subprocess.run(
                    ["sudo", "nmap", "-sV", device['ip']],
                    capture_output=True, text=True, timeout=30
                ).stdout
                
                detail_info = self.parse_detail_scan(detail_output)
                device.update(detail_info)
                device['risk_level'] = VulnerabilityEngine.calculate_device_risk(device)
            
            scan_data = {
                'scan_id': self.scan_id,
                'network': self.current_network,
                'devices': self.devices
            }
            self.db.save_scan(scan_data)
            
            self.update_ui()
            self.status_label.config(text=f"Complete - {len(self.devices)} devices", foreground="green")
            
        except Exception as e:
            print(f"[-] Error: {e}")
            self.status_label.config(text=f"Error: {e}", foreground="red")
        
        finally:
            self.scanning = False
    
    def parse_ping_scan(self, output):
        devices = []
        lines = output.splitlines()
        
        for i, line in enumerate(lines):
            if 'Nmap scan report for' in line:
                ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', line)
                if ip_match:
                    ip = ip_match.group()
                    
                    mac, vendor = None, None
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
                        'open_ports': []
                    }
                    devices.append(device)
        
        return devices
    
    def parse_detail_scan(self, output):
        ports = []
        lines = output.splitlines()
        
        in_ports = False
        for line in lines:
            if line.strip().startswith('PORT'):
                in_ports = True
                continue
            
            if in_ports and line.strip():
                if not line[0].isdigit():
                    break
                
                match = re.match(r'^(\d+)/tcp\s+(\w+)\s+([\w\-]+)', line.strip())
                if match:
                    ports.append({
                        'port': match.group(1),
                        'service': match.group(3)
                    })
        
        return {'open_ports': ports}
    
    def update_ui(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for device in self.devices:
            ip = device['ip']
            vendor = device.get('vendor', 'Unknown')
            dev_type = device.get('device_type', 'Unknown')
            port_count = len(device.get('open_ports', []))
            risk = device.get('risk_level', 'UNKNOWN')
            
            parent = self.tree.insert('', 'end', text=ip, values=(ip, vendor, dev_type, port_count, risk))
            
            for port_info in device.get('open_ports', []):
                self.tree.insert(parent, 'end', text=f"Port {port_info['port']}", 
                               values=('', '', port_info.get('service', ''), '', ''))
    
    def export_html(self):
        if not self.devices:
            messagebox.showwarning("No Data", "Please run a scan first")
            return
        
        scan_data = {
            'network': self.current_network,
            'devices': self.devices
        }
        
        filename = ReportGenerator.generate_html_report(scan_data)
        messagebox.showinfo("Success", f"Report saved to {filename}")
    
    def export_csv(self):
        if not self.devices:
            messagebox.showwarning("No Data", "Please run a scan first")
            return
        
        filename = f"mubbleZX_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['IP', 'Vendor', 'Type', 'Risk', 'Open Ports', 'Services'])
            
            for device in self.devices:
                ports = ', '.join([p['port'] for p in device.get('open_ports', [])])
                services = ', '.join([p.get('service', '') for p in device.get('open_ports', [])])
                writer.writerow([
                    device['ip'],
                    device.get('vendor', ''),
                    device.get('device_type', ''),
                    device.get('risk_level', ''),
                    ports,
                    services
                ])
        
        messagebox.showinfo("Success", f"CSV saved to {filename}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  mubbleZX v12 - ENTERPRISE FRAMEWORK")
    print("  Network Reconnaissance + Vulnerability Detection")
    print("="*60)
    print("\n[!] HOME NETWORK ONLY - USE ETHICALLY\n")
    
    root = tk.Tk()
    app = mubbleZX(root)
    root.mainloop()
