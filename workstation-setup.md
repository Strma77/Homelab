# Workstation Setup

This document describes my primary Linux workstation setup.
It serves as the **foundation system** for development, virtualization, and all homelab-related projects.

This machine acts as:

* The primary development environment
* The virtualization host (VirtualBox)
* The control plane for managing and testing homelab services

---

## Hardware

* **CPU:** Ryzen 7 3700X
* **RAM:** 32 GB DDR4
* **GPU:** RTX 2060 Super
* **Storage:**

  * 500 GB NVMe SSD — OS, development tools, virtual machines
  * 5.5 TB HDD — bulk data and shared storage for VMs

---

## Operating System

* Ubuntu 25.10 (Desktop)
* Clean Linux-only installation (Windows removed)
* Data disk preserved and mounted post-install

---

## Software Stack

### Development & Systems

* VS Code
* IntelliJ
* build-essential
* git

### Virtualization & Networking

* Docker
* VirtualBox
* Wireshark
* Cisco Packet Tracer

### Utilities

* Anki
* fastfetch
* micro

---

## Storage Usage Model

The HDD is used as a **single source of truth** for large datasets and shared resources.
Selected directories are exposed to virtual machines via VirtualBox shared folders, avoiding duplication while keeping data centralized on the host.

---

## Notable Issues & Fixes

* **Display scaling issues after installation**
  → Resolved via system update and user session restart

* **Browser performance issues (Brave snap package)**
  → Resolved by installing Brave from the official repository

---

## Constraints

* Single-machine setup (no dedicated always-on server hardware yet)
* VM availability depends on workstation uptime
* Networking experiments constrained by ISP-provided network equipment

---

## Scope Note

This document intentionally describes **only the host workstation**.
Details about VM configuration, networking architecture, VPNs, and self-hosted services are documented separately within their respective project directories.
