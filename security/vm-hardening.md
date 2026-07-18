# SSH Hardening — Step-by-Step Walkthrough

**Original date:** 2026-05-10 (Ubuntu Server VM)
**Updated:** 2026-07-18 (expanded for Proxmox host + any Debian/Ubuntu system)
**Operator:** strma77
**Goal:** SSH key-only auth, root login disabled, fail2ban, UFW. Every step spells out exactly what you'll see and type.

---

## Before you start — read this first

**What machine are you hardening?**

- **Ubuntu Server VM** (like your Docker host at `192.168.100.50`): you already have a non-root user called `admin`. Skip straight to Step 1.
- **Proxmox host** (like your Beelink at `192.168.100.10`): you only have `root` right now. You MUST create a non-root user first — go to Step 0.

**What machine are you running commands FROM?**

Your main desktop/laptop PC — referred to as **DESKTOP** throughout. The machine you're hardening is referred to as **SERVER**.

**Replace these placeholders everywhere you see them:**

| Placeholder | Replace with | Example |
|---|---|---|
| `SERVER_IP` | The IP of the machine you're hardening | `192.168.100.10` or `192.168.100.50` |
| `YOUR_USER` | The non-root username on the server | `admin` or `vito` |
| `you@email` | Your actual email (for SSH key comment only, not functional) | `vito@homelab` |

**The two-terminal safety rule:**

Before touching ANY SSH config, open TWO separate SSH sessions to the server. Work in one. Leave the other untouched. If you break SSH config and reload, your existing sessions stay alive — the untouched session is your lifeline to fix it. **Never close both sessions while making SSH changes.**

Why? Existing SSH connections survive config changes. New connections use the new config. If the new config is broken, new connections fail — but your already-open session still works. Close both and you're locked out.

---

## Step 0 — Create a non-root user (PROXMOX ONLY)

> **Skip this step entirely if you're on Ubuntu Server — you already have a non-root user.**

Proxmox only gives you `root` by default. You need a regular user to SSH in as, because the whole point of hardening is disabling root SSH access.

**0.1 — Log into the Proxmox console** (either the physical screen on the Beelink, or the web UI shell at `https://SERVER_IP:8006` → node → Shell).

**0.2 — Create a new user:**

```bash
useradd -m -s /bin/bash YOUR_USER
```

What this does:
- `-m` → creates a home directory at `/home/YOUR_USER`
- `-s /bin/bash` → sets their shell to bash (without this, some systems default to `/bin/sh` or no shell at all, and SSH login dumps you into a weird limited environment)

You'll see: **nothing.** No output means success. If you see an error like `useradd: user 'YOUR_USER' already exists`, that's fine — it already exists, move on.

**0.3 — Set a password for the new user:**

```bash
passwd YOUR_USER
```

You'll see:
```
New password:
```
Type a strong password. **Nothing will appear on screen as you type — no dots, no asterisks, nothing.** This is normal Linux behavior, not a bug. Press Enter.

You'll see:
```
Retype new password:
```
Type the exact same password again. Press Enter.

You'll see:
```
passwd: password updated successfully
```

If you see `Sorry, passwords do not match` — start over, run `passwd YOUR_USER` again.

**0.4 — Give the new user sudo privileges:**

```bash
usermod -aG sudo YOUR_USER
```

You'll see: **nothing.** No output means success.

**0.5 — Test the new user works before continuing:**

```bash
su - YOUR_USER
```

You'll see:
```
Password:
```
Type the password you just set. Press Enter.

Your prompt should change from `root@pve:~#` to `YOUR_USER@pve:~$`. The `$` instead of `#` confirms you're no longer root.

Now test sudo:
```bash
sudo whoami
```

You'll see:
```
[sudo] password for YOUR_USER:
```
Type your password. Press Enter.

You'll see:
```
root
```

That confirms sudo works. Type `exit` to go back to root, then `exit` again to go back to the console login. You're done with Step 0.

---

## Step 1 — Change the default password (SERVER)

> **Proxmox users:** you already set a root password during install AND a user password in Step 0. Skip to Step 2.
>
> **Ubuntu Server users:** if you're still using the default `admin`/`admin` credentials, change them now.

```bash
passwd
```

