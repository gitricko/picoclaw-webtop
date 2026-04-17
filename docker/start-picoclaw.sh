#!/bin/bash
SRC="/custom-cont-init.d/PicoClaw.desktop"

mkdir -p /config/.config/autostart
mkdir -p /config/Desktop
chown abc:abc /config/.config/autostart
chown abc:abc /config/Desktop

# Function to safely sync the desktop file if it has changed
sync_desktop_file() {
    local DEST="$1"
    local DEST_DIR
    local DEST_BASE
    local TMP_DEST

    DEST_DIR="$(dirname "$DEST")"
    DEST_BASE="$(basename "$DEST")"
    TMP_DEST="$(mktemp "${DEST_DIR}/.${DEST_BASE}.tmp.XXXXXX")" || return 1

    if [ -f "$DEST" ]; then
        # Check if the file content is different
        if ! cmp -s "$SRC" "$DEST"; then
            echo "Updating $DEST (content changed). Preparing replacement"
            if ! cp "$SRC" "$TMP_DEST"; then
                rm -f "$TMP_DEST"
                return 1
            fi
            if ! chown abc:abc "$TMP_DEST"; then
                rm -f "$TMP_DEST"
                return 1
            fi
            mv "$DEST" "${DEST}.bak"
            mv "$TMP_DEST" "$DEST"
        else
            echo "$DEST is already up to date."
            rm -f "$TMP_DEST"
        fi
    else
        echo "Creating $DEST"
        if ! cp "$SRC" "$TMP_DEST"; then
            rm -f "$TMP_DEST"
            return 1
        fi
        if ! chown abc:abc "$TMP_DEST"; then
            rm -f "$TMP_DEST"
            return 1
        fi
        mv "$TMP_DEST" "$DEST"
    fi
}

sync_desktop_file "/config/.config/autostart/PicoClaw.desktop"
sync_desktop_file "/config/Desktop/PicoClaw.desktop"