# Homelab TODO

## Phase 0 cleanup
- [ ] Update README.md structure diagram to include security/soc-lab/
- [ ] Add docker-compose.yml + .env.example to each service folder
- [ ] Add CHANGELOG / History section to each service doc
- [ ] Add .gitignore (exclude .env, *.tar.gz backups, etc.)
- [ ] Verify all docs are consistent (host hardware specs across files)
- [ ] After 24h of normal ABS usage with no issues:
    - [ ] docker rm audiobookshelf_old
    - [ ] sudo rm -rf /home/admin/audiobookshelf/  (the old bind-mount folder)
    - [ ] Keep the tarball backup until next weekly backup
