## Networking Configuration

The Ubuntu Server VM is connected to the local network using a bridged network adapter.
This allows the VM to behave as a first-class host on the LAN and simplifies VPN and service access.

### IP Addressing
- Interface: `enp0s3`
- Static IP: `192.168.100.50/24`
- Gateway: `192.168.100.1`
- Broadcast: `192.168.100.255`

A static IP was configured to ensure consistent addressing for:
- VPN endpoint configuration
- Future port forwarding
- Service accessibility

### Routing
- Default route via `192.168.100.1`
- Internet connectivity verified via IP and DNS resolution

### Configuration Method
- Static IP configured using netplan (`50-cloud-init.yaml`)
- DHCP disabled on the primary interface
- Configuration validated using routing and connectivity tests

## Constraints & Environment Limitations

The project is deployed in a residential network using an ISP-provided ZTE F8648P XGS-PON ONT.

The ONT exposes only a limited user-level management interface and does not provide access to:
- NAT configuration
- Port forwarding
- Firewall rules

As a result, inbound connections from the public internet to the local network are not possible in the default configuration.
This directly impacts VPN designs that rely on incoming connections to a home-hosted server.

### Design Implications

Due to the restricted capabilities of the ISP-provided ONT, the initial architecture must avoid reliance on inbound port forwarding.

This constraint informed the decision to:
- Treat remote access as a networking problem rather than a tooling problem
- Prioritize architectures that function behind ISP-controlled NAT
- Plan for alternative VPN topologies that do not require exposed home services

## Remote Access Strategy

### Phase 1 – Local VPN Testing
- WireGuard deployed inside the Ubuntu Server VM using Docker
- VPN functionality validated within the local network

### Phase 2 – ISP-Constrained Environment
- ISP ONT does not permit inbound port forwarding
- Direct remote VPN access from the internet is not possible

### Phase 3 – Planned Solutions
One of the following approaches will be implemented:
- Bridge mode on ISP ONT with a user-controlled router
- Outbound-only VPN architecture using an intermediate VPS
- Migration of edge networking to user-owned hardware

## Roadmap

### Completed
- Ubuntu Server VM deployment
- Static IP configuration
- Docker-based service architecture
- Local WireGuard deployment

### In Progress
- Evaluation of remote access strategies under ISP constraints

### Planned
- Migration to bridge mode or user-controlled router
- Secure remote access via VPN
- Audiobookshelf deployment behind authenticated access
- Optional HTTPS reverse proxy
