# Homelab Backups

**What:** Docker volumes + system configs not in Git
**Where:** HDD-backed share (`/mnt/backups` → host `/media/strma77/Glavni/vm-backups`)
**When:** Daily at 04:00 via root cron
**Script:** `scripts/backup-homelab.sh`

---

## What gets backed up
- Audiobookshelf config + metadata volumes
- NPM data volume (proxy host rules, SQLite, keys)
- Pi-hole config volume (DNS records, settings, admin pw hash)
- sshd_config.d/00-hardening.conf
- /etc/fail2ban/jail.local

## What does NOT get backed up
- **Compose files** — already version-controlled in this Git repo
- **Audiobook media** — lives on the host, not the VM; large and re-downloadable
- **NPM certs volume** — empty until SSL in Phase 3
- **Pi-hole dnsmasq volume** — empty unless custom overrides added

---

## How it works

The script stops the container for consistent SQLite. Tars to the HDD and restarts the container via trap EXIT so a failed backup cannot cause an outage.
Older backups auto-pruned; 7 daily backups = ~1 week of recovery points.
Logs are written to `backup.log` (script output) and `cron.log` (cron's capture of the same).

---

## Running manually
```bash
sudo bash /home/admin/homelab/scripts/backup-homelab.sh
```
Must run as root — needs access to root-owned Docker volumes and the docker command.

---

## Restore procedure

```bash
# Extract to root (paths inside the archive are relative, hence -C /)
sudo tar -xzf /mnt/backups/homelab-backup-<TIMESTAMP>.tar.gz -C /

# Restart the container to pick up restored volumes
docker restart audiobookshelf
```
To verify the restore, integrity check:
```bash
sqlite3 /var/lib/docker/volumes/audiobookshelf_config/_data/absdatabase.sqlite "PRAGMA integrity_check;"
```

---

## Verifying a backup (without restoring)

`tar -tzf /mnt/backups/BACKUP.tar.gz`

`-tzf` to list the contents of the backup 

*Lesson:* don't compare live-DB hash to backup hash — the live DB moves after the container restarts. Use PRAGMA integrity_check instead.

---

## Schedule / cron
`0 4 * * * /bin/bash /home/admin/homelab/scripts/backup-homelab.sh >> /mnt/backups/cron.log 2>&1`

```bash
0 4 * * *
│ │ │ │ │
│ │ │ │ └─ day of week (0-7, * = every)
│ │ │ └─── month (1-12, * = every)
│ │ └───── day of month (1-31, * = every)
│ └─────── hour (0-23)  → 4 = 4 AM
└───────── minute (0-59) → 0
```

So `0 4 * * *` = every day at 04:00. Chosen because nobody's using the service at 4 AM, so the brief container stop is invisible.

---

## Known limitations / future
On-site backup only - not true 3-2-1 yet.
Off-host for later-phase.
Media not backed up.
