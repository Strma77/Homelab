# Audiobookshelf

Self-hosted audiobook server running in Docker on an Ubuntu Server VM, accessible remotely via Tailscale.

---

## Networking Configuration

The Ubuntu Server VM uses a **bridged network adapter**, allowing it to behave as a first-class host on the LAN.

### IP Addressing

| Setting | Value |
|---------|-------|
| Interface | `enp0s3` |
| Static IP | `192.168.100.50/24` |
| Gateway | `192.168.100.1` |
| DNS | `1.1.1.1`, `8.8.8.8` |

A static IP ensures consistent addressing for VPN endpoints and service access.

### Netplan Configuration

`/etc/netplan/50-cloud-init.yaml`:

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp0s3:
      dhcp4: no
      addresses: [192.168.100.50/24]
      routes:
        - to: default
          via: 192.168.100.1
      nameservers:
        addresses: [1.1.1.1, 8.8.8.8]
```

```bash
sudo netplan apply
```

> **Note:** DNS must be explicitly set in Netplan. Without it, Docker image pulls fail and Tailscale throws DNS errors on startup.

---

## Environment Constraints

Deployed on a residential network behind an **ISP-provided ZTE F8648P XGS-PON ONT** with no access to NAT, port forwarding, or firewall configuration. Inbound connections from the public internet are not possible.

All remote access must use outbound-only or NAT-traversal-friendly solutions.

---

## Remote Access — Tailscale

### Why Tailscale

Traditional VPN hosting requires inbound port forwarding which the ISP ONT blocks. Tailscale works via outbound-only connections, requiring zero router configuration.

### Installation

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --accept-dns=false
tailscale status
```

> **Critical:** Always use `--accept-dns=false`. Without it, Tailscale overrides system DNS and breaks connectivity after reboot.

### Client Setup

- Install Tailscale on all client devices (phone, laptop, etc.)
- Authenticate under the same account
- Confirm the VM shows a green dot in the Tailscale app before attempting to connect

### Verify

```bash
tailscale status        # VM should show with 100.x.x.x IP
curl http://100.x.x.x:13378  # Should return HTML if Audiobookshelf is running
```

---

## Storage Architecture

Audiobooks are stored on the **host machine's SSD** as a single source of truth. The VM accesses them via a VirtualBox shared folder — no duplication, no sync overhead.

### Host Setup

Create the directory on the host:

```bash
mkdir ~/audiobooks
```

In **VirtualBox GUI** → VM Settings → Shared Folders → Add:

| Setting | Value |
|---------|-------|
| Folder Path | `~/audiobooks` |
| Folder Name | `audiobooks` |
| Mount Point | *(leave empty)* |
| Make Permanent | ✅ |
| Make Global | ❌ |
| Read-only | ❌ |

### VM Setup

```bash
sudo mkdir -p /mnt/audiobooks
```

Add to `/etc/fstab` for persistence:

```
audiobooks  /mnt/audiobooks  vboxsf  defaults,uid=1000,gid=1000  0  0
```

Mount immediately without rebooting:

```bash
sudo mount -a
ls /mnt/audiobooks  # should return contents or empty with no errors
```

> **Note:** VirtualBox auto-mount is unreliable. Always use `/etc/fstab`. Guest Additions must be installed for shared folders to work — verify with `lsmod | grep vboxguest`.

---

## Deployment

Deployed via `docker-compose.yml` in this directory.

From the VM:
```bash
cd ~/homelab/services/audiobookshelf
docker compose up -d
docker ps   # verify (healthy) status appears after ~40s
```

The compose stack uses:
- Named volumes for `/config` and `/metadata` (Docker-managed app state)
- Bind mount `/mnt/audiobooks` → `/audiobooks` (user-managed media library)
- Custom `homelab` bridge network for future inter-service DNS
- HTTP healthcheck via `wget --spider http://localhost/` (40s start_period)
- `restart: unless-stopped` so the container survives VM reboots

See `docker-compose.yml` in this directory for the full definition.

---

## Access

The service is reachable only through Nginx Proxy Manager by hostname:

```text
http://audiobookshelf.home
```

Direct access via `http://192.168.100.50:13378` was removed in the localhost-bind refactor (see History). The container's port 13378 is now bound to `127.0.0.1` on the VM, so only NPM — which talks to the container by name on the `homelab` Docker network — can reach it. External LAN devices have no path to the container directly.

For initial library setup, do it after NPM is configured to route `audiobookshelf.home` and your DNS knows where that hostname lives (Pi-hole or `/etc/hosts`).

### Mobile / remote access

