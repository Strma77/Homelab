# Homelab TODO

## Current Phase: Phase 1 — Infrastructure Migration (two exit checkpoints remaining)

---

## Phase 1 — Completed

- [x] Purchase and receive Beelink ME Mini (N150, 16GB RAM, 1TB NVMe)
- [x] Wipe Windows, install Proxmox VE 9.2 on Beelink
- [x] Verify VT-x and VT-d (IOMMU) enabled in BIOS
- [x] Enable `intel_iommu=on` at kernel level (GRUB)
- [x] Fix Proxmox repos (disable enterprise, add no-subscription, fix Signed-By for .sources format)
- [x] Create non-root user (`admin`) on Proxmox host, install sudo
- [x] SSH hardening on Proxmox host — key-only auth, fail2ban, UFW (ports 22, 8006)
- [x] Create Docker VM (VM 100, Ubuntu 24.04.4, 2 cores, 7GB RAM, 200GB disk)
- [x] Install Docker on the VM
- [x] Migrate all 6 Docker services from old Ubuntu Server VM (volume export/import)
- [x] Fix Homarr — migrated from `ajnart/homarr` to `ghcr.io/homarr-labs/homarr:latest`
- [x] Fix Portainer — fresh volume, new admin account
- [x] SSH hardening on Docker VM — key-only auth, fail2ban, UFW
- [x] Install qemu-guest-agent on Docker VM
- [x] Rebuild Uptime Kuma monitors and Homarr dashboard
- [x] Set up SSH config aliases (`pve`, `docker`) on desktop and laptop
- [x] Deploy Pi-hole as LXC container (CT 101)
- [x] Remove old Pi-hole Docker container and volumes
- [x] Decommission old Ubuntu Server VM (VirtualBox)
- [x] Sandbox box (i5-3470) — purchased (€35), tested POST, verified VT-x. Needs SSD.
- [x] Repo documentation sync — README, workstation-setup.md, compose files updated
- [x] Learn Proxmox snapshots — full lifecycle tested (create, restore, delete)
- [x] Configure Proxmox storage — NFS share from desktop HDD mounted as `desktopbackup` with soft mount options
- [x] Create VM templates — Ubuntu 24.04 template at VM 900, clone tested
- [x] Set up automated Proxmox backups — daily ZSTD, 3-backup retention, tested
- [x] Deploy OPNsense VM (VM 102) — 3 NICs: WAN (vmbr0), Services (vmbr1), Lab (vmbr2)
- [x] Configure OPNsense interfaces — WAN `192.168.100.2/24`, LAN `10.10.20.1/24`, Lab `10.10.30.1/24`
- [x] Configure OPNsense firewall — WAN web UI access, WAN DNS, WAN→Services pass, Lab→Services block, Lab outbound pass
- [x] Configure OPNsense DNS forwarding — Unbound forwards to Pi-hole via system nameserver
- [x] Migrate Docker VM to Services zone — NIC changed to vmbr1, IP `10.10.20.50/24`, gateway `10.10.20.1`
- [x] Migrate Pi-hole LXC to Services zone — NIC changed to vmbr1, IP `10.10.20.53/24`, gateway `10.10.20.1`
- [x] Update router DHCP to push OPNsense (`192.168.100.2`) as primary DNS
- [x] DNS chain verified: devices → router → OPNsense → Pi-hole → upstream (ad blocking confirmed)
- [x] Persistent static routes on desktop and laptop (`10.10.20.0/24` and `10.10.30.0/24` via `192.168.100.2`)
- [x] Update all Uptime Kuma monitors and Homarr tiles with new IPs
- [x] Update SSH config on desktop and laptop (Docker VM now at `10.10.20.50`)
- [x] Configure VM boot order — OPNsense (1), Pi-hole (2), Docker VM (3)
- [x] Fix NFS fstab — changed from `hard` to `soft,timeo=50,retrans=3,_netdev` to prevent system hang when desktop is off
- [x] Fix DHCP start range on router — changed from `.2` to `.3` to avoid IP conflict with OPNsense

## Phase 1 — In Progress

- [ ] **Tighten WAN→Services firewall rule** — currently allows `any` protocol from `192.168.100.0/24` to LAN network. Restrict to specific ports only (7575, 9443, 3001, 80, 81, 443, 53, 22).
- [ ] **Test Lab zone isolation** — spin up a VM on vmbr2 (Lab zone), verify it cannot reach Services zone (`10.10.20.0/24`). Block rule is configured but untested with real traffic.
- [ ] **Update network topology diagram** — must reflect OPNsense, three zones, DNS chain, NFS backup path.

## Phase 1 — Exit Checkpoints

- [x] Can spin up a new VM from template in under 5 minutes
- [ ] VLAN segmentation is working — lab traffic can't reach services traffic (rule configured, not tested)
- [x] All previous services running inside Proxmox, nothing left on bare Ubuntu/VirtualBox
- [x] Can recover a failed VM from snapshot or backup
- [ ] Network topology diagram is accurate and up to date
- [x] Repo documentation matches live infrastructure
- [x] You think in VMs/containers, not in "apps on my computer"

---

## Phase 1 — Parked

- [ ] Sandbox box — needs SSD purchase before Proxmox can install
- [ ] Tailscale setup on new Docker VM — for remote access outside home network
- [ ] SOC lab migration into Proxmox — use Lab zone (`10.10.30.0/24`)
- [ ] WireGuard — deferred, Tailscale covers the use case
- [ ] Localhost-bind refactor for remaining services (Uptime Kuma, Homarr)

---

## Backlog (Phase 2+)

- [ ] Prometheus + Grafana + Loki monitoring stack
- [ ] Ansible for VM provisioning
- [ ] Gitea self-hosted Git
- [ ] Expanded SOC lab with custom Wazuh rules
- [ ] Traefik (replaces NPM)
- [ ] Internal PKI (Step-CA)
- [ ] CI/CD with GitHub Actions or Gitea Actions
- [ ] Terraform for Proxmox
- [ ] Ollama + Open WebUI (AI integration)

---

## Cross-Cutting

- [ ] Document the GitOps workflow for the new Proxmox-based setup
- [ ] Decide on image pinning strategy (`:latest` on everything contradicts reproducibility claim)
