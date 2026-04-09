# Security Hardening

## Overview
Security hardening in the Linux kernel encompasses documentation, tooling, and processes for identifying, reporting, and mitigating security vulnerabilities in the kernel. The kernel has a dedicated security documentation tree (Documentation/security/index.rst), a Linux Security Modules (LSM) framework for building mandatory access control systems, self-protection mechanisms, and a confidential embargo process for hardware vulnerabilities.

## Key Facts
- **Security documentation**: Comprehensive tree at Documentation/security/index.rst
- **LSM framework**: Linux Security Modules (Documentation/security/lsm-development.rst) allow stacking multiple security modules (SELinux, AppArmor, SMACK, etc.)
- **Self-protection**: Kernel self-protection features documented at Documentation/security/self-protection.rst
- **CVE process**: Coordinated Vulnerability Exposure process documented at Documentation/process/cve.rst
- **Embargoed hardware issues**: Confidential disclosure process for hardware-level vulnerabilities (Documentation/process/embargoed-hardware-issues.rst) distinct from standard bug reporting
- **Bug reporting**: Security bugs reported via Documentation/process/security-bugs.rst, not public channels
- **Seccomp**: Filter-based syscall restriction documented at Documentation/userspace-api/seccomp_filter.rst

## Connections
- [[LinuxKernel]] — The subject being hardened against security threats
- [[Linux]] — Hardening protects Linux-based systems and the broader Linux ecosystem

## Connections (additional)
- [[LinuxKernel]] — The subject being hardened against security threats
- [[Linux]] — Hardening protects Linux-based systems and the broader Linux ecosystem