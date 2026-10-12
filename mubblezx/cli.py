"""mubbleZX CLI - nmap-based network scanning framework."""

import argparse
import sys

from . import __version__
from .interfaces import detect_interfaces, print_interfaces, get_default_network
from .scanner import NmapScanner
from .reports import save_json, save_csv, save_html


BANNER = f"""
 ███╗   ███╗██╗   ██╗██████╗ ██████╗ ██╗     ███████╗███████╗██╗  ██╗
 ████╗ ████║██║   ██║██╔══██╗██╔══██╗██║     ██╔════╝╚══███╔╝╚██╗██╔╝
 ██╔████╔██║██║   ██║██████╔╝██████╔╝██║     █████╗    ███╔╝  ╚███╔╝
 ██║╚██╔╝██║██║   ██║██╔══██╗██╔══██╗██║     ██╔══╝   ███╔╝  ██╔██╗
 ██║ ╚═╝ ██║╚██████╔╝██████╔╝██████╔╝███████╗███████╗███████╗██╔╝ ██╗
 ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝
 v{__version__} — nmap-based network scanning framework
 Wired → wlan  |  Wi-Fi → wifi
"""


def progress_callback(stage, msg):
    print(f"  [{stage.upper():>10s}] {msg}")


def cmd_interfaces(args):
    print("\n  Detected network interfaces:\n")
    ifaces = detect_interfaces()
    print_interfaces(ifaces)
    print()


def cmd_scan(args):
    network = args.target or get_default_network()
    ifaces = detect_interfaces()

    iface_label = None
    for iface in ifaces:
        if network.startswith(iface["network"].rsplit("/", 1)[0].rsplit(".", 1)[0]):
            iface_label = iface["label"]
            break
    if not iface_label and ifaces:
        iface_label = ifaces[0]["label"]

    print(f"\n  Target network : {network}")
    print(f"  Interface      : {iface_label or 'unknown'}")
    print(f"  Mode           : {'deep (service + OS)' if args.deep else 'standard'}")
    print()

    scanner = NmapScanner(sudo=not args.no_sudo)
    result = scanner.full_scan(
        network,
        interface_label=iface_label,
        deep=args.deep,
        on_progress=progress_callback,
    )

    print(f"\n  {'='*60}")
    print(f"  SCAN RESULTS — {len(result.devices)} devices on {network}")
    print(f"  {'='*60}\n")

    for d in result.devices:
        ports_str = ", ".join(f"{p['port']}/{p['service']}" for p in d["open_ports"])
        os_str = f"  OS: {d['os']}" if d.get("os") else ""
        print(f"  {d['ip']:16s}  {d.get('vendor') or 'Unknown':20s}  [{d['device_type']:10s}]  Risk: {d['risk_level']:8s}{os_str}")
        if ports_str:
            print(f"  {'':16s}  Ports: {ports_str}")
        print()

    if args.json:
        p = save_json(result, args.json if isinstance(args.json, str) and args.json != "True" else None)
        print(f"  JSON saved: {p}")
    if args.csv:
        p = save_csv(result, args.csv if isinstance(args.csv, str) and args.csv != "True" else None)
        print(f"  CSV saved:  {p}")
    if args.html:
        p = save_html(result, args.html if isinstance(args.html, str) and args.html != "True" else None)
        print(f"  HTML saved: {p}")


def main():
    print(BANNER)

    parser = argparse.ArgumentParser(
        prog="mubblezx",
        description="mubbleZX — nmap-based network scanning framework",
    )
    sub = parser.add_subparsers(dest="command")

    # interfaces
    sub.add_parser("interfaces", aliases=["ifaces", "if"], help="List detected network interfaces")

    # scan
    sp = sub.add_parser("scan", help="Scan a network")
    sp.add_argument("target", nargs="?", help="Target network CIDR (default: auto-detect)")
    sp.add_argument("--deep", action="store_true", help="Enable service version + OS detection")
    sp.add_argument("--no-sudo", action="store_true", help="Run nmap without sudo")
    sp.add_argument("--json", nargs="?", const=True, help="Save results as JSON")
    sp.add_argument("--csv", nargs="?", const=True, help="Save results as CSV")
    sp.add_argument("--html", nargs="?", const=True, help="Save results as HTML report")

    args = parser.parse_args()

    if args.command in ("interfaces", "ifaces", "if"):
        cmd_interfaces(args)
    elif args.command == "scan":
        cmd_scan(args)
    else:
        parser.print_help()
        print("\n  Quick start:")
        print("    python -m mubblezx interfaces   # show wlan/wifi interfaces")
        print("    python -m mubblezx scan          # scan default network")
        print("    python -m mubblezx scan 10.0.0.0/24 --deep --json --html")
        print()


if __name__ == "__main__":
    main()
