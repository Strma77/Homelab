# Homelab TODO

## Current Phase: Phase 1 — Infrastructure Migration (nearly done — diagram + docs-match left)

## Quick / loose ends
- [ ] Portainer — sort out why it's flaky
- [ ] Audiobookshelf — not working since migration, fix or retire
- [ ] Switch service access from 10.10.20.x IPs to real hostnames (NPM) — would also shrink the firewall allow-list to basically 443+22
- [x] Commit the self-hosted roadmap service (done)

## Phase 1 — In Progress
- [x] Tighten WAN→Services firewall rule — DONE + verified (2026-09-06). Replaced the open `192.168.100.0/24→LAN any` rule with a `Services_Ports` alias (22,80,81,443,3001,7575,8080,9443,13378). Proved with :9000 timeout while :7575 works. No port 53 needed (all DNS goes via OPNsense .2).
- [ ] Delete the disabled `Allow Users to Services zone` rule (proven redundant, just needs removing + Apply)
- [x] Test Lab zone isolation — DONE + verified (2026-09-06). Live-ISO VM on vmbr2 @ 10.10.30.50: ping Services = 100% loss (silent block), ping 1.1.1.1 = 0% loss. Lab walled off, internet OK.
- [ ] **Test-restore a backup** — restore CT 101 to a throwaway VMID (e.g. 999), confirm boot, delete. Backups still UNPROVEN until this passes. ← highest-value next job
- [ ] Fix DNS leak / adblocking — phone gets ads on wifi. Diagnostic first (Pi-hole query log: is the phone even hitting Pi-hole, or bypassing via DoH / DNS2 leak?). Then Unbound forward-first→Pi-hole, kill any client-side 1.1.1.1 fallback. Needs a fresh head.
- [ ] Update network topology diagram — reflect OPNsense 3-zone routing, 10.10.20/30 split, DNS chain, NFS path, verified firewall boundaries.

## Phase 1 — Exit Checkpoints (remaining)
- [x] VLAN segmentation verified — Lab can't reach Services, Users→Services restricted (both proven 2026-09-06)
- [ ] Network topology diagram accurate and current
- [ ] Repo docs match live infra — mostly done; blockers are the diagram + the Audiobookshelf fix/retire call

## Doc fixes
- [x] Rewrite scripts/backups.md around PVE vzdump
- [x] New infrastructure/proxmox.md
- [x] New services/pihole/Pihole.md (fills gap + fixes ghost links)
- [x] New services/roadmap/Roadmap.md
- [x] workstation-setup.md backup section -> native nfs
- [x] Stale IPs fixed in Homarr/NPM/Portainer/vm-hardening
- [x] README: firewall claim, ad-block honesty, backup history, monitor count
- [x] Kuma monitors verified live on 10.x (were already correct); drop the "verify" banner + fix any lingering .50 text in UptimeKuma.md
- [x] Homarr tiles verified live on 10.x
- [ ] Audiobookshelf — fix-or-retire decision, then rewrite Audiobookshelf.md

## Phase 1 — Parked
- [ ] Sandbox box — needs SSD before Proxmox
- [ ] SOC lab migration into Lab zone (still on VirtualBox)
- [ ] Tailscale on new Docker VM (remote access)
- [ ] Localhost-bind refactor for Uptime Kuma + Homarr
- [ ] ntfy: narrow matcher to failures-only, consider self-hosting with auth
- [ ] Off-site backup (3-2-1) — currently on-site only
- [ ] SSH cheatsheet md (ssh pve / ssh docker mappings)
- [ ] RepCount clone / MonkDew rework+host / local AI agent — someday
