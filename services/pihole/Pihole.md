# Pi-hole

**What:** Local DNS server + ad/tracker blocking for the homelab.
**Why:** Resolves `.home` hostnames so NPM can route by name, blocks ad/tracker domains network-wide as a bonus.
**Where:** Container `pihole` on the shared `homelab` network. DNS bound to the VM's LAN IP, admin UI on `:8888`.
**Status:** Running and functional. NOT my desktop's daily-driver DNS yet — see "On-demand only" below.

---

## Why it exists

NPM solved the routing problem (`audiobookshelf.home` → the right container) but it didn't solve the resolution problem. Something has to tell devices that `audiobookshelf.home` actually means `192.168.100.50` in the first place.

Before Pi-hole, that was a temporary line in my desktop's `/etc/hosts`. Works for one machine, doesn't scale to phones, TVs, or the future stack of `.home` services.

Pi-hole becomes the answer to "what IP is this hostname?" for the whole homelab, and as a side effect blocks the long list of known ad and tracker domains for any device using it.

The split is clean:
- **Pi-hole** answers "where is it?"
- **NPM** answers "which service?"

Neither one does the whole job alone.

---

## Architecture

```text
Device on LAN
   │
   ▼
DNS query: "audiobookshelf.home?"
   │
   ▼
Pi-hole (192.168.100.50:53)
   │
   ├──── local record? ──── Yes → return 192.168.100.50
   │
   └──── ad/tracker domain? ──── Yes → return blackhole / NXDOMAIN
   │
   └──── neither? ──── forward to upstream DNS (default Google 8.8.8.8)
```

For `.home` hostnames Pi-hole answers from its own local DNS records. For everything else it forwards to upstream resolvers and blocks anything on its blocklists along the way.

---

## Deployment

Defined in the Compose file next to this doc.

### The port-53 problem

systemd-resolved already listens on port 53 — but only on the loopback stub addresses (`127.0.0.53` and `127.0.0.54`). The VM's actual LAN IP (`192.168.100.50:53`) is free.

So instead of disabling systemd-resolved, I bound Pi-hole's port 53 to the LAN IP specifically:

```yaml
ports:
    - "192.168.100.50:53:53/tcp"
    - "192.168.100.50:53:53/udp"
```

Two DNS resolvers coexist on the same machine because they bind different addresses. systemd-resolved keeps doing its job on loopback for the VM's own DNS; Pi-hole serves the LAN.

This is the `IP:HOSTPORT:CONTAINERPORT` syntax — first time I needed it. Worth knowing.

### Admin UI on a non-standard host port

Pi-hole's admin UI runs on container port 80, but NPM already owns host port 80. Picked 8888 (8080 was reserved for an unrelated uni project running on the desktop, didn't want a mental collision):

```yaml
- "8888:80"
```

Eventually this will sit behind NPM as `pihole.home` so users never hit a raw port.

### Shared external network

Same pattern as NPM:

```yaml
external: true
```

Pi-hole joins the existing `homelab` network so future NPM proxy hosts (`pihole.home`) can reach it by container name.

### Persistent storage

```text
pihole_config       /etc/pihole       DNS records, settings, admin pw hash
pihole_dnsmasq      /etc/dnsmasq.d    Custom dnsmasq overrides (empty for now)
```

### Capabilities deliberately NOT granted

Pi-hole's image asks for `CAP_SYS_NICE` (process priority) and `CAP_SYS_TIME` (NTP server mode) and warns when they're missing. I deliberately did not grant them — not using Pi-hole as an NTP server, don't need elevated process priority for a homelab DNS server. The warnings in the logs are harmless.

---

## The password saga

This was the messiest part of the deploy and I want it captured so I don't repeat it.

### Round 1: Pi-hole v6 env var rename

I set `WEBPASSWORD=...` in `.env` (per most online tutorials) and watched the container start. The admin UI rejected my password.

The container logs revealed:
[i] No password set in environment or config file, assigning random password: gkLK-8go

Pi-hole v6 silently ignores the legacy `WEBPASSWORD` env var. The new name is:
FTLCONF_webserver_api_password

Updated `.env` and the compose to use the new name. The lesson: when an image is on a major version that changes config conventions, don't assume the old tutorials apply. Read the official docs for the version actually running.

### Round 2: the bracket trap

When I wrote the new password into `.env`, I copied the format `WEBPASSWORD=<a strong password>` and put my password inside the angle brackets — making the brackets part of the password itself.

