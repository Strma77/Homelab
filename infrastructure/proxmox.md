# Proxmox VE Host — Beelink ME Mini

**What:** The bare-metal hypervisor the whole homelab runs on.
**Why:** Single always-on node. Every VM/CT (OPNsense, Docker host, Pi-hole) lives here.
**Where:** `192.168.100.10` on the WAN/Users segment. Web UI `https://192.168.100.10:8006`, SSH `ssh pve` (`admin@192.168.100.10`).

> This doc exists because the PVE host's config lives on the box, **not in Git**. The backup cron that died in June died precisely because host-level state wasn't documented or version-controlled. Anything here that isn't in a guest disk gets written down here so a rebuild is copy-paste, not archaeology.

---

## Hardware

| Component | Spec |
|-----------|------|
| Model | Beelink ME Mini |
| CPU | Intel N150 (4C/4T) |
| RAM | 16 GB LPDDR5 (soldered) |
| Storage | 1 TB NVMe |
| Network | 2x Intel i226-V 2.5GbE |
| Hypervisor | Proxmox VE 9.2 |

- VT-x / VT-d (IOMMU) enabled in BIOS; `intel_iommu=on` in GRUB.
- Repos: enterprise disabled, `pve-no-subscription` added (deb822 `.sources` format).
- SSH hardened: key-only, root login disabled, fail2ban, UFW (22, 8006). See `security/vm-hardening.md`.

## Bridges

| Bridge | Subnet | Zone | Backing |
|--------|--------|------|---------|
| vmbr0 | `192.168.100.0/24` | WAN/Users | physical NIC |
| vmbr1 | `10.10.20.0/24` | Services | virtual |
| vmbr2 | `10.10.30.0/24` | Lab | virtual |

## Guests + boot order

| VMID | Name | Type | IP | Boot |
|------|------|------|----|----|
| 102 | opnsense | VM | `192.168.100.2` / `10.10.20.1` / `10.10.30.1` | 1 |
| 101 | pihole | LXC | `10.10.20.53` | 2 |
| 100 | docker-host | VM | `10.10.20.50` | 3 |
| 900 | ubuntu-2404-template | template | — | don't start |

---

## Storage

Inspect: `sudo pvesm status` and `sudo cat /etc/pve/storage.cfg`.

| ID | Type | Path / target | Content |
|----|------|---------------|---------|
| `local` | dir | `/var/lib/vz` | iso, vztmpl, backup |
| `local-lvm` | lvmthin | `pve/data` | VM/CT disks |
| `desktopbackup` | **nfs** | `192.168.100.132:/mnt/hdd/vm-backups/proxmox` -> `/mnt/pve/desktopbackup` | backup, iso |

`desktopbackup` was converted from `dir` to native `nfs` type on 2026-09-06 so PVE owns the mount (no fstab fight, clean fail when the desktop is off). Full detail in `scripts/backups.md`.

---

## Backups + notifications

Daily `vzdump` job (21:00, zstd, keep-last=3, VMIDs 100/101/102) -> `desktopbackup`, with ntfy push alerts. This is the entire backup system — see **`scripts/backups.md`** for the job config, ntfy webhook/matcher setup, retention caveats, and restore procedure.

Key host-side files (not in Git, documented here):
- `/etc/pve/jobs.cfg` — the vzdump job
- `/etc/pve/storage.cfg` — storage definitions
- `/etc/pve/notifications.cfg` + `/etc/pve/priv/notifications.cfg` — ntfy webhook target (public + private halves)

---

## Known noise / gotchas

- **Locale warning spam** on `admin@pve` (`perl: warning: Setting locale failed ... en_GB.UTF-8`) — harmless, the `LC_*` vars are set to `en_GB` but the locale isn't generated. Silence with `sudo locale-gen en_GB.UTF-8 && sudo update-locale`. Cosmetic only.
- `pvesm`/`vzdump` live in `/usr/sbin` — run with `sudo` (the `admin` user's PATH may not include sbin), or `command not found` will mislead you into thinking Proxmox tooling is missing.

---

## History

### 2026-09-06 — Backup stack repaired + documented
Converted `desktopbackup` to native NFS, added OPNsense to the vzdump set, wired ntfy notifications, created this doc to stop host-level config from living only on the box.

### 2026-08 — Host stood up
Proxmox 9.2 installed on the Beelink. OPNsense, Docker VM, Pi-hole LXC deployed across three bridges. Network segmentation live.
