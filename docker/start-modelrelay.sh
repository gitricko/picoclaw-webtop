#!/bin/bash
source /custom-cont-init.d/common.sh || exit 1

SRC="/custom-cont-init.d/ModelRelay.desktop"

add_model_if_missing() {
    local file="$1"

    jq '
      if (.model_list | map(select(.model_name == "modelrelay")) | length) == 0 then
        .model_list += [{
          "model_name": "modelrelay",
          "model": "openai/auto-fastest",
          "api_base": "http://localhost:7352/v1"
        }]
      else
        .
      end
    ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
}

# Prep nodejs npm for ModelRelay 
rm -rf /config/.npm
chown abc:abc -R  /usr/local/lib/node_modules &
chown abc:abc -R  /usr/local/bin &

# Sync desktop file for autostart and desktop icon
sync_desktop_file "$SRC" "/config/.config/autostart/ModelRelay.desktop"
sync_desktop_file "$SRC" "/config/Desktop/ModelRelay.desktop"

# Add modelrelay model to picoclaw's config
# /config/picoclaw/config.json 
(
    sleep 15
    add_model_if_missing "/config/.picoclaw/config.json"
    chown abc:abc "/config/.picoclaw/config.json"
) &
