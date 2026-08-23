#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
cd "$root"

if [ ! -f verification/Erdos506.zip ]; then
  echo "Missing verification/Erdos506.zip." >&2
  echo "Download Erdos506.zip from GitHub Release v1.0.0 and place it in verification/." >&2
  exit 2
fi

(cd verification && sha256sum -c Erdos506.zip.sha256)
rm -rf /tmp/erdos506-repository-quick
mkdir -p /tmp/erdos506-repository-quick
unzip -q verification/Erdos506.zip -d /tmp/erdos506-repository-quick
cd /tmp/erdos506-repository-quick/Erdos506
python3 verify.py
echo "ERDOS506_REPOSITORY_QUICK=PASSED"
