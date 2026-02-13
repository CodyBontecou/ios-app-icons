#!/usr/bin/env npx tsx
/**
 * Standalone AI-powered favicon generator using Replicate's SDXL model.
 *
 * Usage:
 *   npx tsx favicon-generator.ts "your app description" --style flat
 *   npx tsx favicon-generator.ts "cat logo" --output ./my-favicons
 *
 * Requirements:
 *   npm install replicate sharp
 *
 * Environment:
 *   REPLICATE_API_TOKEN=your_token_here
 */

import Replicate from "replicate";
import sharp from "sharp";
import { writeFileSync, mkdirSync, existsSync } from "fs";
import { join } from "path";
import { parseArgs } from "util";

// Favicon sizes to generate
const FAVICON_SIZES: Record<string, number> = {
  "favicon-16x16.png": 16,
  "favicon-32x32.png": 32,
  "apple-touch-icon.png": 180,
  "android-chrome-192x192.png": 192,
  "android-chrome-512x512.png": 512,
};

// Style prompts
const STYLES: Record<string, string> = {
  flat: "flat design, minimalist, solid colors, clean geometric shapes, material design",
  modern: "modern app icon, glossy, gradient, professional, sleek design",
  pixel: "pixel art style, retro gaming aesthetic, 8-bit, crisp pixels",
  minimal: "ultra minimalist, single color, simple geometric shape, negative space",
  playful: "friendly, rounded shapes, vibrant colors, approachable design",
};

interface FaviconOptions {
  subject: string;
  style: string;
  customStyle?: string;
  output?: string;
  name: string;
}

function getApiToken(): string {
  const token = process.env.REPLICATE_API_TOKEN;
  if (!token) {
    console.error("Error: REPLICATE_API_TOKEN environment variable not set");
    console.error("Get your token at: https://replicate.com/account/api-tokens");
    process.exit(1);
  }
  return token;
}

async function generateImage(
  subject: string,
  style: string,
  customStyle?: string
): Promise<string> {
  const token = getApiToken();
  const replicate = new Replicate({ auth: token });

  const stylePrompt = customStyle || STYLES[style] || STYLES.flat;

  const prompt = `App icon favicon for ${subject}, ${stylePrompt},
centered composition, single icon, no text, no watermark,
white or transparent background, high quality, 1024x1024`;

  const negativePrompt = `blurry, low quality, text, words, letters, watermark,
signature, multiple icons, busy background, photograph, realistic photo`;

  console.log(`Generating image for: ${subject}`);
  console.log(`Style: ${stylePrompt.slice(0, 50)}...`);

  const output = await replicate.run(
    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    {
      input: {
        prompt,
        negative_prompt: negativePrompt,
        width: 1024,
        height: 1024,
        num_inference_steps: 30,
        guidance_scale: 7.5,
        scheduler: "K_EULER",
      },
    }
  );

  const imageUrl = Array.isArray(output) ? output[0] : output;
  return imageUrl as string;
}

