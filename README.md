<div align="center">

# Damn Vuln IoT SoC Demo

[![Ubtuntu](https://img.shields.io/badge/platform-Ubuntu%2020.04-0078d7.svg?style=for-the-badge&logo=appveyor)](https://www.ubuntu-fr.org) 
[![Python](https://img.shields.io/badge/language-Python3-%23f34b7d.svg?style=for-the-badge&logo=appveyor)](https://www.python.org)

</div>

# :book: Damn Vuln IoT SoC Overview

The aim of Damn Vuln IoT SoC is to create an educational platform with a primary focus on constructing a generator for Systems-on-Chip (SoC) that is vulnerable, configurable, and user-friendly. It is tailored for individuals seeking to improve their proficiency in identifying or exploiting vulnerabilities within the field of hardware security. This platform can function as instructional material or be employed for Capture The Flag (CTF) challenges, offering users practical hands-on experience in a controlled setting. Additionally, the platform can be utilized to assess hardware description analysis tools that identify bugs and backdoors.

# :rocket: Getting Started

> ⚠️ Before installation, we assume that your development tools for your FPGA board are already installed, for example, if you are using a Digilent Basys3 board you need to install Xilinx Vivado. 
> These tools are not necessary if you plan to use only simulation.

## Hardware

- Digilent Basys3 (the demo can easily be ported to another FPGA board)
- Keypad (Pmod KYPD)
- Flash SPI (Pmod SF3)
- JTAG Programmer (JTAG-HS2 / FT232H)

## Use the demo

To use this demo you have to install [Damn Vuln IoT SoC](https://github.com/Damn-Vuln-IoT-SoC/Damn-Vuln-IoT-SoC) before.

If you have the hardware :

```console
$ git clone https://github.com/Damn-Vuln-IoT-SoC/Damn-Vuln-IoT-SoC-Demo.git
$ pip3 install Damn-Vuln-IoT-SoC-Demo/
$ cd Damn-Vuln-IoT-SoC-Demo/Damn-Vuln-IoT-SoC-Demo
$ chmod +x build.py
$ ./build.py --cpu-type=vexriscv --cpu-variant=lite+vul --integrated-main-ram-size=0x5000 --no-compile-gateware --build
$ cd firmware
$ ./firmware.py --build-path=../build/board/ --mem=rom
$ cd ..
$ ./build.py --cpu-type=vexriscv --cpu-variant=lite+vul --integrated-rom-init=firmware/firmware.bin --bios-console=disable --build --load
$ screen <device> 115200
```
Alternatively, you can try the simulation, which is a downgraded version of the challenges and won't allow you to do them all.

```console
$ git clone https://github.com/Damn-Vuln-IoT-SoC/Damn-Vuln-IoT-SoC-Demo.git
$ pip3 install Damn-Vuln-IoT-SoC-Demo/
$ cd Damn-Vuln-IoT-SoC-Demo/Damn-Vuln-IoT-SoC-Demo
$ chmod +x build.py
$ ./sim.py --cpu-type=vexriscv --cpu-variant=lite+vul --integrated-main-ram-size=0x5000 --no-compile-gateware
$ cd firmware
$ ./firmware.py --build-path=../build/sim/ --mem=rom
$ cd ..
$ ./sim.py --cpu-type=vexriscv --cpu-variant=lite+vul --integrated-rom-init=firmware/firmware.bin --bios-console=disable
```

# Contributors

### Founder of the project

- [Philippe TANGUY](https://labsticc.fr/en/directory/tanguy-philippe)

### Developers

- [Adam HENAULT](https://github.com/adamhlt)
- Mohamed AFASSI
- Seydina Oumar NIANG
- Rébecca SZABO
