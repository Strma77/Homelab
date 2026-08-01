# Homarr

**What:** Single-page dashboard / landing page for the homelab.
**Why:** Front door for the stack — one bookmarked URL instead of remembering 6 different `IP:port` combinations.
**Where:** Container `homarr` on the `homelab` Docker network, UI on `:7575` (mapped to internal port `3000`).
**Image:** `ghcr.io/homarr-labs/homarr:latest` (migrated from deprecated `ajnart/homarr` in July 2026)
**Status:** Running on Docker VM at `192.168.100.50`.

---

## Why it exists

The most cosmetic service in the stack. It doesn't teach a new technical skill or solve a security problem. What it provides:

- A single URL to bookmark instead of remembering ports for 6 services + Proxmox
- A presentation surface — "open this URL" is a better story than "let me list ports for you"
- Quick visual access when context-switching back to the homelab after days away

If Homarr disappeared the homelab still works. But the friction of "what was that URL again" adds up, and Homarr eliminates it.

---

## Migration note (July 2026)

The original `ajnart/homarr` image was a semi-abandoned fork. The project moved to `ghcr.io/homarr-labs/homarr` as the actively maintained image. The migration involved:

- **Image swap:** `ghcr.io/ajnart/homarr:latest` → `ghcr.io/homarr-labs/homarr:latest`
- **Volume restructure:** old image used 3 volumes (`homarr_configs`, `homarr_data`, `homarr_icons`). New image uses 1 volume (`homarr_data` mounted at `/appdata`). Old volumes were deleted.
- **Port change:** old image listened on `7575` internally. New image listens on `3000`. Port mapping changed from `7575:7575` to `7575:3000` to keep the external port consistent.
- **Required env var:** new image requires `SECRET_ENCRYPTION_KEY` — a 64-character hex string. Generated with `openssl rand -hex 32`. Stored in `.env` file (gitignored).
- **Dashboard rebuilt from scratch** — tile config from old image was incompatible. All service tiles re-added manually.

---

## Deployment

Defined in `docker-compose.yml` next to this doc.

```yaml
image: ghcr.io/homarr-labs/homarr:latest
ports: "7575:3000"
volumes: homarr_data:/appdata
environment: SECRET_ENCRYPTION_KEY (from .env, gitignored)
```

The `SECRET_ENCRYPTION_KEY` is loaded from a `.env` file in the same directory as the compose file. Do not commit the key to Git.

---

## Configuration

Configuration is done through the web UI, not in files. The dashboard layout lives in the `homarr_data` volume, not in Git.

### Configured tiles

| Tile | URL |
|------|-----|
| Proxmox | `https://192.168.100.10:8006` |
| Pi-hole | `http://192.168.100.53/admin` |
| Portainer | `https://192.168.100.50:9443` |
| Uptime Kuma | `http://192.168.100.50:3001` |
| NPM | `http://192.168.100.50:81` |
| Audiobookshelf | `http://192.168.100.50:13378` |

---

## Verifying it works

```bash
docker ps | grep homarr
curl -I http://192.168.100.50:7575
```

The real check is the browser: open the dashboard, confirm tiles render and clicking each one reaches the expected service.

---

## Known limitations

- **Configuration lives in the UI, not in Git.** The volume backup is the only record of the layout.
- **`:latest` tag.** Subject to breaking changes on pull — the `ajnart` → `homarr-labs` migration was exactly this kind of problem. Consider pinning to a specific version.
- **No Uptime Kuma integration in new image.** The old `ajnart` fork had a Kuma status integration for tile coloring. The new `homarr-labs` image may have a different integration path — not yet investigated.

---

## History

### 2026-06 — Initial deployment (ajnart/homarr)
Deployed via compose with three named volumes. 5 service tiles configured with Uptime Kuma status integration.

### 2026-07 — Migration to homarr-labs/homarr
Old image deprecated. Migrated to actively maintained fork. Required full volume wipe, compose rewrite (new image, single volume, different internal port, mandatory encryption key), and dashboard rebuild from scratch. See migration note above.
