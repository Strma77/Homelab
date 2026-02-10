## Networking Configuration

The Ubuntu Server VM is connected to the local network using a bridged network adapter.
This allows the VM to behave as a first-class host on the LAN and simplifies VPN and service access.

### IP Addressing
- Interface: `enp0s3`
- Static IP: `192.168.100.50/24`
- Gateway: `192.168.100.1`
- Broadcast: `192.168.100.255`

A static IP was configured to ensure consistent addressing for:
- VPN endpoint configuration
- Future port forwarding
- Service accessibility

### Routing
- Default route via `192.168.100.1`
- Internet connectivity verified via IP and DNS resolution

### Configuration Method
- Static IP configured using netplan (`50-cloud-init.yaml`)
- DHCP disabled on the primary interface
- Configuration validated using routing and connectivity tests

## Constraints & Environment Limitations

The project is deployed in a residential network using an ISP-provided ZTE F8648P XGS-PON ONT.

The ONT exposes only a limited user-level management interface and does not provide access to:
- NAT configuration
- Port forwarding
- Firewall rules

As a result, inbound connections from the public internet to the local network are not possible in the default configuration.
This directly impacts VPN designs that rely on incoming connections to a home-hosted server.

### Design Implications

Due to the restricted capabilities of the ISP-provided ONT, the initial architecture must avoid reliance on inbound port forwarding.

This constraint informed the decision to:
- Treat remote access as a networking problem rather than a tooling problem
- Prioritize architectures that function behind ISP-controlled NAT
- Plan for alternative VPN topologies that do not require exposed home services

## Remote Access Strategy

### Phase 1 – Local VPN Testing
- WireGuard deployed inside the Ubuntu Server VM using Docker
- VPN functionality validated within the local network

### Phase 2 – ISP-Constrained Environment
- ISP ONT does not permit inbound port forwarding
- Direct remote VPN access from the internet is not possible

### Phase 3 – Planned Solutions
One of the following approaches will be implemented:
- Bridge mode on ISP ONT with a user-controlled router
- Outbound-only VPN architecture using an intermediate VPS
- Migration of edge networking to user-owned hardware

## Roadmap

### Completed
- Ubuntu Server VM deployment
- Static IP configuration
- Docker-based service architecture
- Local WireGuard deployment

### In Progress
- Evaluation of remote access strategies under ISP constraints

### Planned
- Migration to bridge mode or user-controlled router
- Secure remote access via VPN
- Audiobookshelf deployment behind authenticated access
- Optional HTTPS reverse proxy

---
---

# Conclusion
Remote access is currently limited by ISP-managed network equipment.
Future iterations will revisit this once user-controlled routing is available.

---

## Phase 4 – Tailscale Mesh Network Solution (Implemented)

### Problem
ISP ONT restrictions prevent inbound port forwarding, blocking traditional VPN server hosting.

### Solution
Tailscale provides a mesh VPN that works through NAT/firewalls without requiring port forwarding.
- Works via outbound connections (allowed by ISP)
- Creates encrypted peer-to-peer network
- Provides stable IPs for accessing services remotely

### Implementation
**Date:** February 9, 2025

#### Tailscale Installation on Ubuntu Server VM
```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start and authenticate
sudo tailscale up
# Authenticated via browser on host machine

# Verify IP assignment
tailscale ip -4
# Assigned: 100.x.x.x
```

#### Client Setup
- Tailscale app installed on Android/iOS
- Authenticated with same account
- Connection verified via browser test

#### Verification
- Tested connectivity from phone to VM Tailscale IP
- "Connection refused" response = network path working
- Ready for service deployment

### Status
✅ Tailscale mesh network operational  
✅ VM accessible from phone remotely  
⏳ Audiobookshelf deployment pending

#### Storage Configuration

Audiobooks are stored on the host machine's 5.5TB HDD to avoid duplication and enable centralized management.

**VirtualBox Shared Folder Setup:**

1. **Host Configuration** (VirtualBox GUI)
   - Shared folder created pointing to `~/audiobooks` on host
   - Folder name: `audiobooks`
   - Mount point: `/mnt/audiobooks`
   - Auto-mount: enabled
   - Read-only: disabled

2. **Guest Mounting** (Ubuntu Server VM)
```bash
   # Verify Guest Additions are loaded
   lsmod | grep vboxguest
   # Output: vboxguest 57344 0 ✅

   # Create mount point
   sudo mkdir -p /mnt/audiobooks

   # Mount the shared folder
   sudo mount -t vboxsf audiobooks /mnt/audiobooks

   # Verify accessibility
   ls -la /mnt/audiobooks
```

3. **Persistence**
   - Auto-mount via VirtualBox settings
   - Manual mount command preserved for troubleshooting

**Result:**
- Audiobooks stored once on host HDD
- Accessible to VM via `/mnt/audiobooks`
- No file duplication
- Changes on host immediately visible in VM
