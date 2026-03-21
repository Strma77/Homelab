# HomeLab

This repository documents my hands-on learning in building and operating a self-hosted homelab on personal hardware.

The focus is on **understanding infrastructure through practice**, including:

- Linux system administration
- Virtualization on a single host
- Dockerized self-hosted services
- Networking fundamentals and real-world constraints
- Security considerations for private services

This is not a production environment. It is a learning-focused lab shaped by actual limitations such as ISP-controlled networking equipment and a single-machine setup.

---

## Repository Structure

```
homelab/
├── README.md
├── workstation-setup.md
└── services/
    ├── audiobookshelf/
    │   └── Audiobookshelf.md
    └── navidrome/
        ├── Navidrome.md
        └── scripts/
            └── musiq.py
```

---

## Services

### Audiobookshelf

Self-hosted audiobook server accessible remotely via Tailscale mesh VPN. Stores audiobooks on the host SSD, served to the VM via VirtualBox shared folders, containerized with Docker.

→ [Audiobookshelf.md](services/audiobookshelf/Audiobookshelf.md)

### Navidrome

Self-hosted music streaming server with Subsonic API support for mobile clients. Includes a music acquisition script using yt-dlp and ffmpeg for downloading and tagging songs from YouTube.

→ [Navidrome.md](services/navidrome/Navidrome.md)

---

## Infrastructure

All services run inside a single Ubuntu Server 24.04.4 LTS VM on VirtualBox, connected to the LAN via a bridged network adapter. Remote access is handled by Tailscale mesh VPN — no port forwarding required.

→ [workstation-setup.md](workstation-setup.md)

---

## Philosophy

- Learn by building under real constraints
- Document failures and fixes, not just commands
- Make architectural decisions explicit and reproducible
- Build skills transferable to real infrastructure roles
