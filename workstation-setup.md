# Workstation Setup

This document describes the host machine and VM configuration that powers the homelab. It serves as the foundation for all virtualization, networking, and self-hosted services documented in this repository.

---

## Host Hardware

| Component | Spec |
|-----------|------|
| CPU | Ryzen 7 3700X |
| RAM | 32 GB DDR4 |
| GPU | RTX 2060 Super |
| OS Disk | 500 GB NVMe SSD — OS, dev tools, virtual machines |
| Data Disk | 5.5 TB HDD — bulk data and shared storage for VMs |

**Operating System:** Ubuntu 25.10 (Desktop), clean Linux-only install.

---

## Virtual Machine

All homelab services run inside a VirtualBox VM on the host. The VM uses a bridged network adapter so it appears as a first-class host on the LAN — this is required for Tailscale and direct service access.

| Setting | Value |
|---------|-------|
| OS | Ubuntu Server 24.04.4 LTS |
| RAM | 7 GB |
| CPU Cores | 4 |
| Disk | 25 GB (virtual disk on NVMe SSD) |
| Network Adapter | Bridged |
| Hypervisor | VirtualBox |

### Why these specs?
- **7 GB RAM** — leaves headroom for the host on 32 GB total while comfortably running multiple Docker containers
- **4 cores** — enough for concurrent services without starving the host
- **25 GB disk** — sufficient for OS + Docker images; bulk data lives on the host HDD via VirtualBox shared folders
- **Bridged networking** — mandatory for Tailscale mesh VPN and LAN-accessible services

---

## Storage Model

Bulk data (audiobooks, music, etc.) stays on the **host HDD** as a single source of truth. The VM accesses it via VirtualBox shared folders mounted at boot — no duplication, no sync overhead.

See individual project docs for specific mount configurations.

---

## Software Stack (Host)

| Category | Tools |
|----------|-------|
| Development | VS Code, IntelliJ, git, build-essential |
| Virtualization | VirtualBox, Docker |
| Networking | Wireshark, Cisco Packet Tracer |

---

## Known Issues & Fixes

| Issue | Fix |
|-------|-----|
| VirtualBox shared folders not persisting after reboot | Add entry to `/etc/fstab` inside the VM — auto-mount in VirtualBox GUI is unreliable |
| Docker can't pull images (DNS failure in VM) | Add `nameservers: [8.8.8.8, 1.1.1.1]` to `/etc/netplan/50-cloud-init.yaml` and run `sudo netplan apply` |
| Tailscale DNS errors after VM reboot | Run `sudo tailscale up --accept-dns=false` to stop Tailscale from overriding system DNS |

---

## Constraints

- Single-machine setup — VM uptime depends on host uptime
- No dedicated always-on hardware (yet)
- ISP-provided ONT blocks inbound connections — all remote access is outbound-only via Tailscale

---

## Scope

This document covers the host machine and VM only. All service deployments, networking decisions, and architecture details are documented in their respective project files.