async function downloadImage(url: string): Promise<Buffer> {
  console.log("Downloading generated image...");
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to download image: ${response.statusText}`);
  }
  const arrayBuffer = await response.arrayBuffer();
  return Buffer.from(arrayBuffer);
}

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

  // Build ICO file
  const numImages = pngBuffers.length;

  // ICO header (6 bytes): reserved (2), type (2), count (2)
  const header = Buffer.alloc(6);
  header.writeUInt16LE(0, 0); // Reserved
  header.writeUInt16LE(1, 2); // Type: 1 = ICO
  header.writeUInt16LE(numImages, 4); // Image count

  // Directory entries (16 bytes each)
  const dirEntrySize = 16;
  let dataOffset = 6 + numImages * dirEntrySize;

  const directory = Buffer.alloc(numImages * dirEntrySize);
  const imageDataBuffers: Buffer[] = [];

  pngBuffers.forEach((img, i) => {
    const offset = i * dirEntrySize;
    directory.writeUInt8(img.size < 256 ? img.size : 0, offset); // Width
    directory.writeUInt8(img.size < 256 ? img.size : 0, offset + 1); // Height
    directory.writeUInt8(0, offset + 2); // Color palette
    directory.writeUInt8(0, offset + 3); // Reserved
    directory.writeUInt16LE(1, offset + 4); // Color planes
    directory.writeUInt16LE(32, offset + 6); // Bits per pixel
    directory.writeUInt32LE(img.data.length, offset + 8); // Image size
    directory.writeUInt32LE(dataOffset, offset + 12); // Offset

    dataOffset += img.data.length;
    imageDataBuffers.push(img.data);
  });

  return Buffer.concat([header, directory, ...imageDataBuffers]);
}

async function generateFavicons(
  imageBuffer: Buffer,
  outputDir: string
): Promise<Record<string, number | string>> {
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }

  const generated: Record<string, number | string> = {};

  // Generate PNG favicons
  for (const [filename, size] of Object.entries(FAVICON_SIZES)) {
    const resized = await sharp(imageBuffer)
      .resize(size, size, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png({ compressionLevel: 9 })
      .toBuffer();

    writeFileSync(join(outputDir, filename), resized);
    generated[filename] = size;
    console.log(`  Created: ${filename} (${size}x${size})`);
  }

  // Generate multi-size ICO
  const icoBuffer = await createIco(imageBuffer);
  writeFileSync(join(outputDir, "favicon.ico"), icoBuffer);
  generated["favicon.ico"] = "16,32,48";
  console.log("  Created: favicon.ico (16x16, 32x32, 48x48)");

  // Save original high-res
  const original = await sharp(imageBuffer).png({ compressionLevel: 9 }).toBuffer();
  writeFileSync(join(outputDir, "original-1024.png"), original);
  generated["original-1024.png"] = 1024;
  console.log("  Created: original-1024.png (1024x1024)");

  return generated;
}

function generateWebmanifest(outputDir: string, name: string): void {
  const manifest = {
    name,
    short_name: name,
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
}

function generateHtmlSnippet(outputDir: string): void {
  const snippet = `<!-- Favicon HTML - Add to <head> -->
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
`;
  writeFileSync(join(outputDir, "favicon-html.txt"), snippet);
  console.log("  Created: favicon-html.txt (HTML snippet)");
}

async function main() {
  const { values, positionals } = parseArgs({
    allowPositionals: true,
    options: {
      style: { type: "string", default: "flat" },
      "custom-style": { type: "string" },
      output: { type: "string", short: "o" },
      name: { type: "string", default: "App" },
      help: { type: "boolean", short: "h" },
    },
  });

  if (values.help || positionals.length === 0) {
    console.log(`
AI Favicon Generator

Usage:
  npx tsx favicon-generator.ts <subject> [options]

Arguments:
  subject              Description of your favicon (e.g., "minimalist cat logo")

Options:
  --style <style>      Predefined style: flat, modern, pixel, minimal, playful (default: flat)
  --custom-style <s>   Custom style description (overrides --style)
  --output, -o <dir>   Output directory (default: ./favicons-{timestamp})
  --name <name>        App name for webmanifest (default: App)
  --help, -h           Show this help

Examples:
  npx tsx favicon-generator.ts "rocket ship logo" --style modern
  npx tsx favicon-generator.ts "coffee cup" --custom-style "watercolor, soft edges"
`);
    process.exit(0);
  }

  const subject = positionals[0];
  const style = values.style || "flat";
  const customStyle = values["custom-style"];
  const name = values.name || "App";

  const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, "").replace("T", "-");
  const outputDir = values.output || `favicons-${timestamp}`;

  console.log("\n" + "=".repeat(50));
  console.log("AI Favicon Generator");
  console.log("=".repeat(50) + "\n");

  // Generate image
  const imageUrl = await generateImage(subject, style, customStyle);

  // Download and process
  const imageBuffer = await downloadImage(imageUrl);

  console.log(`\nGenerating favicons in: ${outputDir}/`);
  const generated = await generateFavicons(imageBuffer, outputDir);

  // Generate manifest and HTML snippet
  generateWebmanifest(outputDir, name);
  generateHtmlSnippet(outputDir);

  // Save metadata
  const metadata = {
    subject,
    style: customStyle || style,
    source_url: imageUrl,
    generated_at: new Date().toISOString(),
    files: generated,
  };
  writeFileSync(join(outputDir, "metadata.json"), JSON.stringify(metadata, null, 2));

  console.log("\n" + "=".repeat(50));
  console.log(`Done! Favicons saved to: ${outputDir}/`);
  console.log("=".repeat(50) + "\n");
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
