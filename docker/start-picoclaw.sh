#!/bin/bash
SRC="/custom-cont-init.d/PicoClaw.desktop"

mkdir -p /config/.config/autostart
mkdir -p /config/Desktop
chown abc:abc /config/.config/autostart
chown abc:abc /config/Desktop

# Function to safely sync the desktop file if it has changed
sync_desktop_file() {
    local DEST="$1"
    if [ -f "$DEST" ]; then
        # Check if the file content is different
        if ! cmp -s "$SRC" "$DEST"; then
            echo "Updating $DEST (content changed). Moving existing to .bak"
            mv "$DEST" "${DEST}.bak"
            cp "$SRC" "$DEST"
            chown abc:abc "$DEST"
        else
            echo "$DEST is already up to date."
        fi
    else
        echo "Creating $DEST"
        cp "$SRC" "$DEST"
        chown abc:abc "$DEST"
    fi
}

sync_desktop_file "/config/.config/autostart/PicoClaw.desktop"
sync_desktop_file "/config/Desktop/PicoClaw.desktop"