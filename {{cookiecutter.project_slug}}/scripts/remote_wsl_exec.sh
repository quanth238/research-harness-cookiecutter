#!/usr/bin/env bash
set -euo pipefail

remote_ssh="${REMOTE_SSH:-{{ cookiecutter.remote_wsl_ssh_host }}}"
wsl_distro="${WSL_DISTRO:-{{ cookiecutter.remote_wsl_distro }}}"
workdir=""
raw_script=""

usage() {
  cat <<'EOF'
Usage: scripts/remote_wsl_exec.sh [--ssh USER@HOST] [--distro NAME] [--workdir PATH] -- COMMAND [ARG...]
   or: scripts/remote_wsl_exec.sh [--ssh USER@HOST] [--distro NAME] [--workdir PATH] --script 'bash script'

Runs a command inside the selected WSL distro through the Windows SSH host.
The command payload is base64 encoded to avoid shell quoting issues.
EOF
}

quote_arg() {
  printf '%q' "$1"
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
    --workdir)
      workdir="$2"
      shift 2
      ;;
    --script)
      raw_script="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "[remote-wsl-exec] unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ -n "$raw_script" ] && [ "$#" -gt 0 ]; then
  echo "[remote-wsl-exec] use either --script or COMMAND, not both" >&2
  exit 2
fi

payload="set -euo pipefail"
if [ -n "$workdir" ]; then
  payload="${payload}"$'\n'"cd $(quote_arg "$workdir")"
fi

if [ -n "$raw_script" ]; then
  payload="${payload}"$'\n'"${raw_script}"
else
  if [ "$#" -eq 0 ]; then
    echo "[remote-wsl-exec] missing command" >&2
    usage >&2
    exit 2
  fi
  command_line=""
  for arg in "$@"; do
    command_line="${command_line}$(quote_arg "$arg") "
  done
  payload="${payload}"$'\n'"${command_line}"
fi

encoded="$(printf '%s\n' "$payload" | base64 | tr -d '\n')"
remote_command="wsl.exe -d ${wsl_distro} -- bash -lc \"printf '%s' '${encoded}' | base64 -d | bash\""

exec ssh -o BatchMode=yes -o ConnectTimeout=15 "$remote_ssh" "$remote_command"
