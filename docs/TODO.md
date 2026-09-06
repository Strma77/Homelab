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

## Doc fixes (repo is lying in these spots)
- [ ] Rewrite scripts/backups.md — describes the DEAD cron script. Reality: PVE vzdump, VMIDs 100/101/102, storage `desktopbackup` (nfs type), keep-last=3, ntfy alerts. Old backup-homelab.sh is retired/redundant.
- [ ] Fix stale IPs across docs — Audiobookshelf/NPM/Portainer/Homarr still say 192.168.100.50 / .53. Post-migration: services 10.10.20.50, Pi-hole 10.10.20.53.
- [ ] workstation-setup.md backup section — storage is now `nfs:` type, not `dir:`; fstab NFS line commented out on pve host.
- [ ] Broken refs to services/pihole/Pihole.md — doc doesn't exist. Create it or fix the links in UptimeKuma.md + backups.md.
- [ ] Document services/roadmap (new self-hosted roadmap app).

## Phase 1 — Parked
- [ ] Sandbox box — needs SSD before Proxmox
- [ ] SOC lab migration into Lab zone (still on VirtualBox)
- [ ] Tailscale on new Docker VM (remote access)
- [ ] Localhost-bind refactor for Uptime Kuma + Homarr
- [ ] ntfy: narrow matcher to failures-only, consider self-hosting with auth
- [ ] Off-site backup (3-2-1) — currently on-site only
- [ ] SSH cheatsheet md (what "ssh pve"/"ssh docker" map to)
- [ ] RepCount clone / MonkDew rework+host / local AI agent — someday
