#!/usr/bin/env npx tsx
/**
 * Generate cute iOS app icons for SmartSkin — a gamified skincare routine tracker.
 * Uses Replicate's SDXL model to create multiple icon variants.
 *
 * Usage:
 *   npx tsx generate-smartskin-icon.ts
 */

import Replicate from "replicate";
import sharp from "sharp";
import { writeFileSync, mkdirSync, existsSync } from "fs";
import { join } from "path";

// Standard iOS app icon sizes
const IOS_SIZES = [1024, 180, 167, 152, 120, 76, 60, 40, 29, 20];

// --- Icon concept variants ---
const VARIANTS = [
  {
    name: "sparkle-drop",
    prompt: `Cute kawaii iOS app icon for a skincare app called SmartSkin, a single adorable water droplet character with big sparkly eyes and rosy cheeks, tiny sparkles and stars floating around it, soft pastel pink and lavender gradient background, rounded friendly shape, gamification feel with a tiny golden star badge on the droplet, flat design with subtle depth, clean vector style, single centered icon, no text, no watermark, 1024x1024`,
  },
  {
    name: "glowing-face",
    prompt: `Cute minimal iOS app icon for a skincare tracking app, a simple happy glowing face emoji with dewy skin and sparkle effects, soft peach and mint green gradient background, tiny achievement stars around the face, kawaii style, clean flat design with soft shadows, rounded and friendly, gamification elements like a small level-up arrow, single centered icon, no text, no watermark, 1024x1024`,
  },
  {
    name: "potion-bottle",
    prompt: `Adorable iOS app icon for a gamified skincare routine app, a cute pastel pink serum bottle with a kawaii smiling face, tiny bubbles and sparkles rising from it, soft lavender to baby blue gradient background, a small golden trophy or star sticker on the bottle, clean flat illustration style with soft rounded edges, cozy and inviting, single centered icon, no text, no watermark, 1024x1024`,
  },
  {
    name: "shield-heart",
    prompt: `Cute iOS app icon for SmartSkin skincare app, a soft rounded shield shape with a glowing heart inside representing skin protection, pastel coral pink and cream colors, tiny sparkle particles, small gamification badge ribbon at bottom, kawaii friendly style, clean modern flat design with subtle gradients, warm and inviting, single centered icon, no text, no watermark, 1024x1024`,
  },
];

const NEGATIVE_PROMPT = `blurry, low quality, text, words, letters, watermark, signature, multiple icons, busy background, photograph, realistic photo, ugly, deformed, noisy, grainy, dark, scary, complex background`;

function getApiToken(): string {
  const token = process.env.REPLICATE_API_TOKEN;
  if (!token) {
    console.error("Error: REPLICATE_API_TOKEN not set");
    process.exit(1);
  }
  return token;
}

async function generateImage(replicate: Replicate, prompt: string): Promise<string> {
  const output = await replicate.run(
    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    {
      input: {
        prompt,
        negative_prompt: NEGATIVE_PROMPT,
        width: 1024,
        height: 1024,
        num_inference_steps: 35,
        guidance_scale: 8,
        scheduler: "K_EULER",
      },
    }
  );
  const imageUrl = Array.isArray(output) ? output[0] : output;
  return imageUrl as string;
}

async function downloadImage(url: string): Promise<Buffer> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Download failed: ${response.statusText}`);
  return Buffer.from(await response.arrayBuffer());
}

async function generateiOSSizes(imageBuffer: Buffer, variantDir: string, name: string) {
  // Save original
  const original = await sharp(imageBuffer)
    .resize(1024, 1024, { fit: "cover" })
    .png({ compressionLevel: 9 })
    .toBuffer();

  writeFileSync(join(variantDir, `${name}-1024.png`), original);
  console.log(`    ${name}-1024.png`);

  // Generate all iOS sizes
  for (const size of IOS_SIZES) {
    const resized = await sharp(original)
      .resize(size, size, { fit: "cover" })
      .png({ compressionLevel: 9 })
      .toBuffer();
    writeFileSync(join(variantDir, `AppIcon-${size}.png`), resized);
    console.log(`    AppIcon-${size}.png`);
  }
}

async function main() {
  const timestamp = new Date()
    .toISOString()
    .slice(0, 19)
    .replace(/[:-]/g, "")
    .replace("T", "_");

  const outputDir = join("output", `smartskin-${timestamp}`);
  mkdirSync(outputDir, { recursive: true });

  const token = getApiToken();
  const replicate = new Replicate({ auth: token });

  console.log("\n🧴✨ SmartSkin Icon Generator");
  console.log("━".repeat(50));
  console.log(`Generating ${VARIANTS.length} cute icon variants...\n`);

  for (const variant of VARIANTS) {
    console.log(`  🎨 Variant: ${variant.name}`);
    console.log(`     Generating with Replicate SDXL...`);

    try {
      const imageUrl = await generateImage(replicate, variant.prompt);
      console.log(`     Downloading...`);
      const imageBuffer = await downloadImage(imageUrl);

      const variantDir = join(outputDir, variant.name);
      mkdirSync(variantDir, { recursive: true });

      // Save metadata
      writeFileSync(
        join(variantDir, "metadata.json"),
        JSON.stringify(
          {
            name: variant.name,
            prompt: variant.prompt,
            source_url: imageUrl,
            generated_at: new Date().toISOString(),
          },
          null,
          2
        )
      );

      console.log(`     Generating iOS icon sizes:`);
      await generateiOSSizes(imageBuffer, variantDir, variant.name);
      console.log(`     ✅ Done!\n`);
    } catch (err: any) {
      console.error(`     ❌ Failed: ${err.message}\n`);
    }
  }

  console.log("━".repeat(50));
  console.log(`✅ All variants saved to: ${outputDir}/`);
  console.log(`\n   Variants:`);
  for (const v of VARIANTS) {
    console.log(`     📁 ${v.name}/`);
  }
  console.log();
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
