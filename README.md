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
git clone https://github.com/yourusername/MubbleZX.git
cd MubbleZX
pip install -r requirements.txt
Install Nmap:

bash
sudo apt install nmap
▶️ Usage
Run a basic authorized scan:

bash
python mubblezx.py
Scan a specific subnet:

bash
python mubblezx.py --target 192.168.0.0/24
Export JSON:

bash
python mubblezx.py --json report.json
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
