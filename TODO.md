# Homelab TODO

## Repo Cleanup (in progress this session)
- [x] Update README.md structure diagram to include security/soc-lab/
- [x] Add docker-compose.yml to Audiobookshelf service folder
- [x] Add CHANGELOG / History section to Audiobookshelf doc
- [x] Add .gitignore
- [x] Verify all docs are consistent (host hardware specs across files)

## Validation Window
After 24h of normal ABS usage with no issues:
- [x] docker rm audiobookshelf_old
- [x] sudo rm -rf /home/admin/audiobookshelf/  (the old bind-mount folder)
- [ ] Keep the tarball backup until next weekly backup

## Phase 0 — Services to Deploy
Each must justify its existence in one sentence before deployment.
- [ ] Nginx Proxy Manager (reverse proxy + SSL)
- [ ] Pi-hole (local DNS so services get hostnames)
- [ ] Uptime Kuma (alerting on service outages)
- [ ] WireGuard (replace Tailscale dependency for portfolio purposes — debatable, decide later)
- [ ] Portainer (container observability UI)

## Phase 0 — Hardening Tasks
- [ ] VM SSH hardening (disable root, key-only auth, change port, fail2ban)
- [ ] UFW firewall rules on the VM
- [ ] Automated backup script (rsync + cron) for Docker volumes
- [ ] Migrate Navidrome script (`musiq.py`) — was deleted, may rebuild later

## Cross-Cutting
- [ ] Sync completed roadmap items at strma77.github.io (currently shows 0%, lying)
- [ ] Document the GitOps workflow in workstation-setup.md or a new ops doc
- [ ] Set up shell aliases / functions (.bashrc) for common docker workflows
