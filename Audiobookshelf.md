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
