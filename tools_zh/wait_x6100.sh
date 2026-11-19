#!/bin/bash
# Wait for the X6100 build to finish, then print a short status.
B=/mnt/sd/sdl_1t/openx6x00-cn
LOG=$B/build-x6100.log
for i in $(seq 1 120); do
  if docker ps --format '{{.Names}}' | grep -q '^x6build-x6100$'; then
    sleep 30
  else
    break
  fi
done
echo "=== tail ==="
tail -5 "$LOG"
echo "=== markers ==="
grep -nE "Linking CXX executable x6100_gui|>>> x6100-gui|x6100-gui.*Installing|mkbundle|local-sdcard|== done|Error|error:" "$LOG" | tail -15
echo "=== images ==="
ls -lh "$B/work/AetherX6100Buildroot/build/images/" 2>/dev/null | tail -5
docker ps --format '{{.Names}} {{.Status}}'