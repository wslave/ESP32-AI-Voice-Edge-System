# Main Modules

The `main` directory now keeps two parts:

- ESP32 firmware source code restored from the original hardware project.
- `manager-web`, the retained browser-based management UI.

The backend server, Java management API, and mobile management app from the imported server project have been removed. The Web UI is kept as a separate frontend module so it can be adapted to the ESP32 voice interaction workflow without carrying the full server stack.

## ESP32 Firmware

Core firmware files live directly under `main`, with board, audio, display, LED, protocol, OTA, settings, and system information modules grouped in their existing subdirectories.

## Web UI

The Web UI lives in `main/manager-web`.

```bash
cd main/manager-web
npm ci
npm run build
```

Build output is generated under `main/manager-web/dist` and is intentionally ignored by Git.

