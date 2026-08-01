# Infrastructure Setup

This document describes the hardware and virtualization platform that powers the homelab. It replaces the previous VirtualBox-on-desktop setup, which was decommissioned in July 2026 when the lab migrated to dedicated hardware.

---

## Proxmox Host — Beelink ME Mini

The homelab runs on a dedicated mini PC running Proxmox VE bare-metal. This replaced a VirtualBox VM on the desktop — the key upgrade being always-on capability (within household power rules) and a proper hypervisor instead of a desktop-grade VM manager.

| Component | Spec |
|-----------|------|
| Model | Beelink ME Mini |
| CPU | Intel N150 (4 cores, 4 threads, up to 3.6GHz burst) |
| RAM | 16 GB LPDDR5 (soldered) |
| Storage | 1 TB NVMe SSD (single drive, boot + VM storage) |
| Network | 2x Intel i226-V 2.5GbE (one for management, one reserved for pfSense NIC passthrough) |
| WiFi | WiFi 6 (disabled — everything wired) |
| Hypervisor | Proxmox VE 9.2 |
| Host IP | `192.168.100.10` |
| Web UI | `https://192.168.100.10:8006` |
| SSH | `ssh admin@192.168.100.10` (key-only, password auth disabled) |

### Why this hardware

- **Low power draw** — critical household constraint. Mother has strict power/fire-safety rules: nothing stays plugged in when unused, power strip unplugged for 2+ week trips. The Beelink's low idle wattage and real fan-based cooling satisfied this constraint.
- **Dual 2.5GbE** — one NIC for management/services, one reserved for PCI passthrough to a future pfSense VM.
- **New with warranty** — 3-year warranty. Used enterprise SFF PCs were ruled out due to fan noise, unknown condition, and no real warranty.
- **VT-x and VT-d confirmed** — both enabled in BIOS and at kernel level (`intel_iommu=on` in GRUB). Required for VM virtualization and NIC passthrough respectively.

### Proxmox configuration

- **Repos:** Enterprise repo disabled (no subscription). Using `pve-no-subscription` repo + standard Debian bookworm repos. `.sources` format (Proxmox 9.2 uses deb822, not traditional `.list`).
- **Storage:** `local` (ISO images, CT templates) and `local-lvm` (VM disks, CT volumes) on the 1TB NVMe.
- **SSH hardened:** key-only auth, root login disabled, fail2ban (24h bans), UFW (ports 22 and 8006 only).
- **Non-root user:** `admin` with sudo, created post-install (Proxmox ships root-only by default).

---

## VM 100 — Docker Host

All Docker-based services run inside this VM, migrated from the old VirtualBox setup via volume export/import.

| Setting | Value |
|---------|-------|
| OS | Ubuntu Server 24.04.4 LTS |
| CPU | 2 cores (type: host) |
| RAM | 7 GB (7168 MB) |
| Disk | 200 GB VirtIO Block on local-lvm |
| Network | VirtIO on vmbr0 |
| IP | `192.168.100.50` (static via netplan) |
| SSH | `ssh strma@192.168.100.50` (key-only, password auth disabled) |
| Guest Agent | qemu-guest-agent installed — Proxmox reports VM IP, enables clean shutdown |

### Why these specs
- **2 cores** — sufficient for 5 Docker containers without starving Proxmox or future VMs
- **7 GB RAM** — leaves headroom for Proxmox overhead, Pi-hole LXC, and a future pfSense VM on a 16GB host
- **200 GB disk** — enough for OS + Docker images + volume data. Bulk media stays external.
- **Static IP at `.50`** — deliberately took over the old VM's address so existing bookmarks, DNS entries, and firewall rules carry forward without changes

### SSH hardened
- Key-only auth, password disabled, root login disabled
- fail2ban (24h bans, LAN + Tailscale whitelisted)
- UFW default-deny inbound with per-service port allowlist (22, 53, 80, 81, 443, 3001, 7575, 8888, 9000, 9443)

---

## CT 101 — Pi-hole LXC

DNS runs in a dedicated LXC container, separated from the Docker stack. This means DNS survives Docker VM reboots/maintenance independently — a lesson from Phase 0 where Pi-hole going down with the Docker VM took DNS with it.

| Setting | Value |
|---------|-------|
| OS | Ubuntu 24.04 (standard CT template) |
| CPU | 1 core |
| RAM | 512 MB |
| Disk | 8 GB |
| IP | `192.168.100.53` (static) |
| Web UI | `http://192.168.100.53/admin` |
| Role | Network-wide DNS + ad-blocking for entire LAN |

Router DHCP is configured to push `192.168.100.53` as primary DNS to all devices.

---

## Sandbox Box — i5-3470 Desktop

Secondary machine for disposable lab work — CCNA practice, GNS3/EVE-NG, pentest sandboxing. Fully separate from the production Beelink by design. If it dies or gets nuked, nothing in production breaks.

| Component | Spec |
|-----------|------|
| CPU | Intel i5-3470 (Ivy Bridge, 4 cores) |
| Board | Asus P8H61-I (mini-ITX, H61 chipset) |
| RAM | 8 GB DDR3 (2x4GB, max supported 16GB) |
| Storage | None installed — awaiting SSD purchase |
| PSU | Tracens Radix Eco 400W (no-name, not trusted for unattended use) |
| Case | Thermaltake (mini tower) |
| Cost | €35 total |
| VT-x | Confirmed enabled in BIOS |

**Operational constraint:** PSU is not trusted for unattended operation. This box only runs while actively working on it — never left on overnight or when the house is empty. This is deliberate and consistent with the household power/safety rules.

---

## Desktop PC (development workstation)

The desktop is no longer the hypervisor host (that role moved to the Beelink). It's now purely a development/management workstation.

| Component | Spec |
|-----------|------|
| CPU | AMD Ryzen 7 3700X |
| RAM | 32 GB DDR4-3200 |
| GPU | RTX 2060 Super |
| OS Disk | 500 GB NVMe SSD |
| Data Disk | 5.5 TB HDD |
| OS | Ubuntu 25.10 |

Used for: SSH into Proxmox/VMs, browser access to service UIs, code editing, Git workflow, Packet Tracer/GNS3 client.

---

## Network Overview

All devices sit on the `192.168.100.0/24` subnet behind the ISP router. The Beelink plugs into the ISP router/switch — it does not replace it. Household WiFi and other devices are unaffected by homelab maintenance.

| Device | IP | Role |
|--------|----|------|
| ISP Router | `192.168.100.1` | Gateway, DHCP (DNS overridden to Pi-hole), WiFi AP |
| Proxmox Host | `192.168.100.10` | Hypervisor management |
| Docker VM | `192.168.100.50` | All Docker services |
| Pi-hole LXC | `192.168.100.53` | Network-wide DNS |
| Desktop | DHCP (`.132` typical) | Development workstation |

**Future:** pfSense VM will eventually create proper Management/Services/Lab zone separation via VLANs. Currently everything is flat on one subnet — functional but not segmented.

---

## SSH Access

SSH config on desktop and laptop (`~/.ssh/config`):

```
Host pve
    HostName 192.168.100.10
    User admin

Host docker
    HostName 192.168.100.50
    User strma
```

Usage: `ssh pve` or `ssh docker`. Key-based auth only on both targets.

---

## Constraints

- Single Proxmox host — all VMs/CTs share one machine's resources
- ISP-provided ONT blocks inbound connections — all remote access is outbound-only via Tailscale
- Household power rules — Beelink is the one exception allowed to stay on; sandbox box is session-only
- 16 GB total RAM shared across Proxmox overhead + all VMs + all CTs
