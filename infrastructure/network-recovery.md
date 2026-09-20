# Network Down — Recovery Runbook

If the network's down, panic makes it worse. Don't touch cables yet. Work top to bottom — each step tells you where the break is before you fix anything.

## 1. Stop
Don't unplug/replug anything yet. Random cable swaps turn a 1-cable problem into a 5-cable mystery (ask past-you).

## 2. Isolate: upstream or local?
From your PC:
```
ping -c 3 1.1.1.1
```

- **Works** → internet's fine, problem is isolated to a specific device/service (not a full outage). Stop here, debug that device.
- **Fails** → continue.

## 3. Check the Beelink's uplink
Monitor + keyboard into the Beelink directly (network's down, can't SSH).
```
ip link
```

Look at `nic0` (the uplink to the switch/ZTE):
- **`NO-CARRIER`** → cable's unplugged or dead. Check the physical connection between Beelink and switch/ZTE. This was the Sep 15 root cause.
- **`state UP`, has carrier** → uplink's fine, continue.

## 4. Check OPNsense is running
Still on the Beelink console:
```
qm list
```

VM 102 (opnsense) should say `running`. If not:
```
qm start 102
```


## 5. Power-cycle the ZTE — last resort
Only if steps 2-4 show everything physically connected and running, but it's still dead. Unplug ZTE power, wait 30s, plug back in, wait 2-3 min for full boot.

## Notes
- OPNsense is **not** the house's internet gateway — the ZTE/A1 router is. Killing the Beelink only takes down lab services (Docker, Pi-hole, DNS chain), not household WiFi/internet.
- The ZTE has 2 LAN ports + 1 WAN port. **Never plug a device into WAN** — that's the ISP uplink, not for clients. See `infrastructure/physical-layer.md` for the port map.
