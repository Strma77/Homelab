# Homarr

**What:** Single-page dashboard / landing page for the homelab.
**Why:** Front door for the stack — quick visual access to every service, with live status integration via Uptime Kuma so each tile shows up/down at a glance.
**Where:** Container `homarr` on the `homelab` Docker network, UI on `:7575`.
**Status:** Running with 5 service tiles, Uptime Kuma status integration, Zagreb weather widget, and a clock.

> ⚠️ This doc was drafted with AI assistance during Phase 0 close-out. Rewrite owed by **2026-08-31** — see `docs/TODO.md` documentation debt entry.

---

## Why it exists

Honest framing: this is the most cosmetic service in the stack. It doesn't teach a new technical skill or solve a security problem. What it does provide:

- A single URL to bookmark instead of remembering 6 different `IP:port` combinations
- Visual confirmation of service health that doesn't require opening Uptime Kuma separately — tiles show a green/red status dot pulled from Kuma
- A presentation surface — when showing the homelab to someone, "open this URL" is a much better story than "let me list ports for you"

If Homarr disappeared the homelab still works. But the friction of "what was that URL again" is the kind of small tax that adds up, and Homarr eliminates it.

---

## Deployment

Defined in `docker-compose.yml` next to this doc. Standard pattern. One detail worth noting: Homarr ships with three named volumes instead of one.

```text
homarr_configs   →  /app/data/configs    dashboard layout + tile config + integration creds
homarr_data      →  /data                SQLite DB, user accounts
homarr_icons     →  /app/public/icons    cached service icons (regenerable)
```

`configs` and `data` are backed up. `icons` is intentionally excluded — re-downloadable on container restart, no point archiving them.

---

## Configuration

Configuration is done through the UI in edit mode, not in files. This means:

- The dashboard layout isn't in Git — it lives in the `homarr_configs` volume
- Tile additions, widget tweaks, integration settings: all done by clicking around
- Backups become the only record of the configuration

Each service tile takes two URLs:

- **Internal URL** — used by Homarr for status checks (e.g. `http://audiobookshelf:80` via the homelab network). The container-name path, same trick Uptime Kuma uses.
- **External URL** — where clicking the tile sends the user (e.g. `http://audiobookshelf.home` via NPM, or `http://192.168.100.50:port` for non-proxied admin tools).

### The Uptime Kuma integration

The useful integration. Homarr can pull monitor status from Kuma's API and color the tiles accordingly — green dot = monitor up, red dot = monitor down. Setup outline:

1. Edit mode → settings → Integrations → Uptime Kuma
2. URL: `http://uptime-kuma:3001` (container-name path, same network)
3. Provide Kuma admin credentials
4. Per tile: in tile settings, enable the integration and select the matching Kuma monitor

Result: the monitoring infrastructure surfaces directly on the dashboard. No need to open Kuma to see if something's down — the tile says so.

### Configured tiles

The 5 currently-active service tiles:

| Tile | Internal URL | External URL |
|------|--------------|--------------|
| Audiobookshelf | `http://audiobookshelf:80` | `http://audiobookshelf.home` |
| Nginx Proxy Manager | `http://nginx-manager:81` | `http://192.168.100.50:81` |
| Pi-hole | `http://pihole:80/admin` | `http://192.168.100.50:8888/admin` |
| Uptime Kuma | `http://uptime-kuma:3001` | `http://192.168.100.50:3001` |
| Portainer | `http://portainer:9000` | `http://192.168.100.50:9000` |

Plus a Zagreb weather widget and clock. The default GitHub / Discord / Donate tiles were removed during setup — they're placeholder ads for Homarr itself, not useful.

---

## Backups

`homarr_configs` and `homarr_data` are in the daily backup. `homarr_icons` is excluded by design.

Verified present in the most recent archive:
```text
homarr_configs/default.json
homarr_data/db.sqlite
```

If both are restored, the dashboard layout, tiles, integrations, and the user account come back exactly as they were. If only `data` came back, the layout would be lost but the account would survive.

---

## Verifying it works

```bash
docker ps | grep homarr
curl -I http://192.168.100.50:7575
```

The real check is the browser: open the dashboard, confirm tiles render with their live status dots from Kuma, confirm clicking a tile reaches the expected service.

---

## Known limitations

- **Configuration lives in the UI, not in Git.** Means the backup is the single source of truth for the layout. Acceptable for a single-user homelab; would be a problem in a team setting.
- **Drag-drop layout is fragile.** It's easy to misalign tiles or accidentally move things. Lock-mode helps but isn't a substitute for being careful in edit mode.
- **Admin UI deliberately not behind NPM yet.** Could be `home.home` or similar through NPM later. Cosmetic concern, not blocking.
- **Status dots depend on Kuma being up.** If Kuma is down, all dots go grey/red simultaneously — which is actually a useful signal in itself.

---

## History

### 2026-06 — Initial deployment

Deployed via compose with three named volumes (configs, data, icons). Compose validated and came up clean on first try — by this point the pattern (image, container name, single port publish, `homelab` external network, named volumes) was muscle memory.

Configured 5 service tiles for the existing stack, set up the Uptime Kuma integration, added a Zagreb weather widget, removed the default placeholder widgets. Took a screenshot of the finished dashboard (`screenshots/dashboard.png`) — first tile-layout pass was misaligned but functional; left it because the layout is cheap to fix later and not the point of the artifact.
