# Homelab TODO

## Phase 0 — Closing Out (final items)
- [ ] Localhost-bind refactor — bind audiobookshelf to `127.0.0.1:13378`,
      expose only through NPM; closes the documented Docker/UFW bypass gap
- [ ] Sync completed roadmap items at strma77.github.io
- [ ] Brief docs for Uptime Kuma, Portainer, Homarr (compose files
      exist but service-level writeups don't yet)

## Phase 0 — Services to Deploy
Each must justify its existence in one sentence before deployment.
- [x] Nginx Proxy Manager (reverse proxy)
- [x] Pi-hole (local DNS so services get hostnames)
- [x] Uptime Kuma (alerting on service outages — Telegram channel set up)
- [x] Portainer (container observability UI)
- [x] Homarr dashboard (single front door, Uptime Kuma integration)
- [~] WireGuard — **deferred.** Tailscale already covers secure remote
      access from any device, works behind the ISP-locked ONT (which would
      block WireGuard's required port forwarding). Deploying WireGuard now
      would be tutorial addiction. Revisit if Phase 3 needs a self-hosted
      VPN endpoint.

## Phase 0 — Hardening Tasks
- [x] VM SSH hardening (disable root, key-only auth, fail2ban) — documented in security/vm-hardening.md
- [x] UFW firewall rules on the VM
- [x] Automated backup script (tar + cron) for Docker volumes — tested restore, documented in scripts/backups.md
- [x] Break/fix drill executed (Pi-hole stop/recover, alerted via Telegram, documented in Pihole.md)
- [ ] Localhost-bind refactor (see Phase 0 Closing Out)
- [ ] Migrate Navidrome script (`musiq.py`) — was deleted, may rebuild later

## Phase 0 — Documentation
- [x] services/nginx-proxy-manager/NginxProxyManager.md — runbook
- [x] services/pihole/Pihole.md — runbook
- [x] Network topology diagram — docs/HomeLab-Network-Topology.png (+ .excalidraw source)
- [ ] services/uptime-kuma/UptimeKuma.md — runbook
- [ ] services/portainer/Portainer.md — runbook
- [ ] services/homarr/Homarr.md — runbook

## Networking / DNS (Phase 1 prep)
- [ ] Pi-hole as network-wide DNS — requires VM to be 24/7 (Phase 1)
- [ ] Investigate ISP ONT (ZTE F8648P) for DHCP DNS reconfiguration
      to point all LAN devices at Pi-hole automatically

## Storage / Infrastructure (future, not urgent)
- [ ] Move audiobooks (~/Music/Audiobooks) from SSD to HDD
- [ ] Investigate sda6 (149G, 86% full, UUID mount) — old OS install?
- [ ] Reconsider HDD partition scheme (prvi/Glavni/treći) — consolidate or leave?
- [ ] Decide VM location — move to HDD or wait for Proxmox migration (likely wait)
- [ ] Ubuntu 26.04 LTS upgrade — wait for 26.04.1 (Aug 2026), only if real need

## Cross-Cutting
- [ ] Document the GitOps workflow in workstation-setup.md or a new ops doc
- [ ] Set up shell aliases / functions for common docker workflows
