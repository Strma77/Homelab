# Nginx Proxy Manager

**What:** Reverse proxy used to access homelab services by hostname instead of IP:port.
**Why:** Solves the "which service was on which port?" problem and gives me a single place to manage routing, SSL, and access control later.
**Where:** Container `nginx-manager` on the shared `homelab` Docker network, exposing ports `80`, `443`, and `81`.
**Status:** Running. First proxy host (`audiobookshelf.home`) configured and working. SSL intentionally postponed.

---

## Why it exists

Before NPM, every service was reached by IP and port:

```text
192.168.100.50:13378
192.168.100.50:3000
192.168.100.50:8080
```

Fine with one or two services. Annoying past that — every new app meant another port to remember and document.

NPM fixes it by putting everything behind one reverse proxy. Hostnames instead of ports:

```text
audiobookshelf.home
jellyfin.home
grafana.home
```

From here on, new web services attach to the shared Docker network and get exposed through NPM. Direct `IP:port` access becomes the fallback, not the norm.

---

## Architecture

NPM sits between clients and backend containers.

```text
Browser
   │
   ▼
DNS Resolution
(Pi-hole or /etc/hosts)
   │
   ▼
audiobookshelf.home
   │
   ▼
Nginx Proxy Manager
(:80 / :443)
   │
   ▼
Docker Internal DNS
(container name lookup)
   │
   ▼
audiobookshelf:80
   │
   ▼
Audiobookshelf Container
```

The piece that matters: Docker's built-in DNS. Containers on the same custom network reach each other by container name, no static IPs.

---

## Deployment

Defined in the Compose file next to this doc.

The first Compose draft did NOT work. Three separate YAML mistakes before the container ever started:

* Container name typo (`ngins-proxy-manager`)
* Mis-indented `networks:` section
* Duplicate `networks:` and `volumes:` declarations — the external network definition got nested inside the service instead of at top level

None of these were Docker problems. They were YAML structure problems. `docker compose config` caught all three before I ever ran `up -d`.

Lesson: always `docker compose config` before `docker compose up -d`.

---

### Shared external network

The `homelab` network is declared as:

```yaml
external: true
```

because it already exists (created by the Audiobookshelf compose). NPM joins the existing network instead of making its own — which is what lets it talk to backend containers by name.

---

### Persistent storage

Two named volumes:

```text
nginx-manager_data
nginx-manager_CertStorage
```

`nginx-manager_data` holds the important state:

* SQLite database
* Proxy host definitions
* JWT signing keys
* Nginx configuration
* User accounts and settings

`nginx-manager_CertStorage` will hold Let's Encrypt certificates and renewal data once SSL is enabled. Empty for now.

---

### Healthcheck

```bash
curl -f -s http://localhost:81
```

against the admin UI.

My first attempt was broken — I mixed `curl` with `wget` flags:

```bash
curl --no-verbose --tries=1 --spider   # ← these are wget flags
```

After fixing, I verified `curl` actually exists in the image:

```bash
docker exec nginx-manager which curl
```

Audiobookshelf already taught me that a healthcheck is useless if the tool isn't installed. Apply the lesson on the next service, not the one that taught it.

---

### Port mappings

```text
80:80      HTTP traffic for proxied services
443:443    HTTPS (reserved, no SSL yet)
81:81      NPM admin UI
```

---

## First-run setup

Default credentials:

```text
Email:    admin@example.com
Password: changeme
```

NPM forces a credential change on first login. Default creds are public knowledge — change them immediately. Same logic as the SSH hardening doc.

---

## Adding a proxy host

Example: exposing Audiobookshelf through NPM.

### Proxy Host Configuration

```text
Domain Names:           audiobookshelf.home
Scheme:                 http
Forward Hostname / IP:  audiobookshelf
Forward Port:           80
```

The thing that finally made Docker networking click: the forward destination is NOT what users see externally (`192.168.100.50:13378`). NPM and Audiobookshelf already share the `homelab` network, so from NPM's perspective the destination is:

```text
audiobookshelf:80
```

The hostname is the container name. The port is the container's *internal* port (Audiobookshelf listens on 80 inside the container — the 13378 in `docker ps` is just the host-side mapping). Docker handles the DNS lookup because both containers are on the same network.

### Recommended toggles

```text
Block Common Exploits:  ON
Websockets Support:     ON
Cache Assets:           OFF
```

Websockets matters specifically for Audiobookshelf — it uses persistent connections for playback sync and progress updates. Without it the app loads but behaves weirdly.

