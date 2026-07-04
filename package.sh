#!/usr/bin/env bash
set -euo pipefail

APP_NAME="JarvisAgentSwift"
PRODUCT_NAME="JarvisAgentSwiftApp"
BUILD_DIR=".build/release"
APP_BUNDLE="$APP_NAME.app"
CONTENTS_DIR="$APP_BUNDLE/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"
DMG_NAME="JarvisAgentV3.dmg"

echo "[1/5] Building release..."
swift build -c release

BIN_PATH="$BUILD_DIR/$PRODUCT_NAME"
if [[ ! -f "$BIN_PATH" ]]; then
  echo "Error: Built binary not found at $BIN_PATH" >&2
  exit 1
fi

echo "[2/5] Creating app bundle structure..."
rm -rf "$APP_BUNDLE"
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR"

cat > "$CONTENTS_DIR/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleName</key>
	<string>Jarvis Agent V3</string>
	<key>CFBundleIdentifier</key>
	<string>com.example.jarvisagentv3</string>
	<key>CFBundleExecutable</key>
	<string>JarvisAgentSwiftApp</string>
	<key>CFBundlePackageType</key>
	<string>APPL</string>
	<key>CFBundleShortVersionString</key>
	<string>1.0.0</string>
	<key>CFBundleVersion</key>
	<string>1</string>
	<key>LSMinimumSystemVersion</key>
	<string>14.0</string>
	<key>LSBackgroundOnly</key>
	<false/>
	<key>NSRequiresAquaSystemAppearance</key>
	<false/>
	<key>NSHighResolutionCapable</key>
	<true/>
	<key>NSMicrophoneUsageDescription</key>
	<string>需要麦克风权限以便语音交互（可选）。</string>
	<key>NSCameraUsageDescription</key>
	<string>需要摄像头权限以便视觉交互（可选）。</string>
	<key>NSAppleEventsUsageDescription</key>
	<string>用于与系统进行自动化交互。</string>
	<key>NSSystemAdministrationUsageDescription</key>
	<string>用于提升自动化可靠性（可选）。</string>
</dict>
</plist>
PLIST

echo "[3/5] Copying binary..."
cp "$BIN_PATH" "$MACOS_DIR/$PRODUCT_NAME"
chmod +x "$MACOS_DIR/$PRODUCT_NAME"

# Create a basic icon if desired (skipped). Ensure Applications link exists in DMG stage.

echo "[4/5] Creating DMG layout..."
WORK_DIR="dmg_tmp"
rm -rf "$WORK_DIR" "$DMG_NAME"
mkdir -p "$WORK_DIR"
cp -R "$APP_BUNDLE" "$WORK_DIR/"
ln -s /Applications "$WORK_DIR/Applications"

echo "[5/5] Building DMG..."
hdiutil create -volname "Jarvis Agent V3" -srcfolder "$WORK_DIR" -ov -format UDZO "$DMG_NAME"

echo "Done. DMG created: $DMG_NAME"
