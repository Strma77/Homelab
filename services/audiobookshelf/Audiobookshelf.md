# Audiobookshelf

**What:** Self-hosted audiobook server + mobile app. Streams the personal audiobook library.
**Why:** Own the library, listen from anywhere without a subscription service.
**Where:** Docker container on VM 100 (`docker-host`, `10.10.20.50`). Image `ghcr.io/advplyr/audiobookshelf:latest` (v2.36.0). Accessed primarily through the Audiobookshelf mobile app over Tailscale.

> **Migration note (2026-09):** this service moved from the old VirtualBox setup to Proxmox VM 100. The old `vboxsf` shared-folder media path and `192.168.100.50` addressing are dead — see History. Current setup below.

---

## Access

| Method | URL |
|--------|-----|
| LAN (browser) | `http://10.10.20.50:13378/audiobookshelf` |
| Remote (mobile app) | Tailscale IP of VM 100, port `13378` |

- The container binds `0.0.0.0:13378` (all interfaces) so it's reachable over the LAN and Tailscale. It was previously `127.0.0.1`-only, which is why it appeared "broken" after migration — reachable from nowhere.
- App serves under base path **`/audiobookshelf`** (`ROUTER_BASE_PATH`). Root `/` will look broken — always include `/audiobookshelf`.
- Remote access is via **Tailscale** (VM + phone on the same tailnet). No port-forwarding, no public exposure. Since it's used through the mobile app, no domain/NPM is needed.

> An old NPM proxy host `audiobookshelf.home → audiobookshelf:80` exists but is unused — the local DNS record for `.home` never resolved, and the app-over-Tailscale workflow doesn't need it. Left in place, not relied on.

---

## Storage

| Mount | Container path | Notes |
|-------|----------------|-------|
| `/mnt/audiobooks` (bind) | `/audiobooks` | Media library (~8 GB) |
| `audiobookshelf_config` (volume) | `/config` | DB, users, settings |
| `audiobookshelf_metadata` (volume) | `/metadata` | Covers, cached metadata |

- **Media lives ON the VM**, copied from the desktop (`/home/strma77/Music/Audiobooks`) via `rsync`, owned `strma:strma`. This is deliberate: media on the always-on Beelink, not an NFS mount from the sometimes-off desktop — so the library works even when the desktop is off.
- To add books later: `rsync -av <source>/ strma@10.10.20.50:/mnt/audiobooks/` then trigger a library re-scan in the app (Settings → Libraries → re-scan). New files are not auto-indexed reliably.
- The `config` + `metadata` volumes are captured by the nightly `vzdump` of VM 100 (see `scripts/backups.md`). In-app auto-backups are disabled — vzdump covers it.

---

## History

### 2026-09 — Fixed post-migration
Container was healthy but unreachable: bound to `127.0.0.1` only, and its media folder (`/mnt/audiobooks`) was empty because the library never migrated. Fixed by copying media from the desktop via rsync and flipping the bind to `0.0.0.0:13378`. Verified working from cellular via Tailscale.

### Pre-2026-09 — VirtualBox era
Ran in VirtualBox at `192.168.100.50` with media via a `vboxsf` shared folder and remote access via Tailscale on the desktop host. All superseded by the Proxmox VM setup above.