### DNS requirement

The hostname needs to resolve to the NPM host. Before Pi-hole was deployed, I used a temporary entry in the desktop's `/etc/hosts`:

```text
192.168.100.50 audiobookshelf.home
```

Once Pi-hole is up, the record moves there and the hosts hack goes away.

---

## SSL — deliberately postponed

I wanted HTTPS from day one but the ISP-provided ZTE F8648P ONT blocks port forwarding, which kills Let's Encrypt's HTTP-01 challenge before it starts.

Self-signed certs were on the table briefly. Rejected — clicking through browser warnings every day builds the wrong habits and creates warning fatigue.

Plan: DNS-challenge Let's Encrypt with a real domain in Phase 3. That avoids the port-forwarding problem entirely.

For now: HTTP only, internal LAN/Tailscale only. The `nginx-manager_CertStorage` volume exists empty so the migration to HTTPS later doesn't touch storage.

---

## The Docker/UFW bypass — what NPM eventually helps solve

Full details in `vm-hardening.md`.

Current state — Docker publishes ports straight to `0.0.0.0` and installs its own nftables rules that sit in front of UFW's:

```text
Container ──▶ 0.0.0.0:PORT
```

UFW does not protect Docker-published ports. Awareness now, real fix later.

The fix is to bind backend services to localhost only and expose them through NPM:

```text
Container ──▶ 127.0.0.1:PORT ──▶ NPM ──▶ Clients
```

Then:

* UFW genuinely protects the host
* Backend apps are unreachable except through NPM
* NPM becomes the security boundary, not just a routing convenience

### Status: implemented for Audiobookshelf (2026-06)

The pattern was applied to Audiobookshelf in June 2026:

```text
audiobookshelf
   │
   ▼
127.0.0.1:13378  (loopback only — no LAN reachability)
   │
   ▼ via the homelab Docker network (container name lookup)
   │
NPM (port 80)
   │
   ▼
Clients (hostname: audiobookshelf.home)
```

Result: external LAN access to Audiobookshelf is no longer possible by port. UFW's enforcement actually protects this service now — there's no Docker bypass to undermine it because Docker isn't binding to any externally-reachable interface. NPM is the genuine security boundary, not just a routing convenience.

The pattern can be adopted incrementally for other user-facing services. Admin interfaces (NPM `:81`, Portainer `:9000`, Pi-hole `:8888`) are deliberately left directly accessible as break-glass — if NPM itself or the DNS layer is broken, you want to reach the admin UIs without depending on the broken thing. That's a deliberate trade-off, not an oversight.

See `security/vm-hardening.md` for the per-service UFW + binding table.

---

## Verifying it works

Container is healthy:

```bash
docker ps
# expect: nginx-manager ... Up X (healthy)
```

Admin UI responds:

```bash
curl http://192.168.100.50:81
# expect: HTML response
```

Proxy routing:

1. Make `audiobookshelf.home` resolve to `192.168.100.50` (hosts file or Pi-hole)
2. Open `http://audiobookshelf.home`
3. Audiobookshelf loads through NPM, no `:13378` needed

Both containers on the same network:

```bash
docker network inspect homelab --format '{{range .Containers}}{{.Name}} {{end}}'
# expect: audiobookshelf nginx-manager
```

---

## Backups

`nginx-manager_data` is backed up daily. It holds:

* Proxy host definitions
* SQLite database
* JWT signing keys
* Nginx configuration
* User accounts and settings

Backup verification confirmed the presence of:

```text
database.sqlite
keys.json
proxy_host/
proxy_host/1.conf
```

`nginx-manager_CertStorage` is excluded — empty until SSL.

See `scripts/backups.md` for the backup implementation.

---

## Known limitations

* No SSL yet
* Container ports still published on `0.0.0.0`
* Admin UI exposed directly on `:81` (could be proxied through `nginx-manager.home` eventually)
* NPM is a single point of failure — if it dies, hostname-based access stops working

Not catastrophic — services are still reachable on their direct IP:port if NPM dies.

---

## History

### 2026-06 — Initial deployment

* Deployed NPM container
* Attached to the shared `homelab` network
* Configured persistent volumes
* Fixed multiple YAML structure mistakes before the first successful `up -d`
* Added and verified healthcheck (after fixing wget-flags-in-curl mistake)
* Created first proxy host (`audiobookshelf.home`)
* Verified hostname-based routing end-to-end
* Deferred SSL pending DNS-challenge implementation in Phase 3