- On the LAN: `http://audiobookshelf.home` (requires DNS pointing at the VM)
- Via Tailscale: `http://100.x.x.x:13378` no longer works after the refactor; use `http://audiobookshelf.home` once Tailscale clients resolve `.home` (Phase 1 work — configure Tailscale MagicDNS or per-device DNS)

---

## Architecture Overview

```
[Mobile / Desktop client]
        │
   Tailscale (encrypted mesh, 100.x.x.x)
        │
        ▼
[Ubuntu Server VM — 192.168.100.50]
        │
   docker compose stack (network: homelab)
        │
        ▼
┌──────────────────────────────────────┐
│  audiobookshelf:latest  (port 13378) │
│  healthcheck: wget /, every 30s      │
└──┬───────────────┬──────────────┬────┘
   │               │              │
   ▼               ▼              ▼
[named vol]   [named vol]    [bind mount]
 _config       _metadata      /mnt/audiobooks
                                  │
                                  ▼
                          vboxsf shared folder
                                  │
                                  ▼
                          [Host SSD — ~/audiobooks]
```

---

## Key Design Decisions

1. **Tailscale over traditional VPN** — no port forwarding needed, works behind locked ISP equipment
2. **Shared folders over file duplication** — single source of truth on host SSD
3. **Dockerized deployment** — easy updates, isolated, portable

---

## Limitations

- VM and service depend on host uptime
- Tailscale must be active on all client devices
- No HTTPS — acceptable since Tailscale encrypts the tunnel end-to-end

---

## Future Improvements

- Migrate to dedicated always-on hardware
- Reverse proxy via Nginx Proxy Manager (Phase 0) with HTTPS through internal CA in Phase 3
- Automate library rescans

---

## History

### 2026-06 — Localhost-bind refactor

Closed the documented Docker/UFW bypass for this service. Container port binding changed from `0.0.0.0:13378:80` to `127.0.0.1:13378:80` in the compose file. External LAN clients can no longer reach Audiobookshelf directly by `IP:port`; the only path in is now through Nginx Proxy Manager by hostname.

The refactor exploits a property of the `homelab` Docker network we built earlier: NPM and Audiobookshelf both live on it and resolve each other by container name. So even with the host port bound to loopback only, NPM still reaches the container on `audiobookshelf:80` over the bridge network — no host port hop required.

**Verified end-to-end:** direct `192.168.100.50:13378` access fails with connection refused from both the VM and a separate LAN client. Hostname access via `audiobookshelf.home` continues to serve content through NPM. Uptime Kuma's HTTP monitor (which also uses container-name routing on the homelab network) stayed green through the container recreate.

UFW rule `13378/tcp ALLOW` was removed since the port is no longer externally exposed and the rule documented nothing real.

Compose diff:
```text
- "13378:80"
+ "127.0.0.1:13378:80"
```

This is the pattern other user-facing services (Uptime Kuma, Homarr) can adopt incrementally. Admin tooling (Pi-hole admin UI, NPM admin, Portainer) is deliberately left directly accessible as break-glass for diagnosing outages of the routing or DNS layers themselves.


### 2026-05-09 — Migrate from `docker run` to `docker-compose.yml`
**Why:** Original deployment was a hand-typed `docker run` invocation copied from documentation without full understanding. Not version-controllable, not reproducible, no healthcheck, bind mounts everywhere.

**Changes:**
- Replaced `docker run` with declarative `docker-compose.yml` in repo
- Switched `/config` and `/metadata` to named volumes (Docker-managed)
- Kept `/audiobooks` as bind mount to `/mnt/audiobooks` (user-managed media)
- Added custom `homelab` bridge network (foundation for inter-service DNS)
- Added HTTP healthcheck via `wget` with 40s start_period
- Migrated existing config/metadata into the new named volumes via `cp -a`

**Validation:** Container reports healthy, library and listening progress preserved across migration. Old container kept renamed as `audiobookshelf_old` for 24h rollback window.

### 2026-03-01 — Initial deployment
Hand-typed `docker run` deployment with bind mounts to `~/audiobookshelf/config` and `~/audiobookshelf/metadata`. Audiobooks served from `/mnt/audiobooks` via VirtualBox shared folder. Remote access via Tailscale.

(Deployment retroactively replaced 2026-05; see migration entry above.)

---

## Lessons Learned

| Issue | Fix |
|-------|-----|
| VirtualBox auto-mount unreliable | Use `/etc/fstab` instead |
| Docker pull fails on fresh VM | Set explicit DNS in Netplan (`8.8.8.8`, `1.1.1.1`) |
| Tailscale DNS errors on reboot | Use `--accept-dns=false` on `tailscale up` |
| Tailscale IP unreachable from phone | Tailscale app must be active and connected on the client device |
| Service accessible locally but not via Tailscale | Confirm VM shows green dot in Tailscale app on client |
