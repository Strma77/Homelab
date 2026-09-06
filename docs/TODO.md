# Homelab TODO

## Current Phase: Phase 1 — Infrastructure Migration (2 exit checkpoints remaining)

## Quick / loose ends
- [ ] Portainer — sort out why it's flaky
- [ ] Audiobookshelf — not working since migration, fix or retire
- [ ] Switch service access from 10.10.20.x IPs to real hostnames (NPM)
- [ ] Commit the self-hosted roadmap service (services/roadmap/ — currently untracked)

## Phase 1 — In Progress
- [ ] Tighten WAN→Services firewall rule — still `any` from 192.168.100.0/24 → LAN. Restrict to used ports only (22,53,80,81,443,3001,7575,9443).
- [ ] Fix DNS leak / adblocking — phone gets ads on wifi. Unbound forward-first→Pi-hole, kill the DNS2=1.1.1.1 client fallback. Confirm phone actually hits Pi-hole (query log).
- [ ] Test Lab zone isolation — real VM on vmbr2, prove it can't reach 10.10.20.0/24.
- [ ] Update network topology diagram — reflect OPNsense, 3 zones, DNS chain, NFS path.
- [ ] **Test-restore a backup** — restore CT 101 to a throwaway VMID. Backups are unproven until this passes.

## Phase 1 — Exit Checkpoints (remaining)
- [ ] VLAN segmentation verified — lab traffic can't reach services (configured, untested)
- [ ] Network topology diagram accurate and current
- [ ] Repo docs match live infra (currently FALSE — see doc-fix list)

## Doc fixes
- [x] Rewrite scripts/backups.md around PVE vzdump (2026-09)
- [x] New infrastructure/proxmox.md — PVE host + storage + vzdump + ntfy
- [x] New services/pihole/Pihole.md — fills the missing core-service doc, fixes ghost links
- [x] New services/roadmap/Roadmap.md
- [x] workstation-setup.md backup section -> native nfs reality
- [x] Stale IPs fixed in Homarr/NPM/Portainer/vm-hardening
- [x] README: false firewall claim, ad-block honesty, backup history, monitor count
- [x] **VERIFY LIVE — Uptime Kuma monitor targets** still show 192.168.100.50 in the doc. Reconcile against the running Kuma UI; if monitors point at the dead IP, monitoring is silently broken. Then update UptimeKuma.md.
- [x] **VERIFY LIVE — Homarr tiles** — doc updated to 10.10.20.x; confirm the running dashboard tiles match (not just the doc).
- [ ] Audiobookshelf — fix-or-retire decision, then rewrite Audiobookshelf.md (currently VirtualBox-era history with a status banner).

## Phase 1 — Parked
- [ ] Sandbox box — needs SSD before Proxmox
- [ ] SOC lab migration into Lab zone (still on VirtualBox)
- [ ] Tailscale on new Docker VM (remote access)
- [ ] Localhost-bind refactor for Uptime Kuma + Homarr
- [ ] ntfy: narrow matcher to failures-only, consider self-hosting with auth
- [ ] Off-site backup (3-2-1) — currently on-site only
- [ ] SSH cheatsheet md (what "ssh pve"/"ssh docker" map to)
- [ ] RepCount clone / MonkDew rework+host / local AI agent — someday
