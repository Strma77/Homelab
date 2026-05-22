# Homelab TODO

## Repo Cleanup
- [x] Update README.md structure diagram to include security/soc-lab/
- [x] Add docker-compose.yml to Audiobookshelf service folder
- [x] Add CHANGELOG / History section to Audiobookshelf doc
- [x] Add .gitignore
- [x] Verify all docs are consistent (host hardware specs across files)

## Validation Window
- [x] docker rm audiobookshelf_old
- [x] sudo rm -rf /home/admin/audiobookshelf/  (old bind-mount folder)
- [x] Keep the tarball backup until next weekly backup (superseded by automated backups)

## Phase 0 — Services to Deploy
Each must justify its existence in one sentence before deployment.
- [ ] Nginx Proxy Manager (reverse proxy + SSL)
- [ ] Pi-hole (local DNS so services get hostnames)
- [ ] Uptime Kuma (alerting on service outages)
- [ ] WireGuard (replace Tailscale dependency — debatable, decide later)
- [ ] Portainer (container observability UI)

## Phase 0 — Hardening Tasks
- [x] VM SSH hardening (disable root, key-only auth, fail2ban) — documented in security/vm-hardening.md
- [x] UFW firewall rules on the VM
- [~] Automated backup script (rsync/tar + cron) for Docker volumes — IN PROGRESS
- [ ] Migrate Navidrome script (`musiq.py`) — was deleted, may rebuild later

## Storage / Infrastructure (future, not urgent)
- [ ] Move audiobooks (~/Music/Audiobooks) from SSD to HDD
- [ ] Investigate sda6 (149G, 86% full, UUID mount) — old OS install?
- [ ] Reconsider HDD partition scheme (prvi/Glavni/treći) — consolidate or leave?
- [ ] Decide VM location — move to HDD or wait for Proxmox migration (likely wait)
- [ ] Ubuntu 26.04 LTS upgrade — wait for 26.04.1 (Aug 2026), only if real need

## Cross-Cutting
- [ ] Sync completed roadmap items at strma77.github.io
- [ ] Document the GitOps workflow in workstation-setup.md or a new ops doc
- [ ] Set up shell aliases / functions for common docker workflows
