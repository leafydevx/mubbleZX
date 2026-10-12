# mubbleZX

nmap-based network scanning framework.

**Interface labeling:** wired ethernet shows as `wlan`, normal Wi-Fi shows as `wifi`.

## Features

- Host discovery via nmap ping sweep
- Port scanning (common ports or custom ranges)
- Service version detection (`-sV`)
- OS fingerprinting (`-O`)
- Automatic device classification (router, server, workstation, printer, mobile, IoT)
- Risk assessment per device
- Interface auto-detection with wlan/wifi labeling
- Export to JSON, CSV, and HTML reports

## Installation

```bash
sudo apt install nmap
git clone https://github.com/leafydevx/mubbleZX.git
cd mubbleZX
```

## Usage

```bash
# List network interfaces (wired = wlan, Wi-Fi = wifi)
python -m mubblezx interfaces

# Scan the default network
python -m mubblezx scan

# Scan a specific network with deep (service + OS) detection
python -m mubblezx scan 192.168.1.0/24 --deep

# Scan and export reports
python -m mubblezx scan --json --csv --html

# Scan without sudo
python -m mubblezx scan --no-sudo
```

## Framework Structure

```
mubblezx/
  __init__.py       # version
  __main__.py       # python -m entry point
  cli.py            # CLI argument parsing and output
  interfaces.py     # network interface detection (wlan/wifi labeling)
  scanner.py        # core nmap scanner engine
  reports.py        # JSON, CSV, HTML report generators
```

## Interface Labeling

| Connection Type | mubbleZX Label | Example |
|----------------|----------------|---------|
| Wired (ethernet) | `wlan0`, `wlan1` | eth0 -> wlan0 |
| Wi-Fi (wireless) | `wifi0`, `wifi1` | wlan0 -> wifi0 |

## Legal & Ethical Notice

Authorized use only. You may only scan networks you own or have explicit written permission to test.

MubbleZX follows global cybercrime laws including the Budapest Convention, EU Directive 2013/40/EU, CFAA, and CMA.

THE OWNER/DEVELOPER IS NOT RESPONSIBLE FOR ANY MISUSE OR HARMFUL ACTS OF THIS SOFTWARE.

## Legacy Versions

Previous single-file versions are preserved in the repository root:
- `mubbleZX.py` - v4 radar GUI
- `mubbleZXv2.py` - v2 CLI scanner
- `mubbleZXv5.py` - v5 radar + JSON
- `mubbleZXv12_Enterprise.py` - v12 enterprise GUI

## License

See LICENSE. Licensed for authorized, ethical, defensive use only.
