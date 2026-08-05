# OPNsense — Virtual Firewall/Router

**What:** OPNsense 26.7 running as a VM inside Proxmox, acting as the firewall and router between network zones.
**Why:** Network segmentation — isolate Services from Lab, control what traffic flows where, filter DNS through Pi-hole for all clients.
**Where:** VM 102 on Proxmox, 3 virtual NICs spanning all zones.

---

## Architecture

OPNsense sits between the ISP router and all internal zones. It does not replace the ISP router — it sits behind it on the same subnet and routes traffic between internal virtual networks.

```
ISP Router (192.168.100.1)
    │
    └── vmbr0 (192.168.100.0/24) — WAN/Users
        ├── Proxmox host (.10)
        ├── Desktop/Laptop (DHCP)
        │
        └── OPNsense WAN (.2)
            │
            ├── vmbr1 — Services (10.10.20.0/24)
            │   ├── OPNsense LAN (.1)
            │   ├── Docker VM (.50)
            │   └── Pi-hole LXC (.53)
            │
            └── vmbr2 — Lab (10.10.30.0/24)
                ├── OPNsense Lab (.1)
                └── Future SOC lab VMs
```

---

## VM Specs

| Setting | Value |
|---------|-------|
| VM ID | 102 |
| OS | OPNsense 26.7 |
| CPU | 1 core (type: host) |
| RAM | 2 GB |
| Disk | 16 GB VirtIO |
| Boot order | 1 (starts before all other VMs/CTs) |

### Network Interfaces

| Interface | Bridge | Zone | IP |
|-----------|--------|------|----|
| vtnet0 (WAN) | vmbr0 | WAN/Users | `192.168.100.2/24` |
| vtnet1 (LAN) | vmbr1 | Services | `10.10.20.1/24` |
| vtnet2 (Lab) | vmbr2 | Lab | `10.10.30.1/24` |

WAN gateway: `192.168.100.1` (ISP router)

---

## Key Configuration Decisions

### WAN interface settings
- **"Block private networks"** — unchecked. WAN IS a private network (`192.168.100.0/24`), blocking private nets would block everything.
- **"Block bogon networks"** — unchecked. Same reason.
- **"Disable reply-to on WAN rules"** — checked (Firewall → Settings → Advanced). Required because the desktop/laptop and OPNsense WAN are on the same subnet — without this, OPNsense sends reply packets through the gateway instead of directly back to the client.

### NAT
- **Outbound NAT:** Automatic. Covers LAN (Services) and Lab networks. Traffic from both zones gets NAT'd through the WAN interface to reach the internet.

### DNS
- **System → Settings → General:** DNS server set to `10.10.20.53` (Pi-hole). "Allow DNS override by DHCP/PPP on WAN" unchecked.
- **Services → Unbound DNS:** Enabled on all interfaces. Forwarding mode enabled — Unbound forwards to system nameservers (Pi-hole) instead of resolving recursively.
- **Router DHCP** pushes `192.168.100.2` (OPNsense) as primary DNS to all clients. Chain: device → router → OPNsense (Unbound) → Pi-hole → Cloudflare.

---

## Firewall Rules

### WAN Rules
| Action | Source | Destination | Port | Description |
|--------|--------|-------------|------|-------------|
| Pass | `192.168.100.0/24` | WAN address | HTTPS (443) | Allow LAN access to OPNsense web UI |
| Pass | `192.168.100.0/24` | WAN address | DNS (53) | Allow DNS to OPNsense |
| Pass | `192.168.100.0/24` | LAN network | any | Allow Users to Services zone |

> ⚠️ **TODO:** The "Allow Users to Services zone" rule currently allows `any` protocol. Should be tightened to specific ports only (22, 53, 80, 81, 443, 3001, 7575, 9443).

### LAN (Services) Rules
Default OPNsense rules: allow all outbound from LAN network. Services zone can reach the internet through NAT.

### Lab Rules
| Action | Source | Destination | Port | Description |
|--------|--------|-------------|------|-------------|
| Block | Lab network | LAN network | any | Block Lab from Services zone |
| Pass | Lab network | any | any | Allow Lab outbound |

Rule order matters — block rule is above the pass rule. Lab can reach the internet but cannot touch the Services zone.

> ⚠️ **TODO:** Lab isolation is configured but not yet tested with a real VM on vmbr2.

---

## Accessing OPNsense

- **Web UI:** `https://192.168.100.2` from any device on `192.168.100.0/24`
- **Console:** Proxmox web UI → VM 102 → Console
- **Shell:** Console menu option 8, or SSH (if enabled)

---

## Troubleshooting Notes

### WAN IP kept reverting to DHCP
During initial setup, OPNsense's WAN interface kept getting a DHCP address (`.67`) despite the GUI showing static `.2`. Root cause: a DHCP client was running from the initial boot config and overriding the static assignment. Fix: `killall dhclient` + reboot with saved config.

### Web UI unreachable with firewall enabled
Required two fixes: (1) uncheck "Block private networks" on WAN, (2) check "Disable reply-to on WAN rules" in Advanced settings. Without the reply-to fix, OPNsense routes reply packets through the gateway instead of directly back to the requesting client on the same subnet.

### NFS hang causing system freeze
The NFS backup mount (`desktopbackup`) was configured with `hard` mount mode (default). When the desktop was off, any process touching the mount path hung indefinitely, eventually freezing Proxmox completely. Fixed by changing fstab to `soft,timeo=50,retrans=3,_netdev,nofail`.

---

## History

### 2026-08 — Deployment
OPNsense 26.7 deployed as VM 102 with 3 NICs. WAN on vmbr0, Services on vmbr1, Lab on vmbr2. Docker VM and Pi-hole LXC migrated from flat `192.168.100.0/24` to Services zone `10.10.20.0/24`. DNS chain reconfigured through OPNsense Unbound forwarding to Pi-hole. Lab zone created with isolation rules.
