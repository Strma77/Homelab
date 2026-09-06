# Roadmap

**What:** Self-hosted static page showing the homelab's phase-by-phase learning roadmap and checkpoint progress.
**Why:** Single source of truth for "what's done / what's next" that lives on the lab itself, not just on GitHub Pages. A visible progress board keeps the phases honest.
**Where:** Container `roadmap` (nginx:alpine) on the `homelab` Docker network, served on `:8080`.

---

## Deployment

Defined in `docker-compose.yml` next to this doc. Minimal static-file server:

```yaml
image: nginx:alpine
ports: "8080:80"
volumes: ./html:/usr/share/nginx/html:ro   # read-only mount of the html dir
networks: homelab (external)
```

The page itself is `html/index.html` — a single self-contained HTML/CSS file (no build step, no JS framework). Deploy:
```bash
cd ~/homelab/services/roadmap
docker compose up -d
curl -I http://10.10.20.50:8080
```

---

## Updating progress

**Checkbox state is hand-edited in `html/index.html`.** There's no app, no database — a checked item is a class/markup change in the HTML. When a phase task is genuinely done (verified, not aspirational), edit the markup, commit, and the container serves the new file on next request (the mount is read-only and live — no rebuild needed).

> Keep it honest: a checked box here should mean *done and verified*, the same bar as the TODO. Checkbox theater on the roadmap is worse than a stale TODO because it looks official.

---

## Known limitations

- **Manual checkbox editing** — no dynamic state; every update is a hand edit + commit.
- **`:latest` nginx tag** — fine for a static server, but pin a version if a pull ever breaks it.
- **Not behind NPM** — served on raw `:8080`. Could be proxied as `roadmap.home` later. Cosmetic.

---

## History

### 2026-09 — Self-hosted on the Beelink
Moved the roadmap from GitHub Pages (`strma77.github.io`) to a self-hosted nginx container so it lives on the lab. Compose + html committed to the repo.
