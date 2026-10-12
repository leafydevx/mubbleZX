"""Core nmap scanner engine for mubbleZX."""

import subprocess
import re
import json
from datetime import datetime


COMMON_PORTS = "21,22,23,25,53,80,110,135,139,143,443,445,993,995,3306,3389,5432,5900,8080,8443"


class ScanResult:
    def __init__(self, network, interface_label=None):
        self.network = network
        self.interface_label = interface_label
        self.scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.timestamp = datetime.now().isoformat()
        self.devices = []

    def to_dict(self):
        return {
            "scan_id": self.scan_id,
            "network": self.network,
            "interface": self.interface_label,
            "timestamp": self.timestamp,
            "device_count": len(self.devices),
            "devices": [d.copy() for d in self.devices],
        }

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent)

    def save_json(self, path=None):
        if not path:
            path = f"mubbleZX_{self.scan_id}.json"
        with open(path, "w") as f:
            f.write(self.to_json())
        return path


class NmapScanner:
    """Wraps nmap for host discovery, port scanning, and service/OS detection."""

    def __init__(self, sudo=True):
        self.sudo = sudo

    def _run(self, args, timeout=120):
        cmd = []
        if self.sudo:
            cmd.append("sudo")
        cmd.extend(["nmap"] + args)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout

    # ---- discovery ----

    def discover_hosts(self, network):
        output = self._run(["-sn", network], timeout=60)
        return self._parse_discovery(output)

    def _parse_discovery(self, output):
        devices = []
        lines = output.splitlines()
        for i, line in enumerate(lines):
            if "Nmap scan report for" not in line:
                continue
            ip_match = re.search(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', line)
            if not ip_match:
                continue
            ip = ip_match.group(1)

            hostname = None
            h_match = re.match(r'Nmap scan report for (.+?) \(', line)
            if h_match:
                hostname = h_match.group(1)

            mac, vendor = None, None
            for j in range(i + 1, min(i + 5, len(lines))):
                m = re.search(r'MAC Address:\s+([0-9A-Fa-f:]+)\s+\((.+?)\)', lines[j])
                if m:
                    mac, vendor = m.group(1), m.group(2)
                    break

            last_octet = int(ip.split(".")[-1])
            if last_octet in (1, 254):
                device_type = "ROUTER"
            else:
                device_type = "DEVICE"

            devices.append({
                "ip": ip,
                "mac": mac,
                "vendor": vendor,
                "hostname": hostname or ip,
                "device_type": device_type,
                "open_ports": [],
                "os": None,
                "risk_level": "UNKNOWN",
            })
        return devices

    # ---- port scan ----

    def scan_ports(self, ip, ports=None):
        port_arg = ports or COMMON_PORTS
        output = self._run(["-p", port_arg, ip], timeout=60)
        return self._parse_ports(output)

    def _parse_ports(self, output):
        ports = []
        in_section = False
        for line in output.splitlines():
            if line.strip().startswith("PORT"):
                in_section = True
                continue
            if in_section:
                if not line.strip() or not line[0].isdigit():
                    break
                m = re.match(r'^(\d+)/(tcp|udp)\s+(\w+)\s+([\w\-\?]+)\s*(.*)', line.strip())
                if m:
                    ports.append({
                        "port": int(m.group(1)),
                        "protocol": m.group(2),
                        "state": m.group(3),
                        "service": m.group(4),
                        "version": m.group(5).strip(),
                    })
        return ports

    # ---- service + OS detection ----

    def deep_scan(self, ip):
        output = self._run(["-sV", "-O", "--osscan-guess", ip], timeout=120)
        ports = self._parse_ports(output)

        os_guess = None
        for line in output.splitlines():
            m = re.search(r'OS details:\s+(.+)', line)
            if m:
                os_guess = m.group(1)
                break
            m = re.search(r'Aggressive OS guesses:\s+(.+)', line)
            if m:
                os_guess = m.group(1).split(",")[0].strip()
                break

        return {"ports": ports, "os": os_guess}

    # ---- full pipeline ----

    def full_scan(self, network, interface_label=None, deep=False, on_progress=None):
        result = ScanResult(network, interface_label)

        if on_progress:
            on_progress("discovery", f"Discovering hosts on {network}...")
        devices = self.discover_hosts(network)

        for i, device in enumerate(devices):
            ip = device["ip"]
            if on_progress:
                on_progress("scanning", f"Scanning {ip} ({i+1}/{len(devices)})")

            if deep:
                info = self.deep_scan(ip)
                device["open_ports"] = [p for p in info["ports"] if p["state"] == "open"]
                device["os"] = info["os"]
            else:
                ports = self.scan_ports(ip)
                device["open_ports"] = [p for p in ports if p["state"] == "open"]

            device["device_type"] = classify_device(device)
            device["risk_level"] = assess_risk(device)

        result.devices = devices
        if on_progress:
            on_progress("complete", f"Scan complete: {len(devices)} devices found")
        return result


def classify_device(device):
    """Classify device type from open ports and vendor hints."""
    port_numbers = {p["port"] for p in device.get("open_ports", [])}
    services = {p.get("service", "").lower() for p in device.get("open_ports", [])}
    vendor = (device.get("vendor") or "").lower()
    last_octet = int(device["ip"].split(".")[-1])

    if last_octet in (1, 254) or "router" in vendor:
        return "ROUTER"
    if 80 in port_numbers and 443 in port_numbers and 22 in port_numbers:
        return "SERVER"
    if 3389 in port_numbers:
        return "WORKSTATION"
    if 5900 in port_numbers:
        return "WORKSTATION"
    if 631 in port_numbers or 9100 in port_numbers or "printer" in vendor:
        return "PRINTER"
    if "apple" in vendor or "samsung" in vendor or "oneplus" in vendor:
        return "MOBILE"
    if 8080 in port_numbers or 8443 in port_numbers:
        return "IOT"
    if device.get("open_ports"):
        return "DEVICE"
    return "UNKNOWN"


def assess_risk(device):
    """Simple risk assessment based on open ports."""
    ports = device.get("open_ports", [])
    score = 0.0
    score += len(ports) * 1.5

    risky_ports = {21, 23, 135, 139, 445, 3389, 5900}
    for p in ports:
        if p["port"] in risky_ports:
            score += 3

    if device.get("device_type") in ("ROUTER", "SERVER"):
        score += 2

    if score >= 12:
        return "CRITICAL"
    if score >= 8:
        return "HIGH"
    if score >= 4:
        return "MEDIUM"
    if score >= 1:
        return "LOW"
    return "MINIMAL"
