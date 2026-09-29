# Imagen - AI Image Generation Skill

A Claude Code skill that generates images using Google Gemini's image generation model. Simply ask Claude to create an image during any coding session, and it will generate and save it for you.

**Cross-Platform**: Works on Windows, macOS, and Linux.

## Quick Start

### 1. Install the Skill

```bash
# Via plugin marketplace (recommended)
/plugin install imagen@ai-skills

# Or add the entire marketplace
/plugin marketplace add sanjay3290/ai-skills
```

### 2. Set Your API Key

Get an API key from [Google AI Studio](https://aistudio.google.com/). Image generation has no free tier, so billing must be enabled for the key:

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

**Windows (CMD):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**macOS/Linux:**
```bash
export GEMINI_API_KEY="your-api-key-here"

# Add to ~/.zshrc or ~/.bashrc to persist
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
```

### 3. Use It!

Just ask Claude to generate an image during any conversation:

```
"Generate an image of a sunset over mountains"
"I need a hero image for my landing page"
"Create an app icon for a weather app"
```

## How It Works

When you mention needing an image, Claude will automatically:
1. Recognize the request and activate this skill
2. Call the Google Gemini API with your prompt
3. Save the generated image to your project
4. Tell you where to find it

## Features

- **Cross-Platform**: Python script works on Windows, macOS, and Linux
- **Automatic Activation**: Claude detects when you need an image
- **Multiple Sizes**: 512px, 1K (default), 2K or 4K resolution
- **Aspect Ratios**: 1:1 (default), 16:9, 9:16 and more via `--aspect`
- **JPEG Output**: the API only returns JPEG (no transparency)
- **Custom Output Paths**: Save images wherever you need them
- **Frontend Ready**: Perfect for UI development, placeholders, icons
- **Documentation Images**: Generate diagrams, illustrations, flowcharts

## Usage Examples

### During Frontend Development
```
You: "I'm building a dashboard. Generate a placeholder chart image."
Claude: *generates and saves image* "Created the image at ./assets/chart-placeholder.jpg"
```

### For Documentation
```
You: "Create an architecture diagram for our microservices"
Claude: *generates image* "Saved to ./docs/architecture.jpg"
```

### Custom Size & Location
```
You: "Generate a high-res hero image and save it to ./public/hero.jpg"
Claude: *generates 2K image at specified path*
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Your Google Gemini API key |
| `IMAGE_SIZE` | No | `1K` | Default size (512, 1K, 2K or 4K) |
| `GEMINI_MODEL` | No | `gemini-3.1-flash-image` | Gemini model ID |

### Image Sizes

The resolution is for the default 1:1 aspect ratio. Prices are for `gemini-3.1-flash-image` (2026-09).

| Size | Resolution | Price per image | Best For |
|------|------------|-----------------|----------|
| `512` | 512x512 | $0.045 | Icons, thumbnails, quick previews |
| `1K` | 1024x1024 | $0.067 | General use, web images |
| `2K` | 2048x2048 | $0.101 | High-res, print, retina displays |
| `4K` | 4096x4096 | $0.151 | Very large prints and backgrounds |

## Manual Script Usage

```bash
# Basic usage
python scripts/generate_image.py "A serene lake at dawn"

# Custom output path
python scripts/generate_image.py "App icon" "./icon.jpg"

# With size and aspect ratio
python scripts/generate_image.py --size 2K --aspect 16:9 "Detailed landscape" "./wallpaper.jpg"

# With custom model
python scripts/generate_image.py --model gemini-3.1-flash-image "A logo" "./logo.jpg"
```

## File Structure

```
imagen/
├── SKILL.md               # Skill definition (Claude reads this)
├── README.md              # This file
├── reference.md           # Detailed API reference
├── examples.md            # Usage examples
├── .env.example           # API key template
└── scripts/
    └── generate_image.py  # Cross-platform Python script
```

## Requirements

- **Python 3.6+**: No additional packages needed (uses standard library only)
- **Gemini API Key**: From [Google AI Studio](https://aistudio.google.com/), with billing enabled

## Troubleshooting

### "GEMINI_API_KEY not set"

**Windows:**
```powershell
echo $env:GEMINI_API_KEY  # Should show your key
```

**macOS/Linux:**
```bash
echo $GEMINI_API_KEY  # Should show your key
source ~/.zshrc       # Reload if you just added it
```

### API Errors
- **400**: Check your prompt for special characters
- **429**: Rate limited or quota reached, wait a minute and retry
- **403**: Invalid API key, or billing is not set up

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" in the left sidebar
4. Create a new key or copy an existing one
5. Add it to your environment as shown above

## License

Apache-2.0 License - See [LICENSE](../../LICENSE) for details.
