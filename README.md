<div align="center">

# Damn Vuln IoT SoC Demo

[![Ubtuntu](https://img.shields.io/badge/platform-Ubuntu%2020.04-0078d7.svg?style=for-the-badge&logo=appveyor)](https://www.ubuntu-fr.org) 
[![Python](https://img.shields.io/badge/language-Python3-%23f34b7d.svg?style=for-the-badge&logo=appveyor)](https://www.python.org)

</div>

# :book: Project Overview

The aim of this project is to create an educational platform with a primary focus on constructing a generator for Systems-on-Chip (SoC) that is vulnerable, configurable, and user-friendly. It is tailored for individuals seeking to improve their proficiency in identifying or exploiting vulnerabilities within the field of hardware security. This platform can function as instructional material or be employed for Capture The Flag (CTF) challenges, offering users practical hands-on experience in a controlled setting. Additionally, the platform can be utilized to assess hardware description analysis tools that identify bugs and backdoors.

# :rocket: Getting Started

> ⚠️ Before installation, we assume that your development tools for your FPGA board are already installed, for example, if you are using a Digilent Basys3 board you need to install Xilinx Vivado. 
> These tools are not necessary if you plan to use only simulation.

## Build the documentation

### Generate the documentation

```bash
cd damn-vuln-iot-soc
pip3 install -r requirements.txt
cd docs
make html
cd _build/html
```

# Contributors

### Founder of the project

- [Philippe TANGUY](https://labsticc.fr/en/directory/tanguy-philippe)

### Developers

- Mohamed AFASSI
- [Adam HENAULT](https://github.com/adamhlt)
- Seydina Oumar NIANG
- Rébecca SZABO

# Credits

- [LiteX](https://github.com/enjoy-digital/litex) : This SoC generator is the basis of this project, it is a powerful tool.
- [Migen](https://m-labs.hk/gateware/migen/) : Migen is a Python-based tool that automates further the VLSI design process. It is used in LiteX and it is a very interesting tool.
