#!/bin/bash
source /custom-cont-init.d/common.sh

SRC="/custom-cont-init.d/PicoClaw.desktop"

sync_desktop_file "$SRC" "/config/.config/autostart/PicoClaw.desktop"
sync_desktop_file "$SRC" "/config/Desktop/PicoClaw.desktop"