You'll see:
```
Changing password for admin.
Current password:
```
Type your CURRENT password (the old/default one). Press Enter.

```
New password:
```
Type a new, strong password. Press Enter. Nothing appears on screen — that's normal.

```
Retype new password:
```
Same new password again. Press Enter.

```
passwd: password updated successfully
```

If you see `Authentication token manipulation error` — you probably mistyped the current password. Run `passwd` again.

---

## Step 2 — Check for or generate an SSH key (DESKTOP)

You need an SSH keypair on your desktop. The private key stays on your desktop forever. The public key gets copied to the server.

**2.1 — Check if you already have one:**

```bash
ls -la ~/.ssh/
```

You'll see one of two things:

**Scenario A — key already exists:**
```
-rw-------  1 user user  411 May  1 12:00 id_ed25519
-rw-r--r--  1 user user   98 May  1 12:00 id_ed25519.pub
```
If you see `id_ed25519` AND `id_ed25519.pub` → **skip to Step 3.** You already have a keypair.

**Scenario B — no key exists:**
```
ls: cannot access '/home/user/.ssh/': No such file or directory
```
Or the directory exists but has no `id_ed25519` file → generate one now.

**2.2 — Generate a new SSH key:**

```bash
ssh-keygen -t ed25519 -C "you@email"
```

You'll see:
```
Generating public/private ed25519 key pair.
Enter file in which to save the key (/home/user/.ssh/id_ed25519):
```
**Just press Enter.** Accept the default path. Don't change it unless you have a specific reason.

```
Enter passphrase (empty for no passphrase):
```
**Decision point:**
- Type a passphrase → adds a second layer: even if someone steals your private key file, they can't use it without this passphrase. Recommended.
- Just press Enter → no passphrase, key file alone is enough to authenticate. Slightly less secure but more convenient.

Either choice works. Pick one, press Enter.

```
Enter same passphrase again:
```
Type the same passphrase (or press Enter again if you chose no passphrase). Press Enter.

You'll see:
```
Your identification has been saved in /home/user/.ssh/id_ed25519
Your public key has been saved in /home/user/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxx you@email
```

Done. You now have a keypair.

---

## Step 3 — Copy the public key to the server (DESKTOP)

The server needs your public key in its `authorized_keys` file to recognize you.

```bash
ssh-copy-id YOUR_USER@SERVER_IP
```

You'll see:
```
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s)
/usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
YOUR_USER@SERVER_IP's password:
```

Type the SERVER password for `YOUR_USER` (not your desktop password, not the SSH key passphrase — the actual login password on the server). Press Enter.

You'll see:
```
Number of key(s) added: 1

Now try logging into the machine, with:   "ssh 'YOUR_USER@SERVER_IP'"
and check to make sure that only the key(s) you wanted were added.
```

If you see `Connection refused` → SSH isn't running on the server, or the IP is wrong.
If you see `Permission denied` → wrong password. Try again.

---

## Step 4 — Verify key auth works BEFORE disabling passwords (DESKTOP)

**This is the most critical checkpoint. Do NOT skip it. Do NOT proceed to Step 5 if this fails.**

```bash
ssh -o PreferredAuthentications=publickey -o PasswordAuthentication=no YOUR_USER@SERVER_IP 'echo KEY_AUTH_WORKS; whoami'
```

What this does: forces SSH to ONLY try your key, not fall back to password. If the key isn't set up correctly, this will fail loudly instead of silently using your password and giving you a false sense of security.

**Success — you'll see:**
```
KEY_AUTH_WORKS
YOUR_USER
```
This means key auth works. Proceed to Step 5.

**Failure — you'll see:**
```
YOUR_USER@SERVER_IP: Permission denied (publickey,password).
```
This means the key isn't installed correctly on the server. Go back to Step 3 and redo `ssh-copy-id`. Common causes:
- Wrong username in the command
- Key was generated but never copied
- File permissions on the server's `~/.ssh/` directory are wrong (SSH is very picky — `.ssh/` must be `700`, `authorized_keys` must be `600`)

**To fix permissions manually (on SERVER):**
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

---

## Step 5 — Open two SSH sessions (DESKTOP)

This is the safety net. Do it now before changing any SSH config.

**Terminal 1 — your working session:**
```bash
ssh YOUR_USER@SERVER_IP
```

