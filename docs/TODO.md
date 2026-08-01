# Homelab TODO

## Current Phase: Phase 1 — Infrastructure Migration (in progress)

### ⚠️ Documentation debt — owned, dated, scheduled

The following service runbooks were drafted with AI assistance during Phase 0 close-out (2026-06). All three need rewriting to reflect the Phase 1 migration (Proxmox, new images, new architecture):

- `services/uptime-kuma/UptimeKuma.md` — monitors rebuilt from scratch, old monitor table is wrong
- `services/portainer/Portainer.md` — minor updates needed (container count, setup context)
- `services/homarr/Homarr.md` — image changed from `ajnart/homarr` to `homarr-labs/homarr`, volumes restructured, port mapping changed

**Commitment:** rewrite each in my own voice by **2026-08-31**. Deadline is real — don't let Span shifts eat it.

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
- [x] Sandbox box (i5-3470) — purchased, tested POST, verified VT-x in BIOS, Proxmox USB boot tested

## Phase 1 — In Progress

- [ ] **Repo documentation sync** — README, workstation-setup.md, compose files, backup docs all still describe Phase 0/VirtualBox. Must reflect Proxmox reality before anything else.
- [ ] **Update network topology diagram** — V2 exists but README links V1. Diagram needs to show Proxmox host, Docker VM, Pi-hole LXC, sandbox box.

## Phase 1 — Next Up (in order)

- [ ] **Learn Proxmox snapshots** — take a snapshot of Docker VM before any further changes. Practice create, restore, delete.
- [ ] **Configure Proxmox storage** — understand local vs local-lvm. Add any available HDDs as directory storage for VM backups.
- [ ] **Create VM templates** — convert a clean Ubuntu Server install into a reusable template. Clone instead of reinstalling.
- [ ] **Set up automated Proxmox backups** — schedule nightly VM backups to HDD storage. Replaces the old Docker-level tar+cron backup with hypervisor-level backup.

## Phase 1 — Parked (do later, don't let jump the queue)

- [ ] pfSense/OPNsense VM — network segmentation into Management/Services/Lab zones. NIC passthrough ready (IOMMU confirmed). Separate day, clear head.
- [ ] Sandbox box — needs SSD purchase before Proxmox can install. RAM upgrade optional (2x8GB matched pair if upgrading, not mixed sticks).
- [ ] Tailscale setup on new Docker VM — for remote access outside home network
- [ ] SOC lab migration into Proxmox — renumber subnet from `192.168.100.0/24` to `10.10.10.0/24` first (current `.10` address collides with Proxmox host)
- [ ] WireGuard — still deferred, Tailscale still covers the use case
- [ ] Localhost-bind refactor for remaining services (Uptime Kuma, Homarr) — admin tools intentionally left directly accessible

## Phase 1 — Exit Checkpoints

- [ ] Can spin up a new VM from template in under 5 minutes
- [ ] All previous services running inside Proxmox, nothing left on bare Ubuntu/VirtualBox
- [ ] Can recover a failed VM from snapshot or backup
- [ ] Network topology diagram is accurate and up to date
- [ ] Repo documentation matches live infrastructure (no Phase 0 claims remaining)
- [ ] You think in VMs/containers, not in "apps on my computer"

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
