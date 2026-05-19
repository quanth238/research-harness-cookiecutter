#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
remote_ssh="${REMOTE_SSH:-{{ cookiecutter.remote_wsl_ssh_host }}}"
wsl_distro="${WSL_DISTRO:-{{ cookiecutter.remote_wsl_distro }}}"

usage() {
  cat <<'EOF'
Usage: scripts/remote_wsl_doctor.sh [--ssh USER@HOST] [--distro NAME]

Checks the WSL GPU runner without modifying the remote machine.
Required checks: SSH, WSL, GPU visibility, Git, Python, Node/npm, Codex CLI login.
Optional checks: Docker and LaTeX.
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
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[remote-wsl-doctor] unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

doctor_script='
ok=0
required() {
  if "$@" >/tmp/remote-wsl-check.out 2>&1; then
    echo "[ok] $*"
  else
    echo "[fail] $*" >&2
    sed "s/^/[detail] /" /tmp/remote-wsl-check.out >&2 || true
    ok=1
  fi
}
optional() {
  if "$@" >/tmp/remote-wsl-check.out 2>&1; then
    echo "[ok] optional: $*"
  else
    echo "[warn] optional missing or unavailable: $*"
  fi
}

echo "[remote-wsl] user=$(whoami)"
echo "[remote-wsl] home=$HOME"
uname -a
df -h "$HOME" | tail -n 1

required command -v git
required git --version
required command -v python3
required python3 --version
required command -v node
required node --version
required command -v npm
required npm --version
required command -v codex
required codex --version
required codex login status
required command -v nvidia-smi
required nvidia-smi

optional command -v docker
if command -v docker >/dev/null 2>&1; then optional docker --version; fi
optional command -v latexmk
optional command -v tectonic

exit "$ok"
'

"$script_dir/remote_wsl_exec.sh" --ssh "$remote_ssh" --distro "$wsl_distro" --script "$doctor_script"