**Terminal 2 — your lifeline (open a completely separate terminal window):**
```bash
ssh YOUR_USER@SERVER_IP
```

Both should connect. Leave Terminal 2 completely untouched. Do all work in Terminal 1. If something breaks, Terminal 2 is your way back in.

---

## Step 6 — Back up the SSH config (SERVER, in Terminal 1)

```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%F)
```

You'll see: **nothing** (success), or a `[sudo] password for YOUR_USER:` prompt — type your password, press Enter.

**Verify the backup exists:**
```bash
ls -la /etc/ssh/sshd_config.bak.*
```

You'll see something like:
```
-rw-r--r-- 1 root root 3285 Jul 18 10:00 /etc/ssh/sshd_config.bak.2026-07-18
```

Good. If you ever need to undo everything, this file is your reset button.

---

## Step 7 — Create the hardening config (SERVER, in Terminal 1)

**7.1 — Check if the `.d/` directory exists:**

```bash
ls /etc/ssh/sshd_config.d/
```

**If you see files listed** → the directory exists, proceed to 7.2.
**If you see `No such file or directory`** → create it:
```bash
sudo mkdir -p /etc/ssh/sshd_config.d/
```

**7.2 — Also check that the main sshd_config actually includes the `.d/` directory:**

```bash
grep -i "include" /etc/ssh/sshd_config
```

You should see something like:
```
Include /etc/ssh/sshd_config.d/*.conf
```

If you see this → great, snippets in `.d/` will be loaded automatically.
If you see nothing → you'll need to add it. Open the config:
```bash
sudo nano /etc/ssh/sshd_config
```
Add this line at the very top of the file (above everything else):
```
Include /etc/ssh/sshd_config.d/*.conf
```
Save: `Ctrl+O`, press Enter. Exit: `Ctrl+X`.

**7.3 — Create the hardening snippet:**

```bash
sudo tee /etc/ssh/sshd_config.d/00-hardening.conf > /dev/null << 'EOF'
# SSH hardening — homelab
# Created: 2026-07-18
# Purpose: disable password auth, disable root login, enforce key-only
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
# Only allow specific user(s) to SSH in
AllowUsers YOUR_USER
EOF
```

**CRITICAL: Replace `YOUR_USER` in the `AllowUsers` line with your actual username before running this.** If you paste it as-is with the literal text `YOUR_USER`, nobody will be able to SSH in. Double-check before pressing Enter.

You'll see: **nothing.** No output means it worked.

**Verify the file was created correctly:**
```bash
cat /etc/ssh/sshd_config.d/00-hardening.conf
```

You should see the exact content you just wrote. Read it line by line. If anything looks wrong, delete it and redo:
```bash
sudo rm /etc/ssh/sshd_config.d/00-hardening.conf
```
Then run the `sudo tee` command again with corrections.

---

## Step 8 — Validate the config (SERVER, in Terminal 1)

```bash
sudo sshd -t
```

**Success — you'll see:** absolutely nothing. No output = no errors = config is valid.

**Failure — you'll see something like:**
```
/etc/ssh/sshd_config.d/00-hardening.conf line 7: keyword allowusers extra arguments
```
This tells you exactly which file and line has the problem. Fix the error in the snippet, then run `sudo sshd -t` again. Do NOT proceed until this command produces zero output.

---

## Step 9 — Reload SSH (SERVER, in Terminal 1)

```bash
sudo systemctl reload ssh
```

**On Proxmox/Debian:** if `ssh` doesn't work, try `sshd` instead:
```bash
sudo systemctl reload sshd
```

You'll see: **nothing.** No output means success.

