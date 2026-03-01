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

## Audiobookshelf Deployment

```bash
mkdir -p ~/audiobookshelf/config ~/audiobookshelf/metadata

docker run -d \
  --name audiobookshelf \
  --restart unless-stopped \
  -p 13378:80 \
  -v /mnt/audiobooks:/audiobooks \
  -v ~/audiobookshelf/config:/config \
  -v ~/audiobookshelf/metadata:/metadata \
  ghcr.io/advplyr/audiobookshelf:latest
```

Verify it's running:

```bash
docker ps
```

### Initial Setup

1. Open `http://192.168.100.50:13378` in browser
2. Create admin account
3. Add library → set folder to `/audiobooks` → scan
4. For remote access use `http://100.x.x.x:13378` (Tailscale IP)

### Mobile App

- Install Audiobookshelf app
- Add server via Tailscale IP: `http://100.x.x.x:13378`
- Ensure Tailscale is active on the device before connecting

---

## Architecture Overview

```
[Mobile Device + Tailscale]
        ↓
[Ubuntu Server VM (100.x.x.x)]
        ↓
[Docker: Audiobookshelf :13378]
        ↓
[/mnt/audiobooks (vboxsf)]
        ↓
[Host PC SSD – ~/audiobooks]
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
- Add reverse proxy (Caddy/Nginx) with HTTPS
- Automate library rescans

---

## Lessons Learned

| Issue | Fix |
|-------|-----|
| VirtualBox auto-mount unreliable | Use `/etc/fstab` instead |
| Docker pull fails on fresh VM | Set explicit DNS in Netplan (`8.8.8.8`, `1.1.1.1`) |
| Tailscale DNS errors on reboot | Use `--accept-dns=false` on `tailscale up` |
| Tailscale IP unreachable from phone | Tailscale app must be active and connected on the client device |
| Service accessible locally but not via Tailscale | Confirm VM shows green dot in Tailscale app on client |
