# Homelab TODO

## ⚠️ Documentation debt — owned, dated, scheduled

The following service runbooks were drafted with AI assistance during the Phase 0 close-out (2026-06), to allow finishing the phase cleanly without writing 3 runbooks in one tired session:

- `services/uptime-kuma/UptimeKuma.md`
- `services/portainer/Portainer.md`
- `services/homarr/Homarr.md`

**Commitment:** rewrite each in my own voice by **2026-08-31**, after re-reading thoroughly and verifying I can defend every claim in conversation. Rewriting protects the credibility of the repo and locks the technical understanding properly.

Track until paid.

---

## Phase 0 — Closing Out (final items)
- [x] Localhost-bind refactor for Audiobookshelf — closes the documented Docker/UFW bypass for this service. Pattern proven; remaining services can adopt incrementally.
- [ ] Apply localhost-bind pattern to other user-facing services (Uptime Kuma, Homarr) incrementally — admin tools (NPM :81, Portainer, Pi-hole web) intentionally left directly accessible as break-glass
- [ ] Sync completed roadmap items at strma77.github.io
- [~] Brief docs for Uptime Kuma, Portainer, Homarr — drafted; rewrite owed (see Documentation debt above)

## Phase 0 — Services to Deploy
Each must justify its existence in one sentence before deployment.
- [x] Nginx Proxy Manager (reverse proxy)
- [x] Pi-hole (local DNS so services get hostnames)
- [x] Uptime Kuma (alerting on service outages — Telegram channel set up)
- [x] Portainer (container observability UI)
- [x] Homarr dashboard (single front door, Uptime Kuma integration)
- [~] WireGuard — **deferred.** Tailscale already covers secure remote access from any device, works behind the ISP-locked ONT (which would block WireGuard's required port forwarding). Deploying WireGuard now would be tutorial addiction. Revisit if Phase 3 needs a self-hosted VPN endpoint.

## Phase 0 — Hardening Tasks
- [x] VM SSH hardening (disable root, key-only auth, fail2ban) — documented in security/vm-hardening.md
- [x] UFW firewall rules on the VM
- [x] Automated backup script (tar + cron) for Docker volumes — tested restore, documented in scripts/backups.md
- [x] Break/fix drill executed (Pi-hole stop/recover, alerted via Telegram, documented in Pihole.md)
- [x] Localhost-bind refactor (Audiobookshelf) — closes Docker/UFW gap for the canonical user-facing service
- [ ] Migrate Navidrome script (`musiq.py`) — was deleted, may rebuild later

## Phase 0 — Documentation
- [x] services/nginx-proxy-manager/NginxProxyManager.md — runbook
- [x] services/pihole/Pihole.md — runbook
- [x] Network topology diagram — docs/HomeLab-Network-Topology.png (+ .excalidraw source)
- [~] services/uptime-kuma/UptimeKuma.md — runbook (see Documentation debt)
- [~] services/portainer/Portainer.md — runbook (see Documentation debt)
- [~] services/homarr/Homarr.md — runbook (see Documentation debt)

## Networking / DNS (Phase 1 prep)
- [ ] Pi-hole as network-wide DNS — requires VM to be 24/7 (Phase 1)
- [ ] Investigate ISP ONT (ZTE F8648P) for DHCP DNS reconfiguration to point all LAN devices at Pi-hole automatically
- [ ] Tailscale MagicDNS or per-device DNS so `.home` hostnames resolve over Tailscale (so refactored services work remotely)

## Storage / Infrastructure (future, not urgent)
- [ ] Move audiobooks (~/Music/Audiobooks) from SSD to HDD
- [ ] Investigate sda6 (149G, 86% full, UUID mount) — old OS install?
- [ ] Reconsider HDD partition scheme (prvi/Glavni/treći) — consolidate or leave?
- [ ] Decide VM location — move to HDD or wait for Proxmox migration (likely wait)
- [ ] Ubuntu 26.04 LTS upgrade — wait for 26.04.1 (Aug 2026), only if real need

## Cross-Cutting
- [ ] Document the GitOps workflow in workstation-setup.md or a new ops doc
- [ ] Set up shell aliases / functions for common docker workflows