Login kept failing. I was typing the password without brackets, but Pi-hole had stored it with them.

Root cause: `<...>` in instructions and templates means "placeholder, put your value here." It is not literal syntax. I treated it as syntax.

The lesson: in any config file, brackets, quotes, and other punctuation around a placeholder are part of the placeholder convention, not the value.

### Round 3: editing .env after `up -d`

After fixing the bracket mistake I edited `.env` again — and the UI still rejected the new password. Reason: I had only edited the file, not recreated the container.

`docker compose restart` doesn't re-read env vars from `.env`. Only `docker compose down` followed by `docker compose up -d` (or `docker compose up -d --force-recreate`) reloads the env block fully. On top of that, Pi-hole stores the hashed password in the `pihole_config` volume — so even a clean restart can keep the old hash unless the volume is recreated.

Clean reset procedure:

```bash
cd ~/homelab/services/pihole
docker compose down
docker volume rm pihole_config pihole_dnsmasq
docker compose up -d
docker logs pihole 2>&1 | grep -iE "password|environment"
```

Look for:
[i] Assigning password defined by Environment Variable
[✓] FTLCONF_webserver_api_password is used

If those show up, the env-supplied password took. If you see "assigning random password" again, the env var isn't reaching the container — diagnose before retrying.

### Round 4: I leaked the password to chat. Twice.

Two separate times I pasted output containing the live password — once from `docker compose config`, once from `xxd` of the env file where I redacted the ASCII column but left the hex untouched (the hex IS the password, just in a different format).

The rule I locked in after this:

* `<redacted>` is a placeholder marker. It is NOT a sanitization technique.
* When sharing output, replace the entire sensitive value with the literal word `REDACTED`.
* Don't get clever. Don't preserve structure. Replace the whole thing.

Both leaked passwords were rotated immediately.

---

## DNS resolution didn't work on first try either

Once I could log in, I added the local DNS record (`audiobookshelf.home → 192.168.100.50`) and ran `dig` from my desktop. It timed out.

Two separate problems were stacked on top of each other.

### Problem 1: UFW was blocking port 53

I had set up UFW with rules for 22 (SSH) and 13378 (Audiobookshelf) but never added 53. UDP DNS packets were dropped at the firewall.

Fix:

```bash
sudo ufw allow 53/tcp comment 'DNS (Pi-hole)'
sudo ufw allow 53/udp comment 'DNS (Pi-hole)'
```

I used `allow`, not `limit`, on purpose. DNS sees high volumes of legitimate queries per second; `limit`'s "6 attempts per 30 seconds" would block real clients almost immediately. Rate-limiting is for auth endpoints, not high-volume protocols.

This also revealed a gap in the hardening doc: nothing tracked which UFW rules were for which service. I added a service-specific UFW rules table to `vm-hardening.md` afterward.

### Problem 2: Pi-hole was refusing "non-local" queries

Even with UFW out of the way, the logs showed:
WARNING: dnsmasq: ignoring query from non-local network 192.168.100.50

Pi-hole's `dns.listeningMode` defaulted to **LOCAL** — only accept DNS queries from local subnets. The UI offers five modes:

| Mode | Behavior |
|------|----------|
| LOCAL (default) | Local subnets only — safer but rejects LAN queries that Docker NATs |
| SINGLE | One interface only |
| BIND | Force-bind to specific interfaces (fragile) |
| **ALL** | Permit all origins, accept on all interfaces — recommended when properly firewalled |
| NONE | Don't manage listening mode at all (manual config) |

I picked **ALL**. The big warning Pi-hole shows ("you could become an open resolver") applies when Pi-hole is publicly reachable on the internet. With UFW gating port 53 to the LAN and the VM behind ISP NAT, "permit all origins" really means "permit my LAN," which is the goal.

### Verifying

```bash
# From desktop
dig @192.168.100.50 audiobookshelf.home +short
# expect: 192.168.100.50

dig @192.168.100.50 google.com +short
# expect: a real Google IP
```

Both worked. The first proves Pi-hole serves the local record. The second proves it correctly forwards external queries upstream.

---

## On-demand only — and why

This is the most important architectural decision in the doc.

After Pi-hole was working I pointed my desktop's DNS at it and the full chain came up — `audiobookshelf.home` resolved via Pi-hole, NPM routed, Audiobookshelf served. End-to-end working.

