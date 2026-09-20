# Physical Network Layer

The virtual network (zones, VLANs, firewall rules) is documented in `infrastructure/opnsense.md`. This doc covers what the previous one didn't: physical cables and ports — the blind spot that turned a 10-second fix into an hour-long outage on 2026-09-15.

---

## Topology
```
A1 router (WiFi: A1_113771079)
│ WiFi
▼
ZTE bridge — 2× LAN, 1× WAN
│ │
LAN <?> LAN <?>
│ │
Beelink TP-Link/Dlinkgo switch
(.10, nic0 uplink) (unmanaged, 5-port, €15)
│ │
Desktop PS5
(.132) (wired)
```

## ZTE bridge

- **2 LAN ports** (labeled 1, 2) + **1 WAN port**.
- **WAN is the uplink port — never plug a client device into it.** Doing so throws a WAN-fault (red light) because the ZTE expects an internet feed there, not a device. This was the root cause of the 2026-09-15 outage (PS5 plugged into WAN).
- Connects to the **A1 router over WiFi** — the ZTE is a bridge, not the house's actual gateway. The A1 router is the real internet gateway and DHCP server for `192.168.100.0/24`.
- LAN 1 → `<fill in: Beelink or switch>`
- LAN 2 → `<fill in: the other one>`

## Beelink (Proxmox host)

- Two physical NICs:
  - **`nic0`** (MAC `78:55:36:07:26:8d`) — the uplink, bridged to `vmbr0`. This is the cable that matters. If this NIC shows `NO-CARRIER` in `ip link`, the Beelink has no network — check this cable first.
  - **`nic1`** (MAC `78:55:36:07:26:8c`) — unused, not bridged.
- Reserved at `192.168.100.10` via DHCP binding on the A1 router.

## Switch

- Unmanaged 5-port gigabit switch (TP-Link LiteWave LS1005G or Dlinkgo, ~€15), added 2026-09-20 to expand past the ZTE's 2 LAN ports.
- Plugged into ZTE LAN `<1 or 2>`.
- Downstream: Desktop PC (wired), PS5 (wired).

## Desktop PC

- Reserved at `192.168.100.132` via DHCP binding — this IP is the NFS server target for Proxmox backups (`desktopbackup` storage). If this drifts, backups silently fail (has happened twice: 2026-09-09, 2026-09-20).

## PS5

- Wired to the switch (moved off WiFi on 2026-09-20, same day the switch was installed).

---

## Do not touch — critical cables

These two links, if disturbed, take down critical infrastructure. Treat as fixed once verified:

1. **ZTE ↔ A1 router (WiFi link)** — the house's only path to the internet. If this drops, everyone loses internet, not just the lab.
2. **ZTE LAN port ↔ Beelink `nic0`** — the lab's only uplink. If unplugged, OPNsense (and everything behind it: Services zone, Lab zone, Pi-hole, Docker services) goes dark. The house internet is unaffected (OPNsense is not the house gateway — see below).

## Key correction: OPNsense is not the house router

OPNsense routes traffic **between the lab zones only** (`10.10.20.0/24` Services, `10.10.30.0/24` Lab). Its "WAN" side is just a client on the house LAN (`192.168.100.2`). The actual house gateway is the **A1 router**. Confirmed 2026-09-20: powering off the Beelink entirely does not affect house WiFi/internet — only lab services (Docker, Pi-hole DNS, Proxmox-hosted anything) go down.

---

## History

### 2026-09-15 — Total outage from cable shuffle
Plugged PS5 into ZTE's WAN port (WAN-fault, red light) while troubleshooting → started unplugging/replugging cables to fix it → Beelink's `nic0` uplink came fully unplugged → OPNsense WAN down → lab zones offline. Diagnosed via `ip link` on the Beelink console (`nic0` showed `NO-CARRIER`). Fixed by reconnecting the cable. Follow-up WiFi hiccups on other devices were transient DHCP/radio settling, self-resolved.

### 2026-09-20 — Switch installed
Added an unmanaged 5-port switch, wiring both the desktop and PS5 through it into a single ZTE LAN port — permanently resolves the "out of LAN ports" root cause from Sep 15. See `network-recovery.md` for the outage response runbook this incident produced.
