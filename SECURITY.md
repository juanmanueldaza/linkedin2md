# Security Policy

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue in linkedin2md, please report it responsibly.

### Preferred Reporting Method

Use GitHub's private vulnerability reporting:

**[Report a vulnerability →](https://github.com/juanmanueldaza/linkedin2md/security/advisories/new)**

This allows us to coordinate a fix before the details are made public.

### Alternative Contact

You can also email vulnerability reports to:

📧 **juan@daza.ar**

Please include:
- A description of the vulnerability
- Steps to reproduce or a proof-of-concept
- The affected version(s), if known
- Any potential impact you've identified

### Response Timeline

- **Acknowledgment**: We will acknowledge your report within **48 hours**.
- **Updates**: We will provide status updates at least every 7 days until the issue is resolved.
- **Resolution**: We will work to issue a fix as quickly as possible, prioritizing based on severity.

### What We Consider Security Issues

- Path traversal attacks in file output
- ZIP bomb or resource exhaustion vulnerabilities
- Injection vulnerabilities (e.g., CSV/Markdown injection)
- Sensitive data exposure
- Privilege escalation

### Out of Scope

- Denial of service via extremely large input files (already handled by the 500 MB file size limit)
- Issues in dependencies (please report to the respective maintainers)

## Responsible Disclosure

We ask that you:
1. Do not publicly disclose the vulnerability before a fix is available.
2. Give us reasonable time to address the issue before any public announcement.
3. Make a good-faith effort to avoid privacy risks, data destruction, or disruption to others.

Thank you for helping keep linkedin2md and its users safe.