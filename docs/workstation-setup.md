# Infrastructure Setup

This document describes the hardware, virtualization platform, and network architecture that powers the homelab.

---

## Proxmox Host — Beelink ME Mini

| Component | Spec |
|-----------|------|
| Model | Beelink ME Mini |
| CPU | Intel N150 (4C/4T, up to 3.6GHz burst) |
| RAM | 16 GB LPDDR5 (soldered) |
| Storage | 1 TB NVMe SSD |
| Network | 2x Intel i226-V 2.5GbE |
| Hypervisor | Proxmox VE 9.2 |
| Host IP | `192.168.100.10` (vmbr0) |
| Web UI | `https://192.168.100.10:8006` |
| SSH | `ssh pve` → `admin@192.168.100.10` |

### Proxmox configuration
- Repos: `pve-no-subscription` + Debian bookworm (`.sources` deb822 format)
- Storage: `local` (ISOs, templates), `local-lvm` (VM/CT disks), `desktopbackup` (NFS from desktop HDD)
- Bridges: `vmbr0` (physical NIC, WAN/Users), `vmbr1` (virtual, Services), `vmbr2` (virtual, Lab)
- SSH hardened: key-only, fail2ban, UFW (22, 8006)
- IOMMU: enabled (`intel_iommu=on` in GRUB)

### Backup storage
NFS share from desktop HDD (NTFS, sda3 "Glavni", 1.3TB free) mounted as directory storage `desktopbackup`. fstab uses `soft,timeo=50,retrans=3,_netdev,nofail` to prevent system hang when desktop is off. Daily automated backups with ZSTD compression, 3-backup retention.

---

## VM 102 — OPNsense (Firewall/Router)

| Setting | Value |
|---------|-------|
| OS | OPNsense 26.7 (FreeBSD-based) |
| CPU | 1 core (type: host) |
| RAM | 2 GB |
| Disk | 16 GB VirtIO |
| NICs | vtnet0 (vmbr0/WAN), vtnet1 (vmbr1/Services), vtnet2 (vmbr2/Lab) |
| WAN IP | `192.168.100.2/24`, gateway `192.168.100.1` |
| LAN IP | `10.10.20.1/24` (Services zone gateway) |
| Lab IP | `10.10.30.1/24` (Lab zone gateway) |
| Web UI | `https://192.168.100.2` |
| Boot order | 1 (starts first) |

### Key configuration
- "Block private networks" and "Block bogon networks" unchecked on WAN (WAN IS a private network)
- "Disable reply-to on WAN rules" checked (required because desktop and WAN are same subnet)
- Outbound NAT: automatic (covers LAN and Lab networks)
- DNS: Unbound enabled on all interfaces, forwarding mode, forwards to Pi-hole (`10.10.20.53`)
- Router DHCP pushes `192.168.100.2` as primary DNS to all clients

→ [infrastructure/opnsense.md](../infrastructure/opnsense.md)

---

## VM 100 — Docker Host

| Setting | Value |
|---------|-------|
| OS | Ubuntu Server 24.04.4 LTS |
| CPU | 2 cores (type: host) |
| RAM | 7 GB (7168 MB) |
| Disk | 200 GB VirtIO Block |
| Network | VirtIO on vmbr1 (Services zone) |
| IP | `10.10.20.50/24`, gateway `10.10.20.1` |
| SSH | `ssh docker` → `strma@10.10.20.50` |
| Guest Agent | qemu-guest-agent installed |
| Boot order | 3 |

SSH hardened: key-only, fail2ban, UFW (22, 53, 80, 81, 443, 3001, 7575, 8888, 9000, 9443)

---

## CT 101 — Pi-hole LXC

| Setting | Value |
|---------|-------|
| OS | Ubuntu 24.04 |
| CPU | 1 core |
| RAM | 512 MB |
| Disk | 8 GB |
| Network | vmbr1 (Services zone) |
| IP | `10.10.20.53/24`, gateway `10.10.20.1` |
| Web UI | `http://10.10.20.53/admin` |
| Boot order | 2 |

DNS chain: devices → router (`192.168.100.1`) → OPNsense (`192.168.100.2`, Unbound) → Pi-hole (`10.10.20.53`) → Cloudflare (`1.1.1.1`)

---

## VM 900 — Ubuntu 24.04 Template

Clean Ubuntu Server 24.04 with qemu-guest-agent, curl, git pre-installed. Machine-id truncated and SSH host keys removed for clean cloning. Clone and customize, don't start directly.

---

## Sandbox Box — i5-3470 Desktop

| Component | Spec |
|-----------|------|
| CPU | Intel i5-3470 (Ivy Bridge, 4 cores) |
| Board | Asus P8H61-I (mini-ITX, H61) |
| RAM | 8 GB DDR3 (2x4GB) |
| Storage | None — awaiting SSD |
| PSU | Tracens Radix Eco 400W (not trusted unattended) |
| Cost | €35 |
| VT-x | Confirmed |

Session-only use. Fully separate from production by design.

---

## Desktop PC

| Component | Spec |
|-----------|------|
| CPU | AMD Ryzen 7 3700X |
| RAM | 32 GB DDR4-3200 |
| GPU | RTX 2060 Super |
| OS Disk | 500 GB NVMe |
| Data Disk | 5.5 TB HDD (NFS backup source) |
| OS | Ubuntu 25.10 |

Development/management workstation. SSH into Proxmox/VMs, browser access to services, Git workflow.

---

## Network Architecture

```
Living room                    WiFi                     Your room
┌──────────┐                                    ┌──────────┐
│ ISP      │ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~────── │ ZTE      │
│ Router   │                                    │ Wireless │
│ (.1)     │                                    │ Bridge   │
│ DHCP DNS │                                    ├──────────┤
│ →.2      │                                    │ Port 1 → Desktop
└──────────┘                                    │ Port 2 → Beelink NIC1
                                                │ Port 3 → free (sandbox)
                                                └──────────┘
```

### IP Allocation

| Device | IP | Zone | Bridge |
|--------|----|------|--------|
| ISP Router | `192.168.100.1` | WAN | — |
| OPNsense WAN | `192.168.100.2` | WAN | vmbr0 |
| Proxmox Host | `192.168.100.10` | WAN | vmbr0 |
| Desktop | DHCP | WAN | — |
| Laptop | DHCP | WAN | — |
| OPNsense LAN | `10.10.20.1` | Services | vmbr1 |
| Docker VM | `10.10.20.50` | Services | vmbr1 |
| Pi-hole LXC | `10.10.20.53` | Services | vmbr1 |
| OPNsense Lab | `10.10.30.1` | Lab | vmbr2 |

### Firewall Rules Summary

| From → To | Services | Lab | WAN/Internet |
|-----------|----------|-----|--------------|
| WAN/Users | ✅ specific ports + DNS | ❌ blocked | ✅ direct |
| Services | — | ❌ blocked | ✅ via OPNsense NAT |
| Lab | ❌ blocked | — | ✅ via OPNsense NAT |

### Client Access

Desktop and laptop need persistent static routes to reach Services and Lab zones:
```bash
# Added via NetworkManager, survives reboots:
nmcli connection modify "CONNECTION_NAME" +ipv4.routes "10.10.20.0/24 192.168.100.2"
nmcli connection modify "CONNECTION_NAME" +ipv4.routes "10.10.30.0/24 192.168.100.2"
```

### SSH Config (`~/.ssh/config`)
```
Host pve
    HostName 192.168.100.10
    User admin

Host docker
    HostName 10.10.20.50
    User strma
```

---

## Constraints

- Single Proxmox host — all VMs/CTs share 16GB RAM
- ISP router is unmanaged — no VLAN tagging at the physical level, all segmentation is virtual inside Proxmox
- ZTE wireless bridge connects room to router via WiFi — all homelab traffic traverses this link
- Backup storage requires desktop to be powered on (NFS dependency)
- Household power rules — Beelink stays on, sandbox is session-only
