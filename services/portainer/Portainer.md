# Portainer

**What:** Visual UI for managing the Docker stack on the VM.
**Why:** CLI complement, not replacement. Useful for inspecting state at a glance and demoing the stack to people who aren't terminal-native.
**Where:** Container `portainer` on the `homelab` Docker network, admin UI on `:9000` (HTTP) and `:9443` (HTTPS, self-signed).
**Status:** Running. Admin account created on first start.

> ⚠️ This doc was drafted with AI assistance during Phase 0 close-out. Rewrite owed by **2026-08-31** — see `docs/TODO.md` documentation debt entry.

---

## Why it exists

Honest framing: I'm CLI-fluent on Docker by now (logs, exec, inspect, network inspect, volume ls, the whole set). Portainer is not a replacement for any of that. What it does provide:

- A glance-view of all 6 containers at once with state, ports, image, network — useful when context-switching back to the homelab after a few days away
- A clickable path to logs without remembering the syntax (`docker logs -f --tail 100 ...`)
- An interface non-technical viewers can follow when I'm demoing the stack

That's it. If Portainer disappeared tomorrow I'd lose the GUI but not the capability. That's a feature, not a problem.

---

## Deployment

Defined in `docker-compose.yml` next to this doc. Standard pattern — image, container name, two port publishes, restart policy, the external `homelab` network, one named volume on `/data`. Plus one piece that's different and worth understanding.

### The Docker socket bind mount

Portainer's compose has this line in its volumes:

```yaml
- /var/run/docker.sock:/var/run/docker.sock
```

This is a **bind mount**, not a named volume. It maps the host's Docker daemon socket directly into the container so Portainer can call the Docker API. Without it, Portainer starts but shows no containers — it has no way to talk to Docker.

### Security implication

The Docker socket is the API endpoint for the Docker daemon, which runs as root. Anything that can talk to the socket can:

- Start, stop, and remove any container
- Mount arbitrary host paths into new containers
- Run new containers with `--privileged` or `--pid=host`

In other words, the socket is effectively a root shell on the host for anyone with access to it. Mounting it into Portainer gives Portainer that same level of access. This is **not optional** for Portainer to do its job, but it does mean:

- Portainer's admin account is functionally the host's root account in disguise. Treat the password accordingly.
- Portainer should never be exposed publicly without serious auth in front. Internal-only on the LAN is fine; on the open internet it would be a top-tier compromise target.
- The break-glass decision (admin tools not behind NPM, see `vm-hardening.md`) accepts that internal LAN access is sufficient. If the LAN itself is compromised, the homelab has bigger problems than Portainer.

---

## First-run setup

**Important:** Portainer locks out admin account creation after roughly 5 minutes of first start if no account exists. This is a security feature — prevents someone else from claiming the admin slot if you deploy and walk away. So:

1. `docker compose up -d`
2. Immediately browse to `http://192.168.100.50:9000`
3. Create the admin account with a strong password and save it
4. If the lockout did trigger, restart the container to reset the timer

Once the account exists, the lockout no longer applies.

---

## Backups

The `portainer_data` named volume is in the daily backup. It contains:

- `portainer.db` — SQLite database with the admin account, settings, environment definitions
- `portainer.key` and `portainer.pub` — JWT signing keys
- `certs/` — the self-signed TLS cert for `:9443`
- `chisel/` — agent communication keys (unused on a single-host setup but the path exists)

Verified present in the most recent archive.

---

## Verifying it works

```bash
docker ps | grep portainer
curl -I http://192.168.100.50:9000
docker network inspect homelab --format '{{range .Containers}}{{.Name}} {{end}}'
```

The genuine check is in the browser — log in, see all 6 homelab containers in the list with state, images, networks. If Portainer can see them, the socket mount is working. If not, the socket mount is missing or broken.

---

## Known limitations

- **Socket mount = root-on-host.** Accepted trade-off for the functionality.
- **No healthcheck defined.** Container shows "running" rather than "(healthy)". Portainer's image has `wget`; a healthcheck could be added later. Not blocking — the container's own startup either works or doesn't, no gray zone.
- **Admin UI deliberately not behind NPM.** Break-glass pattern, same as the Pi-hole and NPM admin UIs. If NPM itself is broken, I want Portainer reachable to diagnose.
- **Self-signed cert on `:9443` triggers browser warnings.** Phase 3 internal CA work eventually fixes this.

---

## History

### 2026-06 — Initial deployment

Deployed Portainer via compose. The interesting failure: my first compose draft was missing the Docker socket bind mount entirely — only the named volume was declared. The container would have started and shown an empty container list because it had no way to reach the Docker API. Caught in review before `up -d`, added the bind mount, verified the resulting `docker compose config` showed `type: bind` for the socket.

Lesson: when the only "new concept" of a deployment is one specific thing (here, the socket mount), that's exactly where the bug will land. Pre-deploy review caught it.

Created the admin account on first browse and confirmed Portainer could see all 5 homelab containers running at that point (audiobookshelf, nginx-manager, pihole, uptime-kuma, portainer itself).