If you see `Failed to reload ssh.service: Unit ssh.service not found` → use `sshd` instead (Proxmox uses `sshd`, Ubuntu uses `ssh` — they're the same daemon, just named differently).

**Your existing Terminal 1 and Terminal 2 sessions are still alive.** Reload does not kill existing connections — it only affects NEW connections from this point forward.

---

## Step 10 — Run verification tests (DESKTOP, in a NEW third terminal)

**Do NOT close Terminal 1 or Terminal 2 yet.** Open a brand new terminal for these tests.

### Test 1 — Key auth still works

```bash
ssh -o PreferredAuthentications=publickey -o PasswordAuthentication=no YOUR_USER@SERVER_IP 'echo KEY_AUTH_WORKS; whoami'
```

**Expected output:**
```
KEY_AUTH_WORKS
YOUR_USER
```

If this fails → something went wrong. Go to Terminal 2 (your lifeline) and run:
```bash
sudo rm /etc/ssh/sshd_config.d/00-hardening.conf
sudo sshd -t && sudo systemctl reload ssh
```
This removes the hardening snippet and reverts to defaults. Debug what went wrong before trying again.

### Test 2 — Password auth is rejected

```bash
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no YOUR_USER@SERVER_IP 'echo SHOULD_NEVER_PRINT'
```

**Expected output:**
```
YOUR_USER@SERVER_IP: Permission denied (publickey).
```

The `SHOULD_NEVER_PRINT` text must NOT appear. If it does → password auth is still enabled, hardening didn't take. Check that your snippet file is actually being loaded (`grep -i include /etc/ssh/sshd_config`).

### Test 3 — Root login is rejected

```bash
ssh -o PreferredAuthentications=publickey root@SERVER_IP 'echo SHOULD_NEVER_PRINT' 2>&1 | head -5
```

**Expected output:**
```
root@SERVER_IP: Permission denied (publickey).
```

Again, `SHOULD_NEVER_PRINT` must NOT appear.

### Bonus — Check effective config directly (SERVER)

```bash
sudo sshd -T | grep -E "passwordauthentication|permitrootlogin|pubkeyauthentication|allowusers"
```

**Expected output:**
```
permitrootlogin no
passwordauthentication no
pubkeyauthentication yes
allowusers YOUR_USER
```

If any of these show the wrong value, the snippet isn't being loaded. Check the `Include` directive in the main config (Step 7.2).

**All three tests pass? SSH hardening is complete.** You can now safely close Terminal 1 and Terminal 2.

---

## Step 11 — Install and configure fail2ban (SERVER)

### 11.1 — Install fail2ban

```bash
sudo apt update && sudo apt install fail2ban -y
```

You'll see a wall of text as it downloads and installs. Wait for it to finish. The last line will return you to your prompt (`YOUR_USER@...:~$`).

### 11.2 — Check it's running

```bash
sudo systemctl status fail2ban
```

You'll see something like:
```
● fail2ban.service - Fail2Ban Service
     Loaded: loaded
     Active: active (running) since ...
```

**If it says `inactive (dead)`:**
```bash
sudo systemctl enable --now fail2ban
```

### 11.3 — Create the jail config

```bash
sudo tee /etc/fail2ban/jail.local > /dev/null << 'EOF'
[DEFAULT]
bantime = 24h
findtime = 30m
maxretry = 5
bantime.increment = true
bantime.factor = 1.5
bantime.formula = bantime * (1 + failures / 2)
ignoreip = 127.0.0.1/8 ::1 192.168.100.0/24 100.64.0.0/10

[sshd]
enabled = true
EOF
```

What each line does:
- `bantime = 24h` — banned IPs stay blocked for 24 hours
- `findtime = 30m` — failures are counted within a 30-minute window
- `maxretry = 5` — 5 failed attempts within `findtime` triggers a ban
- `bantime.increment = true` — repeat offenders get progressively longer bans
- `ignoreip` — IPs that can NEVER be banned. **This is critical.** Without `192.168.100.0/24` here, fat-fingering your own password a few times bans your own desktop from the server
  - `127.0.0.1/8` = localhost
  - `::1` = IPv6 localhost
  - `192.168.100.0/24` = your LAN (adjust if your network uses a different range)
  - `100.64.0.0/10` = Tailscale IP range

### 11.4 — Restart fail2ban to load the new config

```bash
sudo systemctl restart fail2ban
```

You'll see: **nothing.** No output = success.

Note: fail2ban needs a `restart`, not `reload`, for jail config changes. This is different from SSH which uses `reload`.

### 11.5 — Verify fail2ban is working

```bash
sudo fail2ban-client status sshd
```

**Expected output:**
```
Status for the jail: sshd
|- Filter
|  |- Currently failed:	0
|  |- Total failed:	0
|  `- File list:	/var/log/auth.log
`- Actions
   |- Currently banned:	0
   |- Total banned:	0
   `- Banned IP list:
```

If you see `Sorry but the jail 'sshd' does not exist` → the jail config didn't load. Check for typos in `/etc/fail2ban/jail.local`, then restart fail2ban again.

**Check the settings took correctly:**
```bash
sudo fail2ban-client get sshd bantime
```
Expected: `86400` (that's 24 hours in seconds)

```bash
sudo fail2ban-client get sshd ignoreip
```
Expected: should list your IPs from the `ignoreip` line.

---

## Step 12 — Install and configure UFW (SERVER)

### 12.1 — Install UFW

**Ubuntu:** UFW is pre-installed. Skip to 12.2.

**Proxmox/Debian:** UFW is NOT pre-installed:
```bash
sudo apt install ufw -y
```

### 12.2 — Set default policies (DO NOT ENABLE YET)

```bash
sudo ufw default deny incoming
```
You'll see: `Default incoming policy changed to 'deny'`

```bash
sudo ufw default allow outgoing
```
You'll see: `Default outgoing policy changed to 'allow'`

### 12.3 — Add SSH rule BEFORE enabling (CRITICAL ORDER)

```bash
sudo ufw limit 22/tcp comment 'SSH rate-limited'
```
You'll see: `Rules updated` and `Rules updated (v6)`

**Why `limit` instead of `allow`:** `limit` opens the port but also rate-limits it — if a single IP makes 6+ connection attempts within 30 seconds, UFW temporarily blocks them. Free brute-force friction on top of fail2ban.

### 12.4 — If this is the Proxmox host, also allow the web UI

```bash
sudo ufw allow 8006/tcp comment 'Proxmox Web UI'
```
You'll see: `Rules updated` and `Rules updated (v6)`

**Skip this on the Ubuntu Docker VM** — it doesn't run Proxmox UI.

### 12.5 — Review rules BEFORE enabling

```bash
sudo ufw show added
```

**Expected output (Proxmox host):**
```
Added user rules (see 'ufw status' for running firewall):
ufw limit 22/tcp comment 'SSH rate-limited'
ufw allow 8006/tcp comment 'Proxmox Web UI'
```

**Expected output (Ubuntu VM):**
```
Added user rules (see 'ufw status' for running firewall):
ufw limit 22/tcp comment 'SSH rate-limited'
```

**Read this list carefully.** If SSH (port 22) is NOT in this list and you enable UFW, you are locked out immediately. Do not proceed without seeing port 22 in the list.

### 12.6 — Enable UFW

```bash
sudo ufw enable
```

You'll see:
```
Command may disrupt existing ssh connections. Proceed with operation (y|n)?
```

Type `y`, press Enter.

You'll see:
```
Firewall is active and enabled on system startup
```

### 12.7 — Immediately test SSH from a NEW terminal (DESKTOP)

**Do NOT close your current SSH session yet.**

Open a new terminal on your desktop:
```bash
ssh YOUR_USER@SERVER_IP
```

**If it connects** → UFW is configured correctly, SSH is allowed through. You're done with UFW.

**If it hangs or refuses** → go back to your still-open session and disable UFW immediately:
```bash
sudo ufw disable
```
Then debug which rule is missing or wrong.

### 12.8 — Verify final UFW state

```bash
sudo ufw status verbose
```

**Expected output:**
```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp                     LIMIT IN    Anywhere
8006/tcp                   ALLOW IN    Anywhere
22/tcp (v6)                LIMIT IN    Anywhere (v6)
8006/tcp (v6)              ALLOW IN    Anywhere (v6)
```

---

## How to roll back everything

If anything goes catastrophically wrong at any point, here's the undo for each layer:

### Undo SSH hardening
Use your still-open SSH session, or the physical console / Proxmox web shell:
```bash
sudo rm /etc/ssh/sshd_config.d/00-hardening.conf
sudo sshd -t && sudo systemctl reload ssh
```
Or restore from backup:
```bash
sudo cp /etc/ssh/sshd_config.bak.2026-07-18 /etc/ssh/sshd_config
sudo sshd -t && sudo systemctl reload ssh
```

### Undo fail2ban
```bash
sudo systemctl stop fail2ban
sudo rm /etc/fail2ban/jail.local
sudo systemctl start fail2ban
```

### Undo UFW (nuclear option)
```bash
sudo ufw disable
sudo ufw reset
```
You'll see: `Resetting all rules to installed defaults. Proceed with operation (y|n)?`
Type `y`, press Enter. Firewall is completely off and all rules are wiped.

---

## Final checklist — confirm everything is in place

Run all of these from your DESKTOP after completing all steps:

```bash
# 1. Key auth works
ssh -o PreferredAuthentications=publickey -o PasswordAuthentication=no YOUR_USER@SERVER_IP 'echo KEY_AUTH_WORKS'

# 2. Password auth rejected
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no YOUR_USER@SERVER_IP 'echo SHOULD_NEVER_PRINT'

# 3. Root login rejected
ssh -o PreferredAuthentications=publickey root@SERVER_IP 'echo SHOULD_NEVER_PRINT' 2>&1 | head -5
```

Then on the SERVER:

```bash
# 4. fail2ban is watching SSH
sudo fail2ban-client status sshd

# 5. UFW is active with correct rules
sudo ufw status verbose

# 6. SSH effective config is correct
sudo sshd -T | grep -E "passwordauthentication|permitrootlogin|pubkeyauthentication|allowusers"
```

**All six checks pass = hardening complete.**

---

## Why this matters — threat model

Three threat tiers, in order of likelihood:

**Tier 1 — Automated bots scanning the internet.** The most realistic threat. Bots constantly scan IPv4 space looking for SSH on port 22, trying default vendor passwords like `root/root`, `admin/admin`, leaked credential dumps and slow brute force on common usernames. Even behind NAT, if any LAN device is compromised, the VM/host can be scanned.

**Tier 2 — Targeted opportunistic attack.** Someone who learned the location of your server or has some foothold (phishing email on a laptop, malicious browser tab running a script). They try easy paths first — default credentials, known weak passwords, recently-leaked SSH keys.

**Tier 3 — Determined attacker with skills and time.** Someone targeting you specifically with real expertise. Against this tier, hardening one machine isn't enough — the whole network architecture, OS choice, patch cadence, and operational hygiene matter more.

Our hardening targets Tiers 1 and 2. Most homelab compromises happen there. We're not trying to stop a nation-state — we're trying to be too annoying for opportunistic attacks.

---

## Concepts reference

**Why disable password auth even when keys already work?**
Passwords rely on the weakest security factor — the human — and can be guessed, leaked, or brute-forced. Disabling password auth adds defense in depth: even if a password is compromised, an attacker still needs the private key. Two independent locks instead of one.

**Why disable root login specifically?**
The root account has unrestricted privileges, making it a high-value target. It's also a universal username present on every Unix/Linux system — attackers already know half the login credentials. Disabling root SSH forces them to guess both a valid username AND obtain authentication.

**Why use a `.d/` snippet instead of editing the main `sshd_config`?**
Package upgrades can replace the main `sshd_config`. Files inside `.d/` directories are typically left untouched during upgrades. Separating custom settings from defaults makes them safer and easier to maintain.

**Why run `sshd -t` before reload?**
It validates the config in a dry run without affecting the running service. Catches syntax errors before they lock you out.

**Why reload instead of restart?**
Reload re-reads config without killing existing sessions. Restart kills the daemon and drops all connections. Reload lets you keep your lifeline session alive.

**Why `ufw limit` vs `allow` for SSH?**
`allow` opens the port unconditionally. `limit` opens it but rate-limits: 6+ connection attempts from one IP within 30 seconds triggers a temporary block. Lightweight brute-force friction that complements fail2ban. They work at different layers — UFW throttles connection rate (how often you knock), fail2ban bans on auth failures (how many times you guess wrong).

**The Docker/UFW bypass gotcha:**
When Docker publishes a port, it writes its own iptables/nftables rules that sit in front of UFW. Default-deny in UFW does NOT stop Docker-published ports. The fix is binding container ports to `127.0.0.1` instead of `0.0.0.0`, so Docker can't expose them externally and the only path in is through a reverse proxy.

---

## References

- `man sshd_config` — full SSH directive reference
- `man jail.conf` — fail2ban jail configuration
- https://www.ssh.com/academy/ssh/public-key-authentication
- https://help.ubuntu.com/community/UFW
