# Kernel Development

## Overview
Kernel development is the process of contributing to the Linux kernel's source code. It follows a unique, mailing-list-based workflow entirely different from the GitHub pull-request model used by most open-source projects. Contributors submit patches via email to subsystem maintainers, who review and apply them. The process demands rigorous code quality, adherence to a detailed coding style guide, and a deep understanding of systems programming in C.

## Key Facts
- **Workflow**: Patch-based email workflow — patches sent to lore.kernel.org mailing lists, reviewed by subsystem maintainers, then merged into the mainline tree
- **Getting started**: New contributors start with Documentation/process/development-process.rst and Documentation/process/submitting-patches.rst
- **Coding style**: Strict Linux kernel coding style documented in Documentation/process/coding-style.rst
- **Build system**: kbuild (Documentation/kbuild/index.rst) and development tools (Documentation/dev-tools/index.rst)
- **DCO requirement**: All contributions require a Signed-off-by line per the Developer Certificate of Origin
- **User personas**: New Kernel Developer, Academic Researcher, Maintainer, Hardware Vendor, Distribution Maintainer, and AI Coding Assistant each have dedicated documentation tracks
- **Mainline tree**: Maintained by Linus Torvalds; stable trees maintained separately by Greg KH and subsystem maintainers

## Connections
- [[LinuxKernel]] — The subject of kernel development activities
- [[Linux]] — Kernel development builds the core of the Linux operating system
- [[DeveloperCertificateOfOrigin]] — Required for all kernel contributions
- [[DriverDevelopment]] — A major sub-discipline of kernel development focused on writing device drivers
- [[SecurityHardening]] — Security experts work within the kernel development process to harden the kernel against vulnerabilities

## Connections (additional)
- [[LinuxKernel]] — The subject of kernel development activities
- [[Linux]] — Kernel development builds the core of the Linux operating system
- [[DeveloperCertificateOfOrigin]] — Required for all kernel contributions
- [[DriverDevelopment]] — A major sub-discipline of kernel development focused on writing device drivers
- [[SecurityHardening]] — Security experts work within the kernel development process to harden the kernel against vulnerabilities