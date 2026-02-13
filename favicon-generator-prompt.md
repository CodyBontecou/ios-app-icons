# Favicon Generation Integration

Add AI-powered favicon generation to the portfolio generator using Replicate's SDXL model.

## Requirements

```bash
npm install replicate sharp
```

Environment variable needed: `REPLICATE_API_TOKEN`

## Implementation

Create a favicon generator that:

1. **Accepts a subject description** (e.g., "minimalist rocket logo") and optional style
2. **Calls Replicate SDXL** to generate a 1024x1024 base image
3. **Generates all standard favicon sizes:**
   - `favicon.ico` (multi-size: 16, 32, 48)
   - `favicon-16x16.png`
   - `favicon-32x32.png`
   - `apple-touch-icon.png` (180x180)
   - `android-chrome-192x192.png`
   - `android-chrome-512x512.png`
4. **Generates `site.webmanifest`** with icon references
5. **Outputs HTML snippet** for `<head>` inclusion

## Reference Implementation

```typescript
import Replicate from "replicate";
import sharp from "sharp";

const FAVICON_SIZES = {
  "favicon-16x16.png": 16,
  "favicon-32x32.png": 32,
  "apple-touch-icon.png": 180,
  "android-chrome-192x192.png": 192,
  "android-chrome-512x512.png": 512,
};

async function generateFavicon(subject: string, style = "flat") {
  const replicate = new Replicate({ auth: process.env.REPLICATE_API_TOKEN });

  const prompt = `App icon favicon for ${subject}, ${style} design,
    centered composition, single icon, no text, no watermark,
    white or transparent background, high quality, 1024x1024`;

  const output = await replicate.run(
    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    {
      input: {
        prompt,
        negative_prompt: "blurry, low quality, text, watermark, multiple icons",
        width: 1024,
        height: 1024,
        num_inference_steps: 30,
        guidance_scale: 7.5,
      },
    }
  );

  const imageUrl = Array.isArray(output) ? output[0] : output;
  const response = await fetch(imageUrl);
  const buffer = Buffer.from(await response.arrayBuffer());

  // Generate all sizes
  const favicons: Record<string, Buffer> = {};
  for (const [filename, size] of Object.entries(FAVICON_SIZES)) {
    favicons[filename] = await sharp(buffer)
      .resize(size, size, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png()
      .toBuffer();
  }

  return favicons;
}
```

## ICO File Generation

For `favicon.ico`, combine 16x16, 32x32, and 48x48 PNGs into a single ICO:

```typescript
async function createIco(imageBuffer: Buffer): Promise<Buffer> {
  const sizes = [16, 32, 48];
  const pngBuffers: Buffer[] = [];

  for (const size of sizes) {
    pngBuffers.push(
      await sharp(imageBuffer).resize(size, size).png().toBuffer()
    );
  }

  // ICO header: reserved(2) + type(2) + count(2) = 6 bytes
  const header = Buffer.alloc(6);
  header.writeUInt16LE(0, 0);
  header.writeUInt16LE(1, 2);
  header.writeUInt16LE(sizes.length, 4);

  // Build directory entries (16 bytes each) and concatenate image data
  let dataOffset = 6 + sizes.length * 16;
  const directory = Buffer.alloc(sizes.length * 16);
  const imageData: Buffer[] = [];

  sizes.forEach((size, i) => {
    const png = pngBuffers[i];
    const off = i * 16;
    directory.writeUInt8(size, off);
    directory.writeUInt8(size, off + 1);
    directory.writeUInt8(0, off + 2);
    directory.writeUInt8(0, off + 3);
    directory.writeUInt16LE(1, off + 4);
    directory.writeUInt16LE(32, off + 6);
    directory.writeUInt32LE(png.length, off + 8);
    directory.writeUInt32LE(dataOffset, off + 12);
    dataOffset += png.length;
    imageData.push(png);
  });

  return Buffer.concat([header, directory, ...imageData]);
}
```

## HTML Output

Generate this snippet for users to add to their `<head>`:

```html
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
```

## Webmanifest

```json
{
  "name": "App Name",
  "short_name": "App",
  "icons": [
    { "src": "/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png" }
  ],
  "theme_color": "#ffffff",
  "background_color": "#ffffff",
  "display": "standalone"
}
```

## Available Styles

- `flat` - Minimalist, solid colors, clean geometric shapes
- `modern` - Glossy, gradient, professional
- `pixel` - Retro 8-bit aesthetic
- `minimal` - Ultra minimalist, single color
- `playful` - Friendly, rounded, vibrant

Or pass a custom style string describing the desired aesthetic.
