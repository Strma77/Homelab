# HomeLab

This repository documents my hands-on learning in building and operating a self-hosted homelab on personal hardware.

The focus is on **understanding infrastructure through practice**, including:

- Linux system administration
- Virtualization on a single host
- Dockerized self-hosted services
- Networking fundamentals and real-world constraints
- Security considerations for private services

This is not a production environment. It is a learning-focused lab shaped by actual limitations such as ISP-controlled networking equipment and a single-machine setup.

---

## Recent Changes

- **2026-05:** Migrated Audiobookshelf from hand-typed `docker run` → declarative `docker-compose.yml` with named volumes, healthcheck, and custom bridge network
- **2026-05:** Adopted GitOps workflow — repo as source of truth, VM pulls to deploy
- **2026-05:** Removed deprecated Navidrome service (to be revisited)
- **2026-03:** SOC lab built and operational with attack/detect loop verified

---

## Current State

**Phase:** 0 — Foundation Hardening (in progress)

**Live services:**
- Audiobookshelf — audiobook server, Docker Compose, named volumes, HTTP healthcheck
- SOC Lab — Wazuh + Kali + Metasploitable2, isolated VirtualBox network

**Workflow:**
- Source of truth: this Git repo
- Edits happen on host desktop, deploys happen on VM via `git pull`
- All services run as code (compose files in repo), not hand-typed commands

---

## Repository Structure

```
homelab/
├── README.md
├── TODO.md
├── .gitignore
├── workstation-setup.md
├── security/
│   └── soc-lab/
│       ├── README.md
│       └── [screenshots: Terminal, Wazuh, WazuhEvents]
└── services/
    └── audiobookshelf/
        ├── Audiobookshelf.md
        └── docker-compose.yml
```

---

## Services

### Audiobookshelf

Self-hosted replacement for Audible. Personal audiobook library accessible from any device via Tailscale, no public exposure required.

→ [Audiobookshelf.md](services/audiobookshelf/Audiobookshelf.md)

### SOC Security Lab

Home-built Security Operations Center lab using Wazuh SIEM, Kali Linux and Metasploitable2. Simulates real attack scenarios and detects them using MITRE ATT&CK framework mapping.

→ [SOC Lab](security/soc-lab/README.md)

---

## Infrastructure

All services run inside a single Ubuntu Server 24.04.4 LTS VM on VirtualBox, connected to the LAN via a bridged network adapter. Remote access is handled by Tailscale mesh VPN — no port forwarding required.

→ [workstation-setup.md](workstation-setup.md)

---

## Workflow

The repo is the source of truth, not the running services.

- All edits happen on the host desktop in Git
- Commits get pushed to GitHub
- The VM clones the same repo and pulls to deploy (`git pull` + `docker compose up -d`)
- Nothing is configured directly on the VM — if it's not in Git, it doesn't exist

Authentication is via SSH keys, not HTTPS. Future Phase 3 introduces proper CI/CD.

---

## Core Rules

1. **Every new technology must solve a problem created by the previous phase.** No tutorial addiction.
2. **If you can't explain WHY a service exists in one sentence, don't deploy it yet.**
3. **Exit checkpoints gate each phase, not time.** A phase ends when its goals are met, not when six weeks pass.
4. **Break/fix drills weekly.** Deliberately break something, diagnose it, document the recovery.
5. **Everything in Git with meaningful commits.** No hand-typed `docker run` commands.
6. **GUI tools are for observability, not for hiding CLI knowledge.** Portainer is fine; not knowing what `docker ps` does isn't.
7. **The homelab is the gym, not the competition.** Production-grade habits, not production-grade scale.

### Things deliberately NOT touched yet
- Kubernetes — Docker + Linux mastery first, or you just memorize YAML without understanding systems
- Multi-node clustering — operational maturity on one node before scaling
- Heavy cloud focus (AWS/Azure) — local infrastructure pain teaches WHY cloud exists; learn local first
- Terraform before Ansible — Ansible is simpler and more immediately useful
- Certifications before built projects — certs after skills, not instead of skills

---

## Roadmap

A 5-phase plan, gated by exit checkpoints rather than time. Detailed phase checklists at [strma77.github.io](https://strma77.github.io/).

### Phase 0 — Foundation Hardening *(in progress)*
**Goal:** Build deep Docker Compose + Linux administration fluency before adding any new technology.

- **Adding:** Nginx Proxy Manager, Pi-hole, WireGuard, Uptime Kuma, Portainer
- **Hardening:** SSH key-only auth, UFW, automated backups via rsync + cron
- **Exit:** Every service in Compose, in Git, with healthchecks. Backups automated and tested. Can recover any container without Googling. Can explain the entire setup to someone else without notes.

### Phase 1 — Infrastructure Mindset
**Goal:** Stop being someone who runs services and start being someone who builds infrastructure.

- **Adding:** Proxmox (replaces VirtualBox), pfSense/OPNsense as virtual router, VLAN segmentation
- **Migrating:** All Phase 0 services into Proxmox VMs/LXC containers across segmented networks
- **Exit:** New VM from template in under 5 minutes. VLANs actually isolate traffic. SOC lab on its own isolated VLAN. Network topology diagram exists and matches reality.

### Phase 2 — Monitoring + Automation
**Goal:** Stop being the manual layer in your own infrastructure. Get observability and start automating the repetitive.

- **Adding:** Prometheus, Grafana, Loki, Node Exporter, Ansible, Gitea, expanded SOC lab with custom Wazuh rules
- **Exit:** Find out about problems from alerts, not by noticing. New VM provisioning is an Ansible playbook, not manual SSH. All configs live in Git.

### Phase 3 — Advanced Networking + DevOps
**Goal:** Junior infrastructure engineer skill set. CI/CD, internal PKI, infrastructure-as-code as a daily habit.

- **Adding:** Traefik (replaces NPM), Step-CA for internal certificates, Suricata IDS/IPS, GitHub Actions or Gitea Actions, self-hosted runners, Terraform for Proxmox
- **Exit:** Push code, watch it deploy. Internal services served over HTTPS with my own CA. Infrastructure changes go through Git, not SSH.

### Phase 4 — AI Integration + MLOps
**Goal:** AI as a tool integrated into existing infrastructure, not a standalone toy.

- **Adding:** Ollama with GPU passthrough, Open WebUI, RAG pipeline over the homelab documentation, log analysis assistant pulling from Loki
- **Exit:** Local LLM is woven into the stack. Can articulate the difference between inference, RAG, and fine-tuning from hands-on experience.

---

## Philosophy

- Learn by building under real constraints
- Document failures and fixes, not just commands
- Make architectural decisions explicit and reproducible
- Build skills transferable to real infrastructure roles
