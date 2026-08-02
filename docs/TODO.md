# Homelab TODO

## Current Phase: Phase 1 — Infrastructure Migration (one exit checkpoint remaining)

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
- [x] Install Docker on the VM, set static IP `192.168.100.50`
- [x] Migrate all 6 Docker services from old Ubuntu Server VM (volume export/import)
- [x] Fix Homarr — migrated from `ajnart/homarr` to `ghcr.io/homarr-labs/homarr:latest` (new image, different volume paths, requires `SECRET_ENCRYPTION_KEY`, listens on port 3000 not 7575)
- [x] Fix Portainer — fresh volume, new admin account
- [x] SSH hardening on Docker VM — key-only auth, fail2ban, UFW (ports 22, 80, 81, 443, 3001, 7575, 8888, 9000, 9443, 53)
- [x] Install qemu-guest-agent on Docker VM
- [x] Rebuild Uptime Kuma monitors for new architecture (8 monitors: all services + Proxmox + DNS)
- [x] Rebuild Homarr dashboard with service tiles
- [x] Set up SSH config aliases (`pve`, `docker`) on desktop and laptop
- [x] Deploy Pi-hole as LXC container (CT 101) at `192.168.100.53`
- [x] Configure router DNS to point to Pi-hole LXC
- [x] Remove old Pi-hole Docker container and volumes
- [x] Decommission old Ubuntu Server VM (VirtualBox)
- [x] Sandbox box (i5-3470) — purchased (€35), tested POST, verified VT-x in BIOS, Proxmox USB installer boots. Needs SSD purchase before Proxmox can install.
- [x] Repo documentation sync — README, workstation-setup.md, compose files, Homarr docs all updated to reflect Proxmox reality
- [x] Learn Proxmox snapshots — created, restored, verified rollback, deleted. Full lifecycle tested.
- [x] Configure Proxmox storage — NFS share from desktop HDD (1.3TB available) mounted as directory storage (`desktopbackup`) on Proxmox
- [x] Create VM templates — Ubuntu 24.04 template at VM 900, clone tested with machine-id and SSH host key regeneration verified
- [x] Set up automated Proxmox backups — daily schedule to `desktopbackup` storage, ZSTD compression, 3-backup retention. VM 100 (4.13GB) and CT 101 (307MB) both tested successfully. Note: backups require desktop to be powered on (NFS share dependency).

## Phase 1 — In Progress

- [ ] **Update network topology diagram** — current diagram needs to show Proxmox host, Docker VM, Pi-hole LXC, sandbox box, NFS backup path to desktop. Last gate before Phase 1 closes.

## Phase 1 — Exit Checkpoints

- [x] Can spin up a new VM from template in under 5 minutes
- [x] All previous services running inside Proxmox, nothing left on bare Ubuntu/VirtualBox
- [x] Can recover a failed VM from snapshot or backup
- [ ] Network topology diagram is accurate and up to date
- [x] Repo documentation matches live infrastructure (no Phase 0 claims remaining)
- [x] You think in VMs/containers, not in "apps on my computer"

---

## Phase 1 — Parked (do later, don't let jump the queue)

- [ ] pfSense/OPNsense VM — network segmentation into Management/Services/Lab zones. NIC passthrough ready (IOMMU confirmed). Separate day, clear head.
- [ ] Sandbox box — needs SSD purchase before Proxmox can install. RAM upgrade optional (2x8GB matched pair if upgrading, not mixed sticks).
- [ ] Tailscale setup on new Docker VM — for remote access outside home network
- [ ] SOC lab migration into Proxmox — renumber subnet from `192.168.100.0/24` to `10.10.10.0/24` first (current `.10` address collides with Proxmox host)
- [ ] WireGuard — still deferred, Tailscale still covers the use case
- [ ] Localhost-bind refactor for remaining services (Uptime Kuma, Homarr) — admin tools intentionally left directly accessible

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