Then I asked the obvious question: does the VM need to be on constantly for this to work?

It does. **DNS is a 24/7 service.** If your desktop's DNS server is unreachable, every domain you try to resolve hangs or fails. My VM runs maybe 3 hours a day during active homelab work. Pointing my desktop's DNS at it permanently would mean broken internet for 21 hours a day.

Three options:

* **A — Run the VM 24/7.** The right answer eventually. Right now my VM is on a daily-driver desktop, not always-on infrastructure.
* **B — Use a fallback DNS** (`192.168.100.50, 1.1.1.1`). Behavior is resolver-dependent — some try in order (Pi-hole first, fall back if down), others race them in parallel which defeats the point.
* **C — Revert desktop DNS to automatic, use Pi-hole on demand only.** Pi-hole stays available for `dig @192.168.100.50 ...` tests and demos, but isn't responsible for daily browsing.

I picked C. Honest acknowledgment of my constraints: a part-time VM cannot be daily DNS infrastructure for a daily-use desktop.

This is actually a Phase 1 question. The roadmap's Phase 1 ("Stop being someone who runs services and start being someone who builds infrastructure") includes always-on hardware. Once the Proxmox migration happens on a host that stays on, Pi-hole becomes legitimate network-wide DNS and this entire section becomes obsolete.

For now: Pi-hole is **proven functional, documented, and ready** — just not in the request path of my daily browsing.

---

## First-run setup

Hit `http://192.168.100.50:8888/admin` and log in with the password from `.env`.

First task: add a local DNS record under **Settings → All Settings → DNS → Local DNS Records**:

```text
Domain:     audiobookshelf.home
IP Address: 192.168.100.50
```

Future hostnames go here too as services come online.

---

## Backups

`pihole_config` is backed up daily — it holds local DNS records, settings, and the hashed admin password.

Backup verification confirmed:

```text
pihole/pihole-FTL.db
pihole/setupVars.conf
pihole/dhcp.leases
```

`pihole_dnsmasq` is excluded — empty unless I add custom dnsmasq overrides.

See `scripts/backups.md`.

---

## Known limitations

* Not daily-driver DNS until VM is 24/7 (Phase 1)
* Admin UI exposed on raw `:8888` — could be proxied through `pihole.home` later
* `CAP_SYS_NICE` / `CAP_SYS_TIME` warnings in logs (harmless, deliberately not granted)
* Single point of failure for `.home` hostnames once Pi-hole becomes the canonical resolver
* DHCP-DNS control on the ISP-locked ZTE F8648P ONT not yet investigated — needed to make Pi-hole truly network-wide

---

## History

### 2026-06 — Initial deployment

* Deployed Pi-hole container on the shared `homelab` network
* Bound DNS to VM LAN IP (`192.168.100.50:53`) to coexist with systemd-resolved on loopback
* Admin UI on host port `8888`
* Hit the v6 env-var rename, recovered after the bracket-in-password and edit-after-up-d gotchas (with two password leaks along the way — rotated, lesson locked in)
* Added UFW rules for `53/tcp` and `53/udp`
* Set `dns.listeningMode = ALL` to accept LAN queries (UFW gates the port)
* Created first local DNS record (`audiobookshelf.home → 192.168.100.50`)
* Verified end-to-end resolution from desktop
* Chose to revert desktop DNS to automatic and use Pi-hole on demand only until VM is 24/7

## Break/fix drill — 2026-06-06

Deliberately stopped the Pi-hole container to validate the
monitoring + recovery loop on first real exercise.

**Detection (~60s):**
- Pi-hole Web monitor → DOWN, error: `connect EHOSTUNREACH 172.18.0.4:80`
- Pi-hole DNS Resolution → DOWN, error: `queryA ETIMEOUT audiobookshelf.home`
- All other monitors remained UP, correctly isolating the failure
  scope to Pi-hole alone
- Telegram alert delivered to phone within ~1 minute of the stop

**Recovery:**
- `docker start pihole` — container went through health-starting
  → healthy, monitors flipped back to UP within ~90s
- Telegram delivered recovery alerts

**Total time DOWN → UP:** ~2 minutes.

**What the dual error messages confirm:** the two monitors hit
different layers (network reachability and DNS query response),
so the alert pattern tells you the whole container died, not just
one of its services. Useful diagnostic signal embedded in the
monitoring design.
