# SSH & Console Access

## SSH aliases (from desktop/laptop)
| Command | Target | User@Host |
|---------|--------|-----------|
| `ssh pve` | Proxmox host | admin@192.168.100.10 |
| `ssh docker` | Docker VM (VM 100) | strma@10.10.20.50 |

Aliases defined in `~/.ssh/config`. Key-only auth, no passwords.

## Web UIs
| Service | URL |
|---------|-----|
| Proxmox | https://192.168.100.10:8006 |
| OPNsense | https://192.168.100.2 |
| Pi-hole | http://10.10.20.53/admin |
| Homarr | http://10.10.20.50:7575 |
| Portainer | https://10.10.20.50:9443 |
| NPM admin | http://10.10.20.50:81 |
| Uptime Kuma | http://10.10.20.50:3001 |
| Audiobookshelf | http://10.10.20.50:13378 |
| Roadmap | http://10.10.20.50:8080 |

## Console access (when SSH/web is down)
- **OPNsense:** Proxmox UI → VM 102 → Console
- **Any guest:** Proxmox UI → VM/CT → Console
- **Pi-hole (CT 101) shell from host:** `ssh pve` then `sudo pct enter 101`
- **Password recovery (OPNsense):** reboot VM 102 → boot menu → single-user → `passwd`

## Reaching Services/Lab from clients
Desktop & laptop have persistent static routes:
`10.10.20.0/24` and `10.10.30.0/24` via `192.168.100.2` (NetworkManager)
