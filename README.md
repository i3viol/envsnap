# envsnap

> A CLI tool to capture, diff, and restore environment variable snapshots across dev/staging/prod contexts.

---

## Installation

```bash
pip install envsnap
```

Or with [pipx](https://pypa.github.io/pipx/) for isolated installs:

```bash
pipx install envsnap
```

---

## Usage

**Capture a snapshot of your current environment:**
```bash
envsnap capture --context dev
```

**Diff two snapshots:**
```bash
envsnap diff dev staging
```

**Restore a snapshot:**
```bash
envsnap restore dev
```

**List saved snapshots:**
```bash
envsnap list
```

Snapshots are stored locally in `~/.envsnap/` as encrypted JSON files. Sensitive values are masked by default in diff output.

---

## Example

```bash
$ envsnap capture --context staging
✔ Snapshot saved: staging (42 variables captured)

$ envsnap diff dev staging
+ DATABASE_URL   postgres://staging-host/db
- DATABASE_URL   postgres://localhost/db
~ LOG_LEVEL      debug → info
```

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

[MIT](LICENSE) © envsnap contributors