#!/usr/bin/env python3
import subprocess
import re
import json
from datetime import datetime

# ------------- CONFIG -------------
NETWORK_RANGE = "192.168.1.0/24"
ENABLE_OS_DETECTION = True      # uses -O (needs sudo, may be slower)
ENABLE_SERVICE_DETECTION = True # uses -sV
SAVE_JSON = True
OUTPUT_JSON_FILE = "mubbleZX_v2_results.json"

# ------------- NMAP COMMANDS -------------
def run_nmap_ping_scan(network_range: str) -> str:
    cmd = ["sudo", "nmap", "-sn", network_range]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def run_nmap_detail_scan(ip: str) -> str:
    # -sV: service detection, -O: OS detection (optional)
    cmd = ["sudo", "nmap"]
    if ENABLE_SERVICE_DETECTION:
        cmd.append("-sV")
    if ENABLE_OS_DETECTION:
        cmd.append("-O")
    cmd.append(ip)

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

# ------------- PARSING HELPERS -------------
IP_LINE_RE = re.compile(r"Nmap scan report for ([\d\.]+)")
MAC_LINE_RE = re.compile(r"MAC Address:\s+([0-9A-Fa-f:]+)\s+\((.+?)\)")
HOSTNAME_LINE_RE = re.compile(r"Nmap scan report for (.+) \(([\d\.]+)\)")
OS_LINE_RE = re.compile(r"OS details:\s+(.+)")
PORT_LINE_RE = re.compile(r"^(\d+)/tcp\s+(\w+)\s+([\w\-\?]+)\s*(.*)$")

def parse_ping_scan_output(output: str):
    devices = []
    lines = output.splitlines()
    for i, line in enumerate(lines):
        ip_match = IP_LINE_RE.search(line)
        if ip_match:
            ip = ip_match.group(1)
            mac = None
            vendor = None

            # Look ahead for MAC line
            for j in range(i + 1, min(i + 5, len(lines))):
                mac_match = MAC_LINE_RE.search(lines[j])
                if mac_match:
                    mac = mac_match.group(1)
                    vendor = mac_match.group(2)
                    break

            devices.append({
                "ip": ip,
                "mac": mac,
                "vendor": vendor
            })
    return devices

def parse_detail_scan_output(output: str):
    os_guess = None
    hostname = None
    ports = []

    lines = output.splitlines()

    # Hostname
    for line in lines:
        h_match = HOSTNAME_LINE_RE.search(line)
        if h_match:
            hostname = h_match.group(1)
            break

    # OS details
    for line in lines:
        os_match = OS_LINE_RE.search(line)
        if os_match:
            os_guess = os_match.group(1)
            break

    # Ports
    in_port_section = False
    for line in lines:
        if line.strip().startswith("PORT"):
            in_port_section = True
            continue
        if in_port_section:
            if not line.strip():
                break
            p_match = PORT_LINE_RE.match(line.strip())
            if p_match:
                port = p_match.group(1)
                state = p_match.group(2)
                service = p_match.group(3)
                extra = p_match.group(4).strip()
                ports.append({
                    "port": port,
                    "state": state,
                    "service": service,
                    "extra": extra
                })

    return {
        "hostname": hostname,
        "os_guess": os_guess,
        "ports": ports
    }

# ------------- MAIN LOGIC -------------
def main():
    print("============================================================")
    print("[*] Running Nmap ping scan on:", NETWORK_RANGE)
    print("============================================================")
    ping_output = run_nmap_ping_scan(NETWORK_RANGE)
    print(ping_output)

    devices = parse_ping_scan_output(ping_output)
    print(f"[*] Devices found: {len(devices)}")
    print()

    full_results = []
    for dev in devices:
        ip = dev["ip"]
        print("============================================================")
        print(f"[*] Running detailed Nmap scan on: {ip}")
        print("============================================================")
        detail_output = run_nmap_detail_scan(ip)
        print(detail_output)

        detail_info = parse_detail_scan_output(detail_output)

        device_entry = {
            "ip": ip,
            "mac": dev["mac"],
            "vendor": dev["vendor"],
            "hostname": detail_info["hostname"],
            "os_guess": detail_info["os_guess"],
            "ports": detail_info["ports"],
            "scanned_at": datetime.now().isoformat()
        }
        full_results.append(device_entry)

        # Pretty print summary
        print("\n--- DEVICE SUMMARY ---")
        print(f"IP:       {device_entry['ip']}")
        print(f"MAC:      {device_entry['mac']}")
        print(f"Vendor:   {device_entry['vendor']}")
        print(f"Hostname: {device_entry['hostname']}")
        print(f"OS:       {device_entry['os_guess']}")
        print("Ports:")
        for p in device_entry["ports"]:
            print(f"  - {p['port']}/tcp {p['state']} {p['service']} {p['extra']}")
        print("----------------------\n")

    if SAVE_JSON:
        with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(full_results, f, indent=2)
        print(f"[*] Saved results to {OUTPUT_JSON_FILE}")

if __name__ == "__main__":
    main()

