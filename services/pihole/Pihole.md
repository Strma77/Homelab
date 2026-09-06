# Pi-hole

**What:** Network-wide DNS resolver + ad/tracker blocking for the whole house.
**Why:** Filter ads/trackers at the DNS layer for every client, no per-device config.
**Where:** **CT 101** — an LXC container (not Docker anymore), `10.10.20.53` on vmbr1 (Services zone). Web UI `http://10.10.20.53/admin`.

> **Migration note:** Pi-hole used to be a Docker container on the flat `192.168.100.0/24` network. In Phase 1 it moved to a dedicated **LXC container (CT 101)** at `10.10.20.53` so DNS is always-on and independent of the Docker VM. Any doc or command referencing `docker stop pihole` is pre-migration — the current equivalent is `pct stop 101` / `pct start 101` on the Proxmox host.

---

## Specs (CT 101)

| Setting | Value |
|---------|-------|
| Type | LXC |
| OS | Ubuntu 24.04 |
| CPU / RAM / Disk | 1 core / 512 MB / 8 GB |
| Network | vmbr1 (Services), `10.10.20.53/24`, gateway `10.10.20.1` |
| Web UI | `http://10.10.20.53/admin` |
| Boot order | 2 (after OPNsense, before Docker VM) |

Backed up nightly as part of the PVE `vzdump` job (VMID 101). See `scripts/backups.md`.

---

## DNS chain

```
devices -> ISP router (192.168.100.1) -> OPNsense (192.168.100.2, Unbound) -> Pi-hole (10.10.20.53) -> Cloudflare (1.1.1.1)
```

OPNsense's Unbound is the resolver clients talk to; Unbound forwards to Pi-hole; Pi-hole filters and forwards upstream to Cloudflare. Router DHCP pushes OPNsense (`.2`) as client DNS.

---

## Known issue — ad-blocking leaks (open)

Ads still appear on some clients (notably phone over wifi) despite Pi-hole running. Two separate causes, don't conflate them:

1. **DNS-blocking ceiling (expected).** Pi-hole sinkholes ad *domains*. It cannot block first-party ads or ads served from the same domain/CDN as the content. `canyoublockit.com` passing the *simple* test but failing the *extreme* test is the **normal, healthy** result — the extreme test is built to defeat DNS-only blocking. Killing those needs uBlock Origin at the browser layer, not a Pi-hole change.
2. **Suspected client DNS fallback leak (fixable).** If clients are handed a secondary DNS of `1.1.1.1` (via DHCP or elsewhere), a share of queries bypass Pi-hole entirely even when it's healthy — leaking ads *and* skipping the whole Unbound->Pi-hole chain. Secondary DNS is **not** clean failover; it's queried opportunistically.

**Planned fix:** make Unbound do the fallback, not the clients — Unbound forwards to Pi-hole with `forward-first: yes` so it falls back to recursive resolution if Pi-hole is down, and remove any client-side `1.1.1.1` secondary. Diagnostic first: open Pi-hole -> Query Log, load an ad-heavy page on the phone, and confirm the phone's queries actually reach Pi-hole (if they barely appear, the phone is bypassing it — DoH/private DNS or the DNS2 leak).

---

## Single point of failure

Pi-hole is one LXC. If it's down and Unbound has no fallback, DNS fails for the **whole house**, not just the lab. The `forward-first` fix above is what stops a Pi-hole reboot from taking the house offline. HA (second Pi-hole + keepalived VIP) is a later-phase option, not built yet.

---

## Break/fix drill (2026-06, Docker era)

Ran while Pi-hole was still a Docker container: `docker stop pihole`, watched the two Pi-hole Uptime Kuma monitors go red within ~60s, received the Telegram alert, recovered with `docker start pihole`, monitors back green within ~90s. The other monitors stayed green, correctly isolating the failure scope. Screenshots in `services/uptime-kuma/screenshots/`.

To re-run the drill on the current LXC setup: `pct stop 101` / `pct start 101` on the pve host instead of the docker commands.

---

## Verifying it works

```bash
# from the pve host
pct status 101
# resolve through Pi-hole directly
dig @10.10.20.53 example.com +short
# admin UI
curl -I http://10.10.20.53/admin
```
