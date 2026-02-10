# HomeLab

This repository documents my hands-on learning in building and operating a small, self-hosted homelab on personal hardware.

The focus is on **understanding infrastructure through practice**, including:
- Linux system administration
- Virtualization on a single host
- Dockerized self-hosted services
- Networking fundamentals and real-world constraints
- Security considerations for private services

This is not a production environment.  
It is a learning-focused lab shaped by **actual limitations** such as ISP-controlled networking equipment and a single-machine setup.

---

## Repository Contents

- **README.md**  
  High-level overview and intent of the homelab.

- **workstation-setup.md**  
  Describes the host Linux workstation that serves as the foundation for all virtualization and lab work.

- **Audiobookshelf.md**  
  A documented project covering the deployment of a self-hosted Audiobookshelf service, including networking decisions, storage strategy, and remote access under ISP constraints.

Each document focuses on *why* decisions were made, not just *what* commands were run.

---

## Scope & Philosophy

The goal of this homelab is to:
- Learn by building under constraints
- Make architectural trade-offs explicit
- Document failures, fixes, and lessons learned
- Develop skills transferable to real infrastructure roles

The lab will evolve over time as hardware, networking control, and experience improve.
