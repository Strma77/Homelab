# Navidrome

Self-hosted music streaming server running in Docker on an Ubuntu Server VM, accessible remotely via Tailscale. Functions as a personal Spotify — library player with Subsonic API support for mobile clients.

---

## Architecture Overview

```
[Mobile Client + Tailscale]
        ↓
[Ubuntu Server VM (100.x.x.x)]
        ↓
[Docker: Navidrome :4533]
        ↓
[/mnt/songs (vboxsf)]
        ↓
[Host PC SSD – ~/Music/Songs]
```

---

## Music Pipeline

Songs are acquired on the host machine using `musiq.py` — a script that wraps yt-dlp and ffmpeg — and stored in `~/Music/Songs`. The VM accesses this folder via a VirtualBox shared folder mounted at `/mnt/songs`.

### Tools

| Tool   | Purpose                                               |
| ------ | ----------------------------------------------------- |
| yt-dlp | Downloads audio from YouTube in opus format           |
| ffmpeg | Writes clean artist/title metadata tags post-download |

### Audio Format

Opus is used because:

- YouTube sources are already lossy — FLAC containers provide no quality benefit
- Opus delivers better quality than mp3 at equivalent bitrates
- Smaller file sizes than mp3 at equivalent quality

### Downloading Songs

```bash
# interactive mode
python3 musiq.py

# direct args
python3 musiq.py "Artist" "Song Title"

# with specific YouTube URL
python3 musiq.py "Artist" "Song Title" "https://youtu.be/..."
```

The script searches YouTube automatically, downloads opus audio, writes correct artist/title tags via ffmpeg, and saves to `~/Music/Songs/Artist/Song.opus`.

### Downloading in Bulk

Generate a list of commands from a spreadsheet or text file in the format:

```
python3 musiq.py "Artist 1" "Song 1"
python3 musiq.py "Artist 2" "Song 2"
```

Then run the whole file at once:

```bash
bash download_commands.txt
```

### Installing / Updating yt-dlp

The apt version of yt-dlp lags behind and will cause 403 errors from YouTube. Always install directly from GitHub:

```bash
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp
hash -r
yt-dlp --version
```

---

## Storage Architecture

Music is stored on the **host machine's SSD** as a single source of truth.

### Host Setup

```bash
mkdir ~/Music/Songs
```

In **VirtualBox GUI** → VM Settings → Shared Folders → Add:

| Setting        | Value           |
| -------------- | --------------- |
| Folder Path    | `~/Music/Songs` |
| Folder Name    | `music`         |
| Mount Point    | _(leave empty)_ |
| Make Permanent | ✅              |
| Make Global    | ❌              |
| Read-only      | ❌              |

### VM Setup

```bash
sudo mkdir -p /mnt/songs
```

Add to `/etc/fstab`:

```
music  /mnt/songs  vboxsf  defaults,uid=1000,gid=1000  0  0
```

Mount immediately:

```bash
sudo mount -a
ls /mnt/songs
```

---

## Navidrome Deployment

```bash
mkdir -p ~/navidrome/data

docker run -d \
  --name navidrome \
  --restart unless-stopped \
  -p 4533:4533 \
  -e ND_SCANSCHEDULE=1h \
  -e ND_LOGLEVEL=info \
  -v /mnt/songs:/music:ro \
  -v ~/navidrome/data:/data \
  deluan/navidrome:latest
```

> **Note:** The shared folder must be mounted at `/mnt/songs` on the VM and mapped to `/music` inside the container. Navidrome scans `/music` by default.

Verify:

```bash
docker ps
```

### Initial Setup

1. Open `http://192.168.100.50:4533` in browser
2. Create admin account
3. Trigger a library scan — **Settings → Library → Scan**
4. For remote access use `http://100.x.x.x:4533` (Tailscale IP)

### Mobile Client

Navidrome exposes a Subsonic-compatible API. Recommended clients:

| Client     | Platform | Cost |
| ---------- | -------- | ---- |
| Symfonium  | Android  | Paid |
| Ultrasonic | Android  | Free |

Connect using your Tailscale IP and Navidrome admin credentials.

---

## Remote Access

Same Tailscale setup as Audiobookshelf. See `Audiobookshelf.md` for full Tailscale configuration.

Access Navidrome remotely at `http://100.x.x.x:4533` with Tailscale active on the client device.

---

## Limitations

- VM and service depend on host uptime
- Tailscale must be active on all client devices
- No HTTPS — acceptable since Tailscale encrypts the tunnel
- yt-dlp requires periodic manual updates — apt version lags behind
- Regional tracks often unavailable on YouTube — require manual download with URL

---

## Future Improvements

- Migrate to dedicated always-on hardware
- Add reverse proxy (Caddy/Nginx) with HTTPS
- Set up Symfonium mobile client

---

## Lessons Learned

| Issue                                           | Fix                                                                 |
| ----------------------------------------------- | ------------------------------------------------------------------- |
| Navidrome shows no music after deploy           | Map shared folder to `/music` inside container, not `/songs`        |
| yt-dlp 403 errors                               | apt version outdated — install latest directly from GitHub releases |
| yt-dlp shell still uses old binary after update | Run `hash -r` to clear shell path cache                             |
| Docker pull fails on fresh VM                   | Set explicit DNS in Netplan before deploying                        |
