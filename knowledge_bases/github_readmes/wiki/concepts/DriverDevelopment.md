# Driver Development

## Overview
Device driver development is a major sub-discipline of Linux kernel programming. Drivers live within the kernel source tree, interact with the driver model (Documentation/driver-api/driver-model/driver.rst), support a range of bus types (PCI, USB, I2C, SPI, etc.), and must conform to the kernel's coding standards and APIs. Hardware vendors contributing drivers use the Device Tree bindings (Documentation/devicetree/bindings/) for describing hardware to the kernel.

## Key Facts
- **Driver API**: Full driver API documentation at Documentation/driver-api/index.rst
- **Driver model**: Subsystem-level infrastructure for registering and managing devices (Documentation/driver-api/driver-model/driver.rst)
- **Bus types**: Support for PCI, USB, I2C, SPI, platform bus, and more (Documentation/driver-api/driver-model/bus.rst)
- **Device Tree**: Hardware description format used on ARM, RISC-V, and other architectures (Documentation/devicetree/bindings/)
- **DMA API**: Direct Memory Access programming interface (Documentation/core-api/dma-api.rst)
- **Power management**: PM documentation for drivers at Documentation/driver-api/pm/index.rst
- **User persona**: Hardware Vendors are explicitly identified as a key contributor group for driver development

## Connections
- [[LinuxKernel]] — Drivers are developed as part of the Linux kernel source tree
- [[KernelDevelopment]] — Driver development is a specialized branch of kernel development
- [[Linux]] — Linux's broad hardware support is enabled by its extensive driver ecosystem

## Connections (additional)
- [[LinuxKernel]] — Drivers are developed as part of the Linux kernel source tree
- [[KernelDevelopment]] — Driver development is a specialized branch of kernel development
- [[Linux]] — Linux's broad hardware support is enabled by its extensive driver ecosystem