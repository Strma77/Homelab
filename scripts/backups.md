# Homelab Backups

**What:** Whole-VM/CT backups of the Proxmox guests (OPNsense, Docker host, Pi-hole).
**How:** Proxmox `vzdump` scheduled job -> ZSTD archives on an NFS share hosted by the desktop.
**When:** Daily at 21:00 via the PVE backup job (not cron).
**Alerts:** ntfy push to phone on every run (success + failure).

> **History note:** this replaces the old `scripts/backup-homelab.sh` cron system. That script tarred Docker volumes to the HDD nightly. It silently stopped on 2026-06-07 when the Docker host was rebuilt as a Proxmox VM - cron lives in `/var/spool/cron`, not in Git, so the schedule didn't survive the migration. The script is now **redundant** (a `vzdump` of VM 100 captures the entire Docker VM, volumes included) and is kept only for reference. See "Retiring the old script".

---

## Storage - `desktopbackup` (NFS)

Proxmox-managed NFS storage. PVE owns the mount lifecycle (mounts on demand, fails cleanly when the desktop is off) - it is **not** an fstab mount anymore.

| Field | Value |
|-------|-------|
| Storage ID | `desktopbackup` |
| Type | `nfs` (was `dir` until 2026-09 - see History) |
| NFS server | `192.168.100.132` (desktop) |
| Export | `/mnt/hdd/vm-backups/proxmox` |
| Local mountpoint | `/mnt/pve/desktopbackup` (PVE-managed) |
| Options | `vers=4.2,soft` |
| Content | `backup,iso` |

The desktop's HDD partition (`sda3`, NTFS, label "Glavni") is mounted at `/mnt/hdd` on the desktop and exported over NFS. `soft` means the pve host will not hang if the desktop is off.

```bash
# add (already done - rebuild reference)
pvesm add nfs desktopbackup --server 192.168.100.132 \
  --export /mnt/hdd/vm-backups/proxmox --content backup,iso --options vers=4.2,soft

# check online + list dumps
pvesm status
ls -lah /mnt/pve/desktopbackup/dump/
```

---

## The backup job

Defined in `/etc/pve/jobs.cfg`. Inspect: `grep -A8 vzdump /etc/pve/jobs.cfg`.

| Setting | Value |
|---------|-------|
| Schedule | `21:00` daily |
| VMIDs | `100` (docker-host), `101` (pihole), `102` (opnsense) |
| Storage | `desktopbackup` |
| Mode | `snapshot` (no downtime - LVM snapshot, guests stay up) |
| Compression | `zstd` |
| Retention | `keep-last=3` |
| Notification mode | `notification-system` (routes through matchers) |

> **Retention caveat:** `keep-last=3` keeps the 3 newest dumps *per guest*. The NFS target depends on the desktop being on at 21:00, so nights the desktop is off produce no dump - your 3 retained backups can end up older than 3 days. Known limitation of the on-site design.

Manual smoke test:
```bash
vzdump 101 --storage desktopbackup
# healthy run ends "Backup job finished successfully" and pings ntfy
```

---

## Notifications - ntfy

PVE has no native ntfy target, so it's a **webhook** target POSTing to an ntfy topic. Config splits across public + private files - the target must be created via the web UI or it errors with `private config does not exist`.

| Component | Value |
|-----------|-------|
| Target type | `webhook` (Datacenter -> Notifications) |
| Target name | `ntfy` |
| URL | `https://ntfy.sh/homelab-strma77-az700` |
| Headers | `Title: PVE Backup`, `Priority: high`, `Tags: warning` |
| Body | `{{ message }}` (UI base64-encodes it) |
| Matcher | `backup-ntfy`, mode `all`, target `ntfy` |
| Default matcher | **disabled** (was bouncing to `mail-to-root`, no SMTP relay) |

> `default-matcher` disabled means `ntfy` is the **only** notification route for the whole datacenter, not just backups. If ntfy breaks, all PVE alerts go dark. Self-hosting ntfy with auth + a health check is Phase 2.
> The topic is **public** on ntfy.sh - fine for backup pings (no secrets in body), self-host with auth later.

---

## What gets backed up (and what doesn't)

`vzdump` captures the **entire guest disk** - OS, configs, Docker volumes, everything inside the VM/CT. Big change from the old script (hand-picked volume paths only).

**Not** captured:
- **Audiobook media** - lives on the desktop host, not inside the VM. Large, re-downloadable.
- **Host-level PVE config** (`/etc/pve`, storage.cfg, jobs.cfg, notifications.cfg) - not inside any guest. Documented in `infrastructure/proxmox.md` instead.
- **OPNsense config XML** - vzdump of VM 102 covers it at block level, but OPNsense's own System -> Configuration -> Backups XML export is a faster guest-native restore path. Export periodically as belt-and-suspenders.

---

## Restore

**QEMU VMs (100 docker-host, 102 opnsense):**
```bash
# restore to a NEW throwaway id first, never straight over the live guest
qmrestore /mnt/pve/desktopbackup/dump/vzdump-qemu-100-<TS>.vma.zst 999 --storage local-lvm
```

**LXC container (101 pihole):**
```bash
pct restore 999 /mnt/pve/desktopbackup/dump/vzdump-lxc-101-<TS>.tar.zst --storage local-lvm
```

Restore to a spare VMID (e.g. `999`), boot isolated, confirm, then delete. Never restore over a running production guest as your first test.

---

## Retiring the old script

`scripts/backup-homelab.sh` is orphaned (no cron calls it) and redundant (vzdump of VM 100 already captures the Docker volumes). Options:
1. **Delete it** - cleanest, vzdump supersedes it.
2. **Keep as a file-level layer** - if you want granular per-volume `.tar.gz` restores, re-arm with a proper cron AND a mount guard (`mountpoint -q /mnt/backups || exit 1`) so it can't write to bare disk and fail silently. Log to journald so failures surface when the NFS log is unreachable, and add an Uptime Kuma push heartbeat so a dead run pages you.

Until decided, treat it as dead. Do not trust any `homelab-backup-*.tar.gz` older than 2026-06-07.

---

## Known gaps

- **On-site only** - not 3-2-1. Both copies live in the same house.
- **Desktop-dependent** - no desktop on at 21:00 = no dump that night.
- **Restore unproven** - job runs and lands, but a full restore has not been tested end-to-end yet. Do the throwaway-VMID restore test before trusting any of this.

---

## History

### 2026-09-06 - Resurrected + converted to native NFS
vzdump job had been failing every night since ~2026-08-24 with `could not activate storage 'desktopbackup': mkdir /mnt/desktopbackup: File exists`. Root cause: storage defined as `dir` type over a path an fstab line already NFS-mounted, so PVE's pre-backup mkdir tripped. Fixed by removing the fstab mount and redefining `desktopbackup` as native `nfs` storage. Added VM 102 to the job. Wired ntfy, disabled the bouncing default mail matcher. Verified with manual `vzdump 101`.

### 2026-06-07 - Old cron system last ran
`backup-homelab.sh` cron silently stopped when the Docker host migrated to Proxmox. Not noticed until 2026-09.
