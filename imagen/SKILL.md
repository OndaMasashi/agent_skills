---
name: imagen
description: |
  Generate images using Google Gemini's image generation capabilities. Use this skill when the user needs to create, generate, or produce images for any purpose including UI mockups, icons, illustrations, diagrams, concept art, placeholder images, or visual representations. 日本語トリガー例: 画像を生成して/画像を作って/アイコンを作って/イラストを生成/画像生成/挿絵がほしい/ヒーロー画像を作って。構造化・クリック可能なアーキテクチャ図やフロー図・シーケンス図には使わない（architecture-diagramまたはmermaid-diagramを使用）。デザイン哲学に基づくポスターやPDF/PNGアート作品にはcanvas-designを使用。
---

# Imagen - AI Image Generation Skill

## Overview

This skill generates images using Google Gemini's image generation model (`gemini-3.1-flash-image`, called through the Gemini Interactions API). It enables seamless image creation during any Claude Code session - whether you're building frontend UIs, creating documentation, or need visual representations of concepts.

**Cross-Platform**: Works on Windows, macOS, and Linux.

## When to Use This Skill

Use this skill when:

- User requests image generation (e.g., "generate an image of...", "create a picture...")
- Frontend development requires placeholder or actual images
- Documentation needs illustrations
- Visualizing concepts or ideas as a picture (architecture, flow, and sequence diagrams go to architecture-diagram or mermaid-diagram)
- Creating icons, logos, or UI assets

## How It Works

1. Takes a text prompt describing the desired image
2. Calls the Gemini Interactions API with the size and aspect ratio
3. Saves the generated JPEG to a specified location (defaults to current directory)
4. Returns the file path for use in your project

## Usage

### Python (Cross-Platform - Recommended)

```bash
# Basic usage
python scripts/generate_image.py "A futuristic city skyline at sunset"

# With custom output path
python scripts/generate_image.py "A minimalist app icon for a music player" "./assets/icons/music-icon.jpg"

# With custom size and aspect ratio (sizes: 512, 1K, 2K, 4K; aspect default 1:1)
python scripts/generate_image.py --size 2K --aspect 16:9 "High resolution landscape" "./wallpaper.jpg"
```

## Requirements

- `GEMINI_API_KEY` environment variable must be set (on Windows it is also read from the user environment in the registry)
- Billing must be enabled for the key: image generation has no free tier. Cost per image (2026-09): 512 is 0.045 USD, 1K is 0.067 USD, 2K is 0.101 USD, 4K is 0.151 USD. Tell the user the cost before generating many images
- Python 3.6+ (uses standard library only, no pip install needed)

## Output

Generated images are saved as JPEG files (the API does not return PNG, and there is no transparency). If the output path has another extension, the script saves it as `.jpg` instead and says so. The script returns:

- Success: Path to the generated image
- Failure: Error message with details

## Examples

### Frontend Development

```
User: "I need a hero image for my landing page - something abstract and tech-focused"
-> Generates and saves image, provides path for use in HTML/CSS
```

### Documentation

```
User: "Create a header illustration for the README - an abstract image of data flowing between clouds"
-> Generates the illustration, ready for README or docs
```

### UI Assets

```
User: "Generate a placeholder avatar image for the user profile component"
-> Creates image in appropriate size for component use
```
