"""Network interface detection and classification.

Labeling convention:
  - Wired (ethernet) interfaces are shown as "wlan"
  - Wireless (Wi-Fi) interfaces are shown as "wifi"
"""

import subprocess
import re
import os


def _read_sys_net(iface, attr):
    path = f"/sys/class/net/{iface}/{attr}"
    try:
        with open(path) as f:
            return f.read().strip()
    except (OSError, IOError):
        return None


def _is_wireless(iface):
    return os.path.isdir(f"/sys/class/net/{iface}/wireless")


def detect_interfaces():
    """Return a list of active network interfaces with mubbleZX labels.

    Each entry: {
        "real_name": "eth0",       # OS-level name
        "label": "wlan0",          # mubbleZX display name
        "type": "wired"|"wireless",
        "ip": "192.168.1.5",
        "mac": "aa:bb:cc:dd:ee:ff",
        "state": "UP"|"DOWN",
        "network": "192.168.1.0/24"
    }
    """
    interfaces = []
    wlan_idx = 0
    wifi_idx = 0

    try:
        out = subprocess.run(
            ["ip", "-o", "addr", "show"],
            capture_output=True, text=True, timeout=10
        ).stdout
    except Exception:
        return interfaces

    seen = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        iface = parts[1]
        if iface == "lo" or iface in seen:
            continue

        ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/(\d+)', line)
        if not ip_match:
            continue
        seen.add(iface)

        ip_addr = ip_match.group(1)
        prefix = int(ip_match.group(2))

        octets = list(map(int, ip_addr.split('.')))
        mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
        net_int = (octets[0] << 24 | octets[1] << 16 | octets[2] << 8 | octets[3]) & mask
        network = f"{(net_int >> 24) & 0xFF}.{(net_int >> 16) & 0xFF}.{(net_int >> 8) & 0xFF}.{net_int & 0xFF}/{prefix}"

        mac = _read_sys_net(iface, "address") or "unknown"
        state = _read_sys_net(iface, "operstate") or "unknown"

        if _is_wireless(iface):
            iface_type = "wireless"
            label = f"wifi{wifi_idx}"
            wifi_idx += 1
        else:
            iface_type = "wired"
            label = f"wlan{wlan_idx}"
            wlan_idx += 1

        interfaces.append({
            "real_name": iface,
            "label": label,
            "type": iface_type,
            "ip": ip_addr,
            "mac": mac,
            "state": state.upper(),
            "network": network,
        })

    return interfaces


def get_default_network():
    """Return the network CIDR of the first active interface, or a fallback."""
    for iface in detect_interfaces():
        if iface["state"] == "UP" or iface["ip"]:
            return iface["network"]
    return "192.168.1.0/24"


def print_interfaces(interfaces):
    """Pretty-print detected interfaces."""
    if not interfaces:
        print("  (no active interfaces detected)")
        return
    for iface in interfaces:
        tag = "wired -> wlan" if iface["type"] == "wired" else "Wi-Fi -> wifi"
        print(f"  {iface['label']:8s}  {iface['ip']:16s}  {iface['network']:20s}  [{tag}]  (os: {iface['real_name']})")
