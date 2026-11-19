#!/bin/bash
# Post-process a built OpenX6X00 image: inject the stock XARA binary (from
# the original v0.3.12 card image, since upstream x0rro/xara is discontinued)
# and zip the result.
set -e
B=/mnt/sd/sdl_1t/openx6x00-cn
MODEL=${1:-x6100}
case $MODEL in
    x6100) OUT=OpenX6X00-x6100-local-sdcard.img ;;
    x6200) OUT=OpenX6X00-x6200-local-sdcard.img ;;
    *) echo "usage: post_image.sh x6100|x6200"; exit 2 ;;
esac
case $MODEL in
    x6100) TREE=AetherX6100Buildroot ;;
    x6200) TREE=AetherX6200Buildroot ;;
esac
IMG=$B/work/$TREE/build/images/$OUT
[ -f "$IMG" ] || { echo "no $IMG"; exit 1; }

# unpack the original raw image locally (already present on the server via B/buildroot-trees? no, use /work)
# We keep the original images uploaded to the server next to the workspace:
RAW=/mnt/sd/sdl_1t/openx6x00-cn/raw/OpenX6X00-$MODEL-v0.3.12-sdcard.img

# Simpler: mount both images read-write via loop devices (offset for partition 2).
RAW_MP=$B/mnt-raw
NEW_MP=$B/mnt-new
mkdir -p "$RAW_MP" "$NEW_MP"
RAW_LOOP=$(losetup -f --show -o $((67584*512)) "$RAW")
NEW_LOOP=$(losetup -f --show -o $((67584*512)) "$IMG")
mount -o ro "$RAW_LOOP" "$RAW_MP"
mount -o rw "$NEW_LOOP" "$NEW_MP"

# Inject xara and its doc/ licences if missing from the new image
cp -a "$RAW_MP/usr/bin/xara" "$NEW_MP/usr/bin/xara" 2>/dev/null || echo "no xara in raw image"
cp -a "$RAW_MP/usr/share/x6100/licenses/xara" "$NEW_MP/usr/share/x6100/licenses/xara" 2>/dev/null || true

umount "$RAW_MP" "$NEW_MP"
losetup -d "$RAW_LOOP" "$NEW_LOOP"

# zip
cd "$(dirname "$IMG")"
ZIP=${OUT}.zip
rm -f "$ZIP"
zip -q "$ZIP" "$OUT"
echo "POST OK: $(pwd)/$ZIP"
ls -la "$ZIP"