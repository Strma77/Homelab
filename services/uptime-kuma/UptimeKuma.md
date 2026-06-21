# Uptime Kuma

**What:** Monitoring + alerting for the homelab.
**Why:** Every compose file has a healthcheck, but nothing acted on them until Kuma. The container daemon just sets a flag and moves on — no human ever sees it unless they run `docker ps`. Kuma polls services, tracks history, and fires Telegram alerts when something fails.
**Where:** Container `uptime-kuma` on the shared `homelab` Docker network, admin UI on `:3001`.
**Status:** Running with 7 monitors covering each service plus DNS and an external sanity check. Telegram notifications wired up and verified. Break/fix drill executed and documented in `Pihole.md`.

> ⚠️ This doc was drafted with AI assistance during Phase 0 close-out. Rewrite owed by **2026-08-31** — see `docs/TODO.md` documentation debt entry.

---

## Why it exists

Up to this point, healthchecks were the homelab's "second-class signal" — defined in every compose file, recorded by Docker as container state, but never surfaced anywhere a human would notice. The Audiobookshelf container could go unhealthy at 3am and the first time I'd know was when I tried to use it.

Kuma is the consumer for those healthchecks. It polls services on a schedule, tracks uptime history, and pings Telegram when something fails. Closes the "find out from alerts not by noticing" exit checkpoint that Phase 0 listed.

---

## Architecture

Kuma sits on the same `homelab` Docker network as the services it monitors. That matters: it means Kuma can reach backend containers by name (`http://audiobookshelf:80`, `http://nginx-manager:81`) and test the internal network, not the external Docker port publish. If the bridge breaks or a container dies, Kuma sees it directly.

```text
homelab services ──┐
                   │ HTTP / DNS / Ping checks (60s intervals)
                   ▼
              Uptime Kuma
                   │ on failure
                   ▼
              Telegram bot ──▶ phone push notification
```

---

## Deployment

Defined in `docker-compose.yml` next to this doc. Same pattern as everything else by this point — image, container name, single port publish (`3001:3001`), restart policy, the `homelab` network declared as external, one named volume on `/app/data`.

The only new-ish detail: Kuma's image ships with its own healthcheck script (`node /app/extra/healthcheck.js`). No need to write one or hunt for tooling — use the upstream one.

---

## Monitor design

The 7 monitors are layered deliberately. Each tests a different facet so the failure pattern tells you what broke.

| # | Type | Target | Tests |
|---|------|--------|-------|
| 1 | HTTP(s) | `http://audiobookshelf:80` | ABS app health |
| 2 | HTTP(s) | `http://nginx-manager:81` | NPM admin UI alive |
| 3 | HTTP(s) | `http://nginx-manager:80` with `Host: audiobookshelf.home` header | NPM actually doing its routing job |
| 4 | HTTP(s) | `http://pihole:80/admin` | Pi-hole web UI alive |
| 5 | DNS | Resolve `audiobookshelf.home` via resolver `192.168.100.50` | Pi-hole actually doing its DNS job |
| 6 | Ping | `192.168.100.50` | VM itself alive |
| 7 | HTTP(s) | `https://1.1.1.1` | Internet/upstream working — distinguishes "homelab broken" from "internet broken" |

A few design choices worth calling out:

**HTTP monitors use container names, not IPs.** Because Kuma is on the `homelab` network, it can resolve `audiobookshelf`, `nginx-manager`, `pihole` directly via Docker's internal DNS. Container-name routing tests the internal bridge — if the Docker network breaks, the monitors catch it.

**The DNS monitor uses the IP `192.168.100.50`, not the container name `pihole`.** This was the one gotcha — Kuma's DNS monitor doesn't resolve its resolver field via Docker DNS; it needs a raw IP. Chicken-and-egg: you can't ask DNS to find your DNS server. The error message the first time was `Invalid IP address: [pihole]:53`, which was a clear pointer at the issue. Lesson: HTTP monitors are app-layer (Docker DNS is fine); DNS monitors talk to the DNS resolver before any DNS exists, so they need a literal address.

**Monitor #3 is the routing-layer monitor.** It hits NPM with a manually-set `Host:` header so NPM has to do its real job — pick a backend by hostname — instead of just answering on the admin UI port. If the proxy host config breaks but NPM itself is up, monitor #2 wouldn't catch it; #3 does.

**Monitor #7 is the upstream sanity check.** If both #7 and the homelab monitors all go red simultaneously, the problem is your internet (or your phone's notifications path), not your stack. If only homelab monitors are red and #7 is green, the problem is local. That partitioning is genuinely useful at 2am.

Retry/timeout settings on all monitors: heartbeat 60s, retries 2, timeout default. The retries=2 prevents alerting on single transient blips while still surfacing real outages within ~3 minutes.

---

## Notifications (Telegram)

Telegram is the alert channel. Setup outline:

1. Talk to `@BotFather` on Telegram, `/newbot`, get a bot token.
2. Send the bot any message (it can't message you until you've messaged it once — anti-spam thing).
3. Fetch your chat ID from `https://api.telegram.org/bot<TOKEN>/getUpdates`.
4. In Kuma → Settings → Notifications → add a Telegram notification with the token and chat ID.
5. Test before saving — should land on the phone within ~5 seconds.
6. Toggle "Apply on all existing monitors" so new monitors auto-use it.

The bot token is effectively the bot's password. Don't paste it in chat, screenshots, or the repo. If leaked, rotate via `/revoke` in BotFather.

---

## Backups

The `uptime-kuma_data` volume is in the daily backup. It contains the SQLite DB with monitor configs, history, notification settings, and the admin account. Losing it means rebuilding every monitor and notification by hand. Verified present in the most recent archive.

See `scripts/backups.md` for the script + retention details.

---

## Verifying it works

```bash
# Container healthy
docker ps | grep uptime-kuma

# Admin UI reachable
curl -I http://192.168.100.50:3001

# On the homelab network with the services it monitors
docker network inspect homelab --format '{{range .Containers}}{{.Name}} {{end}}'
# expect to include: uptime-kuma + the services being monitored
```

The real validation is the break/fix drill: `docker stop pihole`, watch Pi-hole monitors flip red within ~60s, get the Telegram notification, then `docker start pihole`. The drill was executed on 2026-06 and the timing + alert pattern is documented in `services/pihole/Pihole.md`.

---

## Known limitations

- **Single monitoring point.** If Kuma dies, monitoring dies — nothing watches the watcher. Phase 1 with always-on infrastructure makes this less painful but doesn't eliminate it.
- **VM intermittent → monitoring intermittent.** Same constraint that affects Pi-hole's DNS role. Monitoring only works during the ~3 hours/day the VM is up. Phase 1 fixes this.
- **One notification channel.** Telegram only. If Telegram is down or my phone is dead, alerts are silent. Email or ntfy as a secondary channel would be a Phase 1+ addition.
- **No status page exposed.** Could publish a public status page later as portfolio polish, not urgent.
- **Admin UI on raw `:3001`.** Could be proxied behind NPM as `uptime.home` later. Cosmetic.

---

## History

### 2026-06 — Initial deployment + 7 monitors + first break/fix drill

Deployed Kuma on the `homelab` network with a single named volume and the upstream healthcheck. Created an admin account, set up the Telegram bot, configured 7 monitors covering each service plus DNS, the host, and an external dependency.

Hit one gotcha on the DNS monitor (resolver field needs a raw IP, not a container name — Kuma's DNS monitor doesn't use Docker DNS to find its resolver). Fixed by switching the resolver from `pihole` to `192.168.100.50`. Captured the lesson in this doc's monitor design section.

Ran the break/fix drill the same day — `docker stop pihole`, watched the two Pi-hole monitors go red within ~60s, Telegram delivered alerts to phone, recovered with `docker start pihole`, monitors flipped back green within ~90s. The other 5 monitors stayed green throughout, correctly isolating the failure scope. Details and screenshots in `services/pihole/Pihole.md`.
