# Homelab TODO

## Current Phase: Phase 1 — Infrastructure Migration (nearly done — diagram + docs-match left)

## Quick / loose ends
- [ ] Portainer — sort out why it's flaky
- [ ] Audiobookshelf — not working since migration, fix or retire
- [ ] Switch service access from 10.10.20.x IPs to real hostnames (NPM) — would also shrink the firewall allow-list to basically 443+22
- [ ] figure out why roadmap site doesnt save state even after refresh

## Phase 1 — In Progress
- [ ] **Test-restore a backup** — restore CT 101 to a throwaway VMID (e.g. 999), confirm boot, delete. Backups still UNPROVEN until this passes. ← highest-value next job
- [ ] Fix DNS leak / adblocking — phone gets ads on wifi. Diagnostic first (Pi-hole query log: is the phone even hitting Pi-hole, or bypassing via DoH / DNS2 leak?). Then Unbound forward-first→Pi-hole, kill any client-side 1.1.1.1 fallback. Needs a fresh head.
- [ ] Update network topology diagram — reflect OPNsense 3-zone routing, 10.10.20/30 split, DNS chain, NFS path, verified firewall boundaries.

## Phase 1 — Exit Checkpoints (remaining)
- [ ] Network topology diagram accurate and current
- [ ] Repo docs match live infra — mostly done; blockers are the diagram + the Audiobookshelf fix/retire call

## Doc fixes
- [ ] Audiobookshelf — fix-or-retire decision, then rewrite Audiobookshelf.md

## Phase 1 — Parked
- [ ] Sandbox box — needs SSD before Proxmox
- [ ] SOC lab migration into Lab zone (still on VirtualBox)
- [ ] Tailscale on new Docker VM (remote access)
- [ ] Localhost-bind refactor for Uptime Kuma + Homarr
- [ ] ntfy: narrow matcher to failures-only, consider self-hosting with auth
- [ ] Off-site backup (3-2-1) — currently on-site only
- [ ] SSH cheatsheet md (ssh pve / ssh docker mappings)
- [ ] RepCount clone / MonkDew rework+host / local AI agent — someday, as soon as possible as I have real world use for it immediately
