#!/bin/bash
# Correct the file:// tarball SOURCE names to match the actual downloaded files,
# then rebuild the x6100 GUI package (deps already cached).
set -e
B=/mnt/sd/sdl_1t/openx6x00-cn
WORK=$B/work
DL=$WORK/dl-tar

set_source() { local mk=$1 var=$2 file=$3
  sed -i "s|^${var}_SOURCE = .*|${var}_SOURCE = ${file}|" "$mk"
  sed -i "s|^${var}_SITE = .*|${var}_SITE = file:///work/dl-tar|" "$mk"
  sed -i "s|^${var}_SITE_METHOD = git|${var}_SITE_METHOD = file|" "$mk"
  grep -E "^${var}_SOURCE|^${var}_SITE" "$mk"
}

echo "=== X6100 control ==="
set_source "$WORK/AetherX6100Buildroot/br2_external/package/aether-x6100-control/aether-x6100-control.mk" \
  AETHER_X6100_CONTROL aether-x6100-control-v0.16.3.tar.gz

echo "=== X6200 control ==="
set_source "$WORK/AetherX6200Buildroot/br2_external/package/aether-x6200-control/aether-x6200-control.mk" \
  AETHER_X6200_CONTROL aether-x6200-control-v0.1.1.tar.gz

echo "=== ft8lib (both trees) ==="
for t in AetherX6100Buildroot AetherX6200Buildroot; do
  set_source "$WORK/$t/br2_external/package/ft8lib/ft8lib.mk" \
    FT8LIB ft8lib-73b0db861dc41c7ca9f3dedc73ee148daa06dd0e.tar.gz
done

echo "=== rtw88 (X6200) ==="
RTW=$(grep -rl "RTW88_SITE_METHOD" "$WORK/AetherX6200Buildroot/br2_external/package/rtw88/" | head -1)
[ -n "$RTW" ] && set_source "$RTW" RTW88 rtw88-461b696b51317ba4ca585a4ddb32f2e72cd4efc9.tar.gz || echo "rtw88 mk not found"

echo "FIXED"