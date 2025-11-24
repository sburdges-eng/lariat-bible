#!/usr/bin/env node
/**
 * Generate app icons from SVG source
 * Run: node scripts/generate-icons.js
 * Requires: sharp (npm install sharp)
 */

const sharp = require('sharp');
const path = require('path');
const fs = require('fs');

const assetsDir = path.join(__dirname, '..', 'assets');
const svgPath = path.join(assetsDir, 'logo.svg');

// Icon sizes needed for different platforms
const sizes = {
  // General PNG icons
  png: [16, 32, 48, 64, 128, 256, 512, 1024],
  // macOS icns requires these specific sizes
  mac: [16, 32, 64, 128, 256, 512, 1024],
  // Windows ico
  win: [16, 24, 32, 48, 64, 128, 256]
};

async function generateIcons() {
  console.log('Generating icons from', svgPath);

  // Read SVG
  const svgBuffer = fs.readFileSync(svgPath);

  // Create icons directory if needed
  const iconsDir = path.join(assetsDir, 'icons');
  if (!fs.existsSync(iconsDir)) {
    fs.mkdirSync(iconsDir, { recursive: true });
  }

  // Generate PNG icons
  console.log('Generating PNG icons...');
  for (const size of sizes.png) {
    const outputPath = path.join(iconsDir, `icon-${size}.png`);
    await sharp(svgBuffer)
      .resize(size, size)
      .png()
      .toFile(outputPath);
    console.log(`  Created ${size}x${size} PNG`);
  }

  // Copy main icon.png (512x512)
  const mainIconPath = path.join(assetsDir, 'icon.png');
  await sharp(svgBuffer)
    .resize(512, 512)
    .png()
    .toFile(mainIconPath);
  console.log('Created main icon.png (512x512)');

  // For ICO and ICNS, we'll create the PNGs and note that
  // additional tools are needed for the final conversion
  console.log('\n--- Icon Generation Complete ---');
  console.log('\nTo create platform-specific icons:');
  console.log('\nmacOS (.icns):');
  console.log('  Use iconutil or png2icns:');
  console.log('  mkdir icon.iconset');
  console.log('  cp icons/icon-16.png icon.iconset/icon_16x16.png');
  console.log('  cp icons/icon-32.png icon.iconset/icon_16x16@2x.png');
  console.log('  ... (repeat for all sizes)');
  console.log('  iconutil -c icns icon.iconset -o icon.icns');
  console.log('\nWindows (.ico):');
  console.log('  Use png2ico or online converter');
  console.log('  Or electron-builder will auto-convert from PNG');
}

generateIcons().catch(console.error);
