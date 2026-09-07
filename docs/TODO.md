# Homelab TODO

## Current Phase: Phase 1 wrapping up → Phase 2 ready to start
Phase 1 gates DONE: segmentation verified (both boundaries), backups restore-proven. Only non-gate polish left below.

## Quick / loose ends
- [ ] Portainer — sort out why it's flaky
- [ ] Audiobookshelf — not working since migration, fix or retire
- [ ] Switch service access from 10.10.20.x IPs to real hostnames (NPM) — also shrinks firewall allow-list to ~443+22
- [ ] Roadmap site doesn't persist checkbox state on refresh (see note — it's static by design)

## Phase 1 — remaining polish (not gates)
- [ ] Rewrite Audiobookshelf.md after the fix/retire call

## Phase 1 — Parked
- [ ] Sandbox box — needs SSD before Proxmox
- [ ] SOC lab migration into Lab zone (still on VirtualBox)
- [ ] Tailscale on Docker VM (remote access)
- [ ] Localhost-bind refactor for Uptime Kuma + Homarr
- [ ] Off-site backup (3-2-1) — currently on-site only
- [ ] RepCount clone / MonkDew rework+host / local AI agent — wanted ASAP, real use case
