#!/usr/bin/env bash
#
# backup-homelab.sh — backs up Docker volumes + system configs to HDD
# Run via cron daily. Stops audiobookshelf briefly for consistent DB state.
#
set -euo pipefail   # fail fast: error on undefined vars, pipe failures, any command error

# ── Config ──────────────────────────────────────────
BACKUP_DIR="/mnt/backups"
TIMESTAMP="$(date +%F_%H%M%S)"
ARCHIVE="${BACKUP_DIR}/homelab-backup-${TIMESTAMP}.tar.gz"
RETENTION=7                       # how many backups to keep
LOGFILE="${BACKUP_DIR}/backup.log"

# Docker volume data paths (root-owned)
VOLUMES="/var/lib/docker/volumes/audiobookshelf_config/_data \
         /var/lib/docker/volumes/audiobookshelf_metadata/_data \
         /var/lib/docker/volumes/nginx-manager_data/_data \
         /var/lib/docker/volumes/pihole_config/_data"

# System configs not in Git
CONFIGS="/etc/ssh/sshd_config.d/00-hardening.conf \
         /etc/fail2ban/jail.local"

# ── Helper: timestamped logging ─────────────────────
log() { echo "[$(date '+%F %T')] $1" | tee -a "$LOGFILE"; }

# ── Backup ──────────────────────────────────────────
log "=== Backup started ==="

# Always restart the container on exit, even if backup fails
trap 'docker start audiobookshelf 2>/dev/null || true' EXIT

# Stop the container
log "Stopping audiobookshelf..."
docker stop audiobookshelf

# Create the archive
log "Creating archive ${ARCHIVE}..."
tar -czf "$ARCHIVE" $VOLUMES $CONFIGS
# restore with tar -xzf $ARCHIVE-NAME -C /

# Prune old backups, keep newest $RETENTION
log "Pruning old backups (keeping ${RETENTION})..."
ls -t "$BACKUP_DIR"/homelab-backup-*.tar.gz | tail -n +$((RETENTION+1)) | xargs -r rm --

log "=== Backup complete: ${ARCHIVE} ==="
