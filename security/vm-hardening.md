# VM SSH Hardening

**Date:** 2026-05-10
**VM:** Ubuntu Server 24.04.4 LTS at `192.168.100.50`
**Operator:** strma77
**Status:** SSH key-only auth + root login disabled. fail2ban and UFW applied.

---

## Why this matters

The VM isn't directly exposed to the public internet (it's behind ISP NAT, reachable via Tailscale), but "internal only" is a comfort blanket, not armor. The sooner SSH is hardened, the better — before exposure ever becomes a question.

### Threat model

First have to define what to defend against.

Three threat tiers, in order of likelihood:

#### Tier 1 - Automated bots scanning the internet

The most realistic threats are bots constantly scanning IPv4 space looking for SSH on port 22, trying default vendor passwords like `root/root`, `admin/admin`, leaked credential dumps and slow-motion brute force on common usernames.
Since the VM is already exposed via Tailscale, it is technically less reachable than a public IP but internal lateral movement is real.
If any LAN device is compromised, VM can be scanned.

#### Tier 2 - Targeted opportunistic attack

Someone who specifically learned the location of the VM or has some foothold (maybe a phishing email got onto the laptop, maybe a malicious browser tab on the desktop ran a script).
They'd try the easy paths first — default credentials, known weak passwords, recently-leaked SSH keys, etc.

#### Tier 3 - Determined attacker with skills and time

Someone targeting you specifically with real expertise. 
Honestly, against this tier, hardening one VM is hardly gonna do much. The whole network architecture, OS choice, patch cadence, and operational hygiene matter more.

---

*Our hardening is aimed at Tiers 1 and 2.*
Most homelab compromises happen at those tiers. We're not trying to stop a nation-state; we're trying to be too annoying for opportunistic attacks.

---

## What changed

| Change | Before | After |
|--------|--------|-------|
| VM admin password | `admin` (default) | strong passphrase |
| SSH key auth from desktop | not configured | ed25519 key in `authorized_keys` |
| Password authentication | enabled (default) | disabled |
| Root SSH login | `prohibit-password` (default) | disabled entirely |
| Keyboard-interactive auth | enabled | disabled |
| Allowed SSH users | any valid user | `admin` only |


---

## SSH Key Authentication

Asymmetric cryptography uses two mathematically linked keys: a private key and a public key. The private key signs; the public key verifies. They're mathematically linked but you can't derive one from the other.

**Private key**: stays secret on your machine and must never be shared. During SSH authentication, the server does not request the private key itself. Instead, it sends a random challenge. Your device signs that challenge using the private key and returns the signature. The server then verifies it with your public key. This proves you own the private key without ever transmitting it across the network.

**Public key**: can be shared freely and is placed on the server. On its own, it is useless to attackers.

Unlike a password - which is sent to the server on every login, even if encrypted in transit - the private key never travels across the network at all.

### Why brute-forcing ed25519 is infeasible

Passwords are vulnerable because humans choose predictable combinations. Ed25519 keys use a keyspace of about 2²⁵² possibilities, making brute-force attacks computationally unrealistic even with enormous computing power. The mathematics provides no practical shortcuts.

### Why ed25519 instead of RSA

Both are asymmetric algorithms, but ed25519 is newer and based on elliptic-curve cryptography, while RSA relies on factoring large primes. Ed25519 offers strong security with smaller keys, faster performance, and cleaner implementations, making it the modern default for SSH authentication.

---

## How to reproduce

Steps assume a fresh Ubuntu Server VM and a desktop that already has an SSH keypair.
Keep two SSH sessions open during the sshd changes (see Concepts → safety pattern).

### 1. Change the default password (on VM)
kill default creds 
```bash
passwd
```

### 2. Verify or generate an SSH key (on DESKTOP)
need a keypair to authenticate with
```bash
ls -la ~/.ssh/                          # check for existing id_ed25519
ssh-keygen -t ed25519 -C "you@email"    # only if none exists
```

### 3. Copy the public key to the VM (on DESKTOP)
VM needs your public key in authorized_keys
```bash
ssh-copy-id admin@192.168.100.50
```

### 4. Verify key auth works BEFORE disabling passwords (on DESKTOP)
never disable the fallback until the new method is proven
```bash
ssh -o PreferredAuthentications=publickey -o PasswordAuthentication=no admin@192.168.100.50 'echo OK; whoami'
```

### 5. Back up sshd_config (on VM)
rollback safety net
```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%F)
```

### 6. Create the hardening snippet (on VM)
.d/ snippet survives package upgrades; main file untouched
```bash
sudo tee /etc/ssh/sshd_config.d/00-hardening.conf > /dev/null << 'EOF'
# SSH hardening — homelab
# Created: 2026-05-10
# Purpose: disable password auth, disable root login, enforce key-only
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
# Optional: only allow specific user(s) to SSH in
AllowUsers admin
EOF
```

### 7. Validate config syntax (on VM)
catch typos before reload, never reload a broken config
```bash
sudo sshd -t
```

### 8. Reload sshd (on VM)
re-read config without dropping existing sessions
```bash
sudo systemctl reload ssh
```

### 9. Verify the three tests (on DESKTOP)
Run the three tests from the 'How to verify' section below.

---

## How to verify it's working

Run these from the desktop any time you want to confirm hardening is intact.

### Test 1 — key auth works
```bash
ssh -o PreferredAuthentications=publickey -o PasswordAuthentication=no admin@192.168.100.50 'echo KEY_AUTH_WORKS; whoami'
```
Expect: `KEY_AUTH_WORKS` and `admin`. Forces publickey only, so it fails loudly if the key isn't working instead of silently falling back to a password prompt.

### Test 2 — password auth is rejected
```bash
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no admin@192.168.100.50 'echo SHOULD_NEVER_PRINT'
```
Expect: `Permission denied`. The echo must NOT print — if it does, password auth is still alive and hardening failed.

### Test 3 — root login is rejected
```bash
ssh -o PreferredAuthentications=publickey root@192.168.100.50 'echo SHOULD_NEVER_PRINT' 2>&1 | head -5
```
Expect: `Permission denied`. Root cannot SSH in regardless of auth method.

### Bonus — check effective config without connecting (on VM)
```bash
sudo sshd -T | grep -E "passwordauthentication|permitrootlogin|pubkeyauthentication"
```
Expect: `passwordauthentication no`, `permitrootlogin no`, `pubkeyauthentication yes`. This dumps sshd's *effective* runtime config — the real source of truth, accounting for all config files combined.

---

## How to roll back

If a config change locks you out or breaks SSH, recover via the backup and snippet removal.
(Use a still-open session, or the VirtualBox console if fully locked out.)

```bash
# Option A: remove just the hardening snippet
sudo rm /etc/ssh/sshd_config.d/00-hardening.conf
sudo sshd -t && sudo systemctl reload ssh

# Option B: restore the full original config backup
sudo cp /etc/ssh/sshd_config.bak.2026-05-10 /etc/ssh/sshd_config
sudo sshd -t && sudo systemctl reload ssh
```

Backup location: `/etc/ssh/sshd_config.bak.2026-05-10`

---

## Concepts

### Why disable password auth even when keys already work?
Passwords rely on the weakest security factor — the human — and can be guessed, leaked, or brute-forced. Disabling password authentication adds defense in depth: even if a password is compromised, an attacker still needs the private key to log in. Two independent locks instead of one.

### Why disable root login specifically?
The root account has unrestricted privileges, making it a high-value target. It is also a universal username present on nearly every Unix/Linux system, meaning attackers already know half the login credentials before they even start. Disabling direct root login reduces the attack surface and forces attackers to guess both a valid username and obtain authentication.

### Why use a `.d/` snippet instead of editing the main `sshd_config`?
Configuration snippets inside `sshd_config.d/` are easier to manage because they separate custom settings from the default configuration. More importantly, package upgrades can replace or modify the main `sshd_config`, while files inside the `.d/` directory are typically left untouched, making custom configurations safer and easier to maintain.

### Why run `sshd -t` before reload?
`sshd -t` validates the SSH daemon configuration in a dry run without affecting the currently running service. This allows syntax errors or invalid settings to be caught before reloading the daemon and potentially breaking SSH access.

### Why reload instead of restart?
Reloading makes `sshd` re-read its configuration without terminating existing SSH sessions. Restarting kills the daemon and disconnects active connections. Using reload allows configuration changes to be applied safely while keeping the current session alive in case something goes wrong.

### The two-terminal safety pattern
Two SSH sessions are kept open while modifying SSH settings: one active working session and one untouched fallback session. Existing SSH sessions remain alive even if the configuration changes, so if the working session becomes unusable after a reload, the fallback session still provides access to fix the configuration and prevent lockout.

### Why `ufw limit` vs `allow` for SSH
`allow` opens the port unconditionally. `limit` opens it but adds rate-limiting: if a single IP makes 6 or more connection attempts within 30 seconds, UFW temporarily blocks it. This is a lightweight complement to fail2ban — they work at different layers. UFW `limit` throttles connection *rate* (how often you can knock on the door); fail2ban bans on *auth failures* (how many times you guess wrong). Using `limit` on port 22 adds friction to brute-force attempts for free.

**Why this matters:** enabling UFW does NOT protect your Docker-published ports (like 13378). Don't assume "UFW is on, everything's firewalled." UFW protects host-level services (SSH); Docker manages its own exposure. Awareness now, real fix in Phase 0 with the reverse proxy.
---

## Fail2ban

### What it does

Watches log files for failure patterns. When an IP racks up too many failed auth attempts in a time window, fail2ban tells the firewall to *drop that IP* for a set period.

### Why bother

With password auth disabled, fail2ban buys log hygiene, resource savings, defense in depth for the future

### Configuration
Settings live in `/etc/fail2ban/jail.local`. This overrides the package defaults without touching the shipped `defaults-debian.conf` — same upgrade-safe override pattern as `sshd_config.d/`.

```ini
[DEFAULT]
bantime = 24h
findtime = 30m
maxretry = 5
bantime.increment = true
bantime.factor = 1.5
bantime.formula = bantime * (1 + failures / 2)
ignoreip = 127.0.0.1/8 ::1 192.168.100.0/24 100.64.0.0/10
```

- `bantime = 24h` — banned IPs blocked for a day
- `findtime = 30m` — window in which failures are counted
- `maxretry = 5` — failures allowed before a ban
- `bantime.increment` — repeat offenders get progressively longer bans
- `ignoreip` — never-ban list: localhost, the LAN (`192.168.100.0/24`), and the Tailscale range (`100.64.0.0/10`). **Critical — without the LAN whitelisted, a few fat-fingered logins could ban you from your own VM.**

Apply changes with `sudo systemctl restart fail2ban` (jail config needs a restart, not reload).

### Backend note

Reads from systemd journal, bans via nftables

### Verify commands
`sudo fail2ban-client status sshd`
`sudo fail2ban-client get sshd bantime`
`sudo fail2ban-client get sshd ignoreip`

---

## UFW Firewall

### What it is and what it does

Host firewall.
 
Default-deny inbound - block everything coming in by default then explicitly allow only the ports you actually need
Allow outbound - stays open because VM needs to reach the internet for updates, Docker pulls, Tailscale, etc.

### Rules

```bash
# 1. Set default policies (deny incoming, allow outgoing) — NOT enabled yet
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 2. Allow SSH FIRST — before enabling. Use 'limit' for built-in rate limiting.
sudo ufw limit 22/tcp comment 'SSH rate-limited'

# 3. (Optional) explicitly allow Audiobookshelf — even though Docker bypasses UFW,
#    adding the rule documents intent and covers the case if Docker's behavior changes
sudo ufw allow 13378/tcp comment 'Audiobookshelf'

# 4. Review the rules BEFORE enabling
sudo ufw show added
```

### The Docker gotcha

When Docker publishes a port, it writes its OWN nftables/iptables rules directly into the `DOCKER` chain, which sits _in front of_ UFW's rules.
Even if UFW rules are set to default-deny inbound, Docker-published ports stay reachable because Docker's rules are evaluated first

Will properly solve this in Phase 0 when you add Nginx Proxy Manager — the pattern becomes "bind Docker services to localhost, expose only through the reverse proxy on 80/443." That's the real fix. For now, awareness is enough.

### Safe-enable procedure
UFW can lock you out the same way a bad sshd config can, so the order is non-negotiable:

1. Set default policies (deny in, allow out) — but don't enable yet
2. Add the allow rules **first**, especially SSH (`ufw limit 22/tcp`)
3. Review with `sudo ufw show added` before enabling
4. `sudo ufw enable` while keeping the current SSH session open
5. Test a **fresh** SSH connection from a second terminal before closing the first

If the new connection fails, the still-open session is the rope back in: `sudo ufw disable` and debug. Never enable a firewall and immediately close your only session.

### Verify command
`ufw status verbose`


> Note: both fail2ban and UFW enforce through nftables. They coexist without conflict — UFW manages the base firewall policy, fail2ban dynamically inserts ban rules. No special integration needed.

---

## Status: Complete

This hardening pass is done. All four layers in place:
- [x] SSH key-only auth, password + root login disabled
- [x] fail2ban (24h ban, LAN + Tailscale whitelisted)
- [x] UFW default-deny inbound, SSH rate-limited

### Future hardening (later phases)
- [ ] Solve the Docker/UFW bypass properly — bind containers to localhost, expose via reverse proxy (Phase 0, with NPM)
- [ ] Automated off-host backups of configs (Phase 0)
- [ ] Consider SSH cert-based auth or 2FA (later, optional)



## References
- `man sshd_config` — full directive reference
- https://www.ssh.com/academy/ssh/public-key-authentication
- `man jail.conf` — fail2ban jail configuration
- https://help.ubuntu.com/community/UFW — UFW documentation
