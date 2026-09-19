1. Code of conduct
Respect legality:  
All contributions must align with international cybercrime law (Budapest Convention, EU Directive 2013/40/EU, CFAA, CMA) and ethical hacking standards (ISO/IEC 27001, CEH principles).

No offensive features:  
No code that:

performs unauthorized access

bypasses authentication

exploits vulnerabilities

disrupts services

interacts with RF jammers or interference devices

Authorized use only:  
All examples, docs, and features must assume you own the network or have explicit written permission.

2. How to contribute
Fork the repo  
Create your own fork and work in a feature branch:

feature/device-classification

feature/reporting-improvements

fix/bug-description

Write clean, documented code

Use clear function names

Add docstrings/comments

Keep logic readable and maintainable

Add tests where possible

For parsing

For JSON output

For classification logic

Update documentation  
If your change affects behavior, update:

README.md

DOCUMENTATION.md

any relevant section about legal/ethical use

3. Legal & ethical requirements
All contributions must:

Explicitly state authorized context in examples and docs.

Avoid language suggesting hacking, exploitation, or unauthorized use.

Respect privacy: no real IPs, domains, or sensitive data in examples.

Align with ethical hacking principles:

get permission

stay in scope

do no harm

4. Pull request guidelines
When opening a PR:

Title: short and clear

Add device type inference for smart TVs

Improve JSON report structure

Description: include:

what you changed

why you changed it

any legal/ethical considerations

any docs you updated

Checklist:

[ ] Code builds

[ ] No offensive/illegal features

[ ] Docs updated

[ ] Tests added/updated (if applicable)

5. Types of contributions welcome
New device classification logic

Better JSON reporting

Improved parsing of scan output

Safer defaults for scanning

Documentation improvements (especially legal/ethical clarity)

6. Not accepted
Exploit modules

Password cracking features

DDoS, flooding, or disruption tools

Anything that encourages or enables unauthorized access
