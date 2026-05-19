#!/usr/bin/env bash
set -euo pipefail

remote_ssh="${REMOTE_SSH:-{{ cookiecutter.remote_wsl_ssh_host }}}"
wsl_distro="${WSL_DISTRO:-{{ cookiecutter.remote_wsl_distro }}}"
source_codex_home="${CODEX_HOME:-$HOME/.codex}"

usage() {
  cat <<'EOF'
Usage: scripts/sync_codex_auth_to_wsl.sh [--ssh USER@HOST] [--distro NAME] [--codex-home PATH]

Copies only auth.json and config.toml from the local Codex home into ~/.codex
inside the WSL distro. The script never prints, parses, or modifies secret
contents. Run only after the operator has explicitly approved auth sync.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --ssh)
      remote_ssh="$2"
      shift 2
      ;;
    --distro)
      wsl_distro="$2"
      shift 2
      ;;
    --codex-home)
      source_codex_home="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[sync-codex-auth] unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ ! -s "$source_codex_home/auth.json" ]; then
  echo "[sync-codex-auth] missing local auth.json at $source_codex_home/auth.json" >&2
  exit 1
fi
if [ ! -s "$source_codex_home/config.toml" ]; then
  echo "[sync-codex-auth] missing local config.toml at $source_codex_home/config.toml" >&2
  exit 1
fi

echo "[sync-codex-auth] syncing auth.json and config.toml to WSL ~/.codex"
tar -C "$source_codex_home" -cf - auth.json config.toml \
  | ssh -o BatchMode=yes -o ConnectTimeout=15 "$remote_ssh" \
      "wsl.exe -d ${wsl_distro} -- bash -lc 'mkdir -p ~/.codex && tar -C ~/.codex -xf - && chmod 700 ~/.codex && chmod 600 ~/.codex/auth.json ~/.codex/config.toml'"

ssh -o BatchMode=yes -o ConnectTimeout=15 "$remote_ssh" \
  "wsl.exe -d ${wsl_distro} -- bash -lc 'test -s ~/.codex/auth.json && test -s ~/.codex/config.toml && echo \"[sync-codex-auth] WSL Codex auth files are present\" && if command -v codex >/dev/null 2>&1; then codex login status; else echo \"[sync-codex-auth] codex CLI not installed yet\"; fi'"
