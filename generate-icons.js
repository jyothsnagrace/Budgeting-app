// Generate app icons from penguin-happy.png
// Run: npm run generate-icons

import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const SIZES = [72, 96, 128, 144, 152, 192, 384, 512];
const SOURCE_IMAGE = join(__dirname, 'src', 'assets', 'penguin-happy.png');
const PUBLIC_DIR = join(__dirname, 'public');

console.log('🐧 Generating Penny the Penguin app icons...\n');

// Check if source image exists
if (!fs.existsSync(SOURCE_IMAGE)) {
  console.error('❌ Source image not found:', SOURCE_IMAGE);
  console.log('\nPlease make sure penguin-happy.png exists in src/assets/');
  process.exit(1);
}

// Create public directory if it doesn't exist
if (!fs.existsSync(PUBLIC_DIR)) {
  fs.mkdirSync(PUBLIC_DIR, { recursive: true });
}

// Try to import sharp for image processing
let sharp;
try {
  sharp = (await import('sharp')).default;
  console.log('✅ Using sharp for high-quality image resizing\n');
} catch (err) {
  console.log('⚠️  Sharp not installed - attempting fallback method...\n');
}

if (sharp) {
  // Use sharp to resize images
  for (const size of SIZES) {
    const outputPath = join(PUBLIC_DIR, `icon-${size}.png`);
    
    try {
      await sharp(SOURCE_IMAGE)
        .resize(size, size, {
          fit: 'contain',
          background: { r: 255, g: 255, b: 255, alpha: 0 }
        })
        .png()
        .toFile(outputPath);
      
      console.log(`✅ Created icon-${size}.png (${size}x${size})`);
    } catch (error) {
      console.error(`❌ Error creating icon-${size}.png:`, error.message);
    }
  }
  
  console.log('\n🎉 All Penny icons generated successfully!');
  console.log('📱 Your PWA is ready with your cute penguin companion!');
  
} else {
  // Fallback: Use online tool or manual method
  console.log('📋 To generate icons without sharp, use one of these methods:\n');
  console.log('Method 1: Install sharp (recommended)');
  console.log('  npm install --save-dev sharp');
  console.log('  npm run generate-icons\n');
  console.log('Method 2: Use PWA Builder (online tool)');
  console.log('  1. Visit: https://www.pwabuilder.com/imageGenerator');
  console.log('  2. Upload: src/assets/penguin-happy.png');
  console.log('  3. Download all sizes');
  console.log('  4. Place in public/ folder\n');
  console.log('Method 3: Use ImageMagick (if installed)');
  console.log('  Run these commands in PowerShell:');
  SIZES.forEach(size => {
    console.log(`  magick src/assets/penguin-happy.png -resize ${size}x${size} public/icon-${size}.png`);
  });
  
  process.exit(1);
}

