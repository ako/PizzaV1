#!/usr/bin/env bash
# Apply every MDL script in mdlsource/ in order. A flow whose change cannot be
# spliced (MDL-V1-REBUILD) is rebuilt deliberately with tools/mdl_rebuild.py.
# Afterwards a second pass must report everything unchanged.
set -euo pipefail
cd "$(dirname "$0")/.."
for f in mdlsource/*.mdl; do
  out=$(./mxcli exec "$f" -p GitPizza.mpr 2>&1 || true)
  if grep -q 'cannot be spliced' <<<"$out"; then
    # write every other statement first (new flows the rebuilt ones call), then rebuild
    ./mxcli exec "$f" -p GitPizza.mpr --continue-on-error >/dev/null 2>&1 || true
    python3 tools/mdl_rebuild.py "$f"
    out=$(./mxcli exec "$f" -p GitPizza.mpr 2>&1 || true)
  fi
  if grep -q -E '✗|Refusing' <<<"$out"; then echo "FAILED: $f"; echo "$out" | grep -E '✗|Refusing' | head -5; exit 1; fi
  changed=$(grep -c -E '^(Created|Modified|Dropped|Added|Granted|Updated)' <<<"$out" || true)
  echo "$f: $changed change(s)"
done
