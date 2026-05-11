# VM SSH Hardening

**Date:** 2026-05-10
**VM:** Ubuntu Server 24.04.4 LTS at `192.168.100.50`
**Operator:** strma77
**Status:** SSH key-only auth + root login disabled. fail2ban and UFW pending.

---

## Why this matters

Since the VM is exposed on the internet the sooner its protected against attacks the better.

### Threat model

First have to define what to defend against.

Three threat tiers, in order of likelyhood:

#### Tier 1 - Automated bots scanning the internet

Most realistic threat. Bots constantly scan IPv4 space looking for SSH on port 22. 
They try `root/root`, `admin/admin`, `ubuntu/ubuntu`, default vendor passwords, leaked credential dumps, and slow-motion brute force on common usernames. 
VM, already exposed via Tailscale, is technically less reachable than a public IP, but internal lateral movement is real — 
if any device on your LAN gets compromised, that device can now scan your VM. Internal-network safety is a comfort blanket, not armor.

With bots constantly scanning IPv4 space looking for SSH on port 22, constantly trying default vendor passwords like `root/root`, `admin/admin`, `ubuntu/ubuntu` or leaked credentials or slow rute force on common usernames


#### Tier 2 - Targeted opportunistic attack

Someone who specifically learned the location of the VM and has some foothold (maybe a phishing email got onto the laptop, maybe a malicious browser tab on the desktop ran a script).
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

## How to reproduce

