🔍 Overview
MubbleZX is a multi‑version, defensive network diagnostics tool designed for authorized environments such as home networks, labs, and enterprise networks where the operator has explicit permission to perform scanning.

It provides:

Host discovery

Port scanning

OS fingerprinting

Device classification

JSON‑structured reporting

Versioned improvements across releases

MubbleZX is strictly an ethical, legal, and compliance‑aligned tool.

🛡️ Legal & Ethical Notice
Each item begins with a Guided Link.

Authorized use only — You may only scan networks you own or have explicit written permission to test.

International cybercrime compliance — MubbleZX follows global laws including the Budapest Convention, EU Directive 2013/40/EU, CFAA, CMA, and Romanian Penal Code Art. 360–364.

Ethical hacking standards — ISO/IEC 27001 and CEH principles apply.

Unauthorized access, interception, or interference is illegal worldwide.

🚀 Features
Each item begins with a Guided Link.

Host discovery

Port scanning

OS fingerprinting

MAC vendor lookup

Device classification

JSON reporting

🧩 Version History
V1 — Basic Discovery
Ping sweep

IP detection

V2 — Nmap Integration
Port scanning

OS detection

MAC vendor parsing

JSON output

V3 — Device Intelligence
Device type guessing

Port‑based classification

V4 — Structured Reporting
Timestamped logs

Multi‑device JSON reports

V5 — Claude Edition
Enhanced parsing

Cleaner summaries

Cross‑model collaboration

📦 Installation
See INSTALL.md for full instructions.

Basic setup:

bash
git clone https://github.com/leafydevx/mubbleZX.git
cd mubbleZX

Install Nmap (the tools call the nmap command):

bash
sudo apt install nmap

Python 3 is required. The scripts import only standard-library modules, plus tkinter for the GUI versions (v4, v5, and v12). Install tkinter with your system package manager if it is missing (for example `sudo apt install python3-tk`).

▶️ Usage
Each version is a separate script. Run the one you want directly with Python:

bash
python3 mubbleZX.py          # v4: radar-style GUI, port scan
python3 mubbleZXv2.py        # v2: text output, nmap-based scan
python3 mubbleZXv5.py        # v5: radar-style GUI (hold SPACE to scan)
python3 mubbleZXv12_Enterprise.py   # v12: GUI, results stored in SQLite

Scan settings are not command-line options yet. The v2 script reads its target and options from a CONFIG block at the top of the file (for example NETWORK_RANGE, ENABLE_OS_DETECTION, and OUTPUT_JSON_FILE). The default target in the GUI versions is 192.168.1.0/24. Change it in the source before scanning a different network.

Each item begins with a Guided Link:

Authorized scanning rules

Network basics

🔒 Security
See SECURITY.md for full policy.

Key points:

No unauthorized access

No exploitation

No disruption

No harmful interference

Follow responsible disclosure

🤝 Contributing
See CONTRIBUTING.md.

Contributions must:

Follow legal and ethical rules

Avoid offensive features

Include documentation updates

Use clean, readable code

📜 License
See LICENSE.

MubbleZX is licensed for authorized, ethical, defensive use only.

⭐ Additional Documentation
INSTALL.md

SECURITY.md

CONTRIBUTING.md

LICENSE
THE OWNER/DEVELOPER IS NOT RESPONSIBLE FOR ANY MISUSE OR HARMFUL ACTS OF THIS SOFTWARE.
