## Networking Configuration

The Ubuntu Server VM is connected to the local network using a **bridged network adapter**, allowing it to behave as a first-class host on the LAN. This simplifies VPN usage and service access.

### IP Addressing

* Interface: `enp0s3`
* Static IP: `192.168.100.50/24`
* Gateway: `192.168.100.1`
* Broadcast: `192.168.100.255`

A static IP is used to ensure consistent addressing for VPN endpoints, service exposure, and future routing changes.

### Routing & Connectivity

* Default route via `192.168.100.1`
* Internet connectivity verified via IP reachability and DNS resolution

### Configuration Method

* Netplan configuration (`50-cloud-init.yaml`)
* DHCP disabled on the primary interface
* Configuration validated using routing table inspection and connectivity tests

---

## Environment Constraints

The project is deployed in a residential network using an **ISP-provided ZTE F8648P XGS-PON ONT**.

Limitations of the ONT include:

* No access to NAT configuration
* No port forwarding
* No firewall rule management

As a result, **inbound connections from the public internet are not possible**, which directly impacts VPN designs that rely on exposed home services.

### Design Implications

Due to ISP-controlled network equipment, the architecture must:

* Avoid reliance on inbound port forwarding
* Function behind carrier-grade or locked-down NAT
* Use outbound-only or NAT-traversal-friendly networking solutions

---

## Remote Access Strategy

### Phase 1 – Local VPN Validation

* WireGuard deployed inside the Ubuntu Server VM using Docker
* VPN functionality validated within the local network

### Phase 2 – ISP-Constrained Reality

* Inbound VPN access blocked by ONT limitations
* Traditional VPN server model deemed infeasible

### Phase 3 – Architectural Alternatives

Evaluated approaches:

* Bridge mode on ISP ONT with user-controlled router
* VPS-based hub-and-spoke VPN
* Mesh VPN solution (selected)

---

## Phase 4 – Tailscale Mesh Network (Implemented)

### Problem

ISP ONT restrictions prevent inbound port forwarding, blocking traditional VPN hosting.

### Solution

**Tailscale mesh VPN** was implemented to enable secure remote access without requiring router configuration.

Key properties:

* Outbound-only connections
* Encrypted peer-to-peer mesh
* Stable, private IP addressing

### Implementation

**Date:** February 9, 2025

#### Tailscale Installation (Ubuntu Server VM)

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
tailscale ip -4
```

* Authentication performed via browser on host machine
* Assigned IP: `100.x.x.x`

#### Client Setup

* Tailscale installed on mobile devices
* Authenticated under the same account
* Connectivity verified ("connection refused" confirms network path is functional)

**Status:** ✅ Mesh network operational

---

## Storage Architecture

Audiobooks are stored on the host machine’s **512 GB SSD** to avoid duplication and maintain a single source of truth.

### VirtualBox Shared Folder

**Host Configuration (GUI):**

* Folder path: `~/audiobooks`
* Folder name: `audiobooks`
* Mount point: `/mnt/audiobooks`
* Auto-mount: enabled
* Read-only: disabled

**Guest Configuration (Ubuntu Server VM):**

```bash
lsmod | grep vboxguest
sudo mkdir -p /mnt/audiobooks
sudo mount -t vboxsf audiobooks /mnt/audiobooks
ls -la /mnt/audiobooks
```

### Persistence

```bash
sudo nano /etc/fstab

audiobooks  /mnt/audiobooks  vboxsf  defaults,uid=1000,gid=1000  0  0
```

**Result:**

* Files stored once on host
* Instantly accessible to VM
* No duplication or sync overhead

---

## Audiobookshelf Deployment

### Docker Deployment

```bash
mkdir -p ~/audiobookshelf/config ~/audiobookshelf/metadata

docker run -d \
  --name audiobookshelf \
  --restart unless-stopped \
  -p 13378:80 \
  -v /mnt/audiobooks:/audiobooks \
  -v ~/audiobookshelf/config:/config \
  -v ~/audiobookshelf/metadata:/metadata \
  ghcr.io/advplyr/audiobookshelf:latest
```

### Initial Setup

* Accessed via: `http://100.x.x.x:13378`
* Admin account created
* Audiobooks library added at `/audiobooks`
* Metadata fetched automatically

### Mobile App

* Audiobookshelf app installed
* Server added via Tailscale IP
* Remote playback verified

**Status:** ✅ Service operational

---

## Architecture Overview

```
[Mobile Device + Tailscale]
        ↓
[Ubuntu Server VM (100.x.x.x)]
        ↓
[Docker: Audiobookshelf]
        ↓
[/mnt/audiobooks (vboxsf)]
        ↓
[Host PC – 5.5 TB HDD]
```

---

## Key Design Decisions

1. **Tailscale over traditional VPN** – no port forwarding, NAT-friendly
2. **Shared folders over file duplication** – single source of truth
3. **Dockerized services** – isolation, portability, easy updates

---

## Current Limitations

* VM depends on host uptime
* Tailscale required on clients
* No HTTPS (acceptable due to encrypted tunnel)

---

## Future Improvements

* Migrate to dedicated 24/7 hardware
* Add reverse proxy with HTTPS
* Automate library rescans

---

## Lessons Learned

* VirtualBox auto-mount is unreliable → `/etc/fstab` required
* Guest Additions are mandatory for shared folders
* Docker volume paths must be absolute
* Outbound-only VPNs are ideal for ISP-restricted networks

---

## Status: Phase 4 Complete ✅

* Tailscale operational
* Shared storage mounted
* Audiobookshelf deployed
* Remote access verified
