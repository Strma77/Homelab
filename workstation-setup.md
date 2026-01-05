# Workstation Setup - January 2025

## Hardware
- CPU: Ryzen 7 3700X
- RAM: 32GB DDR4
- GPU: RTX 2060 Super
- Storage: 500GB NVMe SSD (Ubuntu) + 5.5TB HDD (data)

## OS Installation
- Wiped Windows from SSD
- Fresh Ubuntu 25.10 install
- HDD left untouched with data

## Issues Encountered
1. **Display scaling broken on first boot**
   - Fixed by: `sudo apt update && upgrade`, then relog
   
2. **Brave browser lag**
   - Fixed by uninstalling Brave downloaded via snap and installed it via their repo. Running it through terminal so it uses hardware acceleration and made an alias so I dont have to type the whole command.

## Software Installed
- Dev tools: VS Code, IntelliJ, build-essential, git
- CCNA: Cisco Packet Tracer, Wireshark
- Networking: Docker, VirtualBox
- Utils: Anki, fastfetch, micro

## Next Steps
- Configure Ubuntu Server VM
- Deploy first Docker container
- Continue CCNA (currently on Day 5)
