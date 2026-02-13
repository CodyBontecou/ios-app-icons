#!/usr/bin/env npx tsx
/**
 * Generate a "CC" text favicon in all standard sizes.
 */

import sharp from "sharp";
import { writeFileSync, mkdirSync, existsSync } from "fs";
import { join } from "path";

const FAVICON_SIZES: Record<string, number> = {
  "favicon-16x16.png": 16,
  "favicon-32x32.png": 32,
  "apple-touch-icon.png": 180,
  "android-chrome-192x192.png": 192,
  "android-chrome-512x512.png": 512,
};

// Clean black & white "CC" — elegant serif font, no background
const svgFavicon = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="white"/>
  <text
    x="256" y="272"
    font-family="Georgia, 'Times New Roman', Times, serif"
    font-size="320"
    font-weight="400"
    fill="black"
    text-anchor="middle"
    dominant-baseline="central"
    letter-spacing="-18"
  >CC</text>
</svg>
`;

async function createIco(imageBuffer: Buffer): Promise<Buffer> {
  const sizes = [16, 32, 48];
  const pngBuffers: { size: number; data: Buffer }[] = [];

  for (const size of sizes) {
    const resized = await sharp(imageBuffer)
      .resize(size, size, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png()
      .toBuffer();
    pngBuffers.push({ size, data: resized });
  }

  const numImages = pngBuffers.length;
  const header = Buffer.alloc(6);
  header.writeUInt16LE(0, 0);
  header.writeUInt16LE(1, 2);
  header.writeUInt16LE(numImages, 4);

  const dirEntrySize = 16;
  let dataOffset = 6 + numImages * dirEntrySize;
  const directory = Buffer.alloc(numImages * dirEntrySize);
  const imageDataBuffers: Buffer[] = [];

  pngBuffers.forEach((img, i) => {
    const offset = i * dirEntrySize;
    directory.writeUInt8(img.size < 256 ? img.size : 0, offset);
    directory.writeUInt8(img.size < 256 ? img.size : 0, offset + 1);
    directory.writeUInt8(0, offset + 2);
    directory.writeUInt8(0, offset + 3);
    directory.writeUInt16LE(1, offset + 4);
    directory.writeUInt16LE(32, offset + 6);
    directory.writeUInt32LE(img.data.length, offset + 8);
    directory.writeUInt32LE(dataOffset, offset + 12);
    dataOffset += img.data.length;
    imageDataBuffers.push(img.data);
  });

  return Buffer.concat([header, directory, ...imageDataBuffers]);
}

async function main() {
  const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, "").replace("T", "_");
  const outputDir = join("output", `cc-favicon-${timestamp}`);

  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }

  console.log("\n=== Generating CC Favicon ===\n");

  // Render SVG to 512px PNG base image
  const baseBuffer = await sharp(Buffer.from(svgFavicon))
    .resize(512, 512)
    .png()
    .toBuffer();

  // Save SVG source
  writeFileSync(join(outputDir, "favicon.svg"), svgFavicon.trim());
  console.log("  Created: favicon.svg");

  // Generate PNG favicons
  for (const [filename, size] of Object.entries(FAVICON_SIZES)) {
    const resized = await sharp(baseBuffer)
      .resize(size, size, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png({ compressionLevel: 9 })
      .toBuffer();

    writeFileSync(join(outputDir, filename), resized);
    console.log(`  Created: ${filename} (${size}x${size})`);
  }

  // Generate ICO
  const icoBuffer = await createIco(baseBuffer);
  writeFileSync(join(outputDir, "favicon.ico"), icoBuffer);
  console.log("  Created: favicon.ico (16, 32, 48)");

  // Save original high-res
  const original = await sharp(Buffer.from(svgFavicon))
    .resize(1024, 1024)
    .png({ compressionLevel: 9 })
    .toBuffer();
  writeFileSync(join(outputDir, "original-1024.png"), original);
  console.log("  Created: original-1024.png (1024x1024)");

  // Generate webmanifest
  const manifest = {
    name: "CC",
    short_name: "CC",
    icons: [
      { src: "/android-chrome-192x192.png", sizes: "192x192", type: "image/png" },
      { src: "/android-chrome-512x512.png", sizes: "512x512", type: "image/png" },
    ],
    theme_color: "#ffffff",
    background_color: "#ffffff",
    display: "standalone",
  };
  writeFileSync(join(outputDir, "site.webmanifest"), JSON.stringify(manifest, null, 2));
  console.log("  Created: site.webmanifest");

  // Generate HTML snippet
  const snippet = `<!-- Favicon HTML - Add to <head> -->
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
`;
  writeFileSync(join(outputDir, "favicon-html.txt"), snippet);
  console.log("  Created: favicon-html.txt");

  console.log(`\n✅ Done! Favicons saved to: ${outputDir}/\n`);
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
