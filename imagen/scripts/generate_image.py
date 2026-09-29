#!/usr/bin/env python3
"""
Imagen - Google Gemini Image Generation Script

Cross-platform image generation using the Gemini API (Interactions API).
Works on Windows, macOS, and Linux. Uses the standard library only.

Usage:
    python generate_image.py "prompt" [output_path] [--size 1K] [--aspect 16:9]

Environment variables:
    GEMINI_API_KEY (required) - Your Google Gemini API key
                                (on Windows, also read from the user environment in the registry)
    IMAGE_SIZE (optional) - Image size: "512", "1K" (default), "2K" or "4K"
    GEMINI_MODEL (optional) - Model ID (default: gemini-3.1-flash-image)

Output is always JPEG (the API rejects image/png). Image generation is billed; there is no free tier.
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Configuration
DEFAULT_MODEL_ID = "gemini-3.1-flash-image"
API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"
DEFAULT_IMAGE_SIZE = "1K"
# USD per image for gemini-3.1-flash-image (2026-09). Also the list of valid sizes
PRICE_PER_IMAGE = {"512": 0.045, "1K": 0.067, "2K": 0.101, "4K": 0.151}
DEFAULT_ASPECT = "1:1"
VALID_ASPECTS = ["1:1", "3:2", "2:3", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
JPEG_SUFFIXES = {".jpg", ".jpeg"}


def get_api_key() -> str:
    """Get the Gemini API key from the environment (or, on Windows, the user environment in the registry)."""
    api_key = os.environ.get("GEMINI_API_KEY")
    # A shell started before the variable was set (e.g. from an editor) may not see it
    if not api_key and sys.platform == "win32":
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as reg:
                api_key = winreg.QueryValueEx(reg, "GEMINI_API_KEY")[0]
        except OSError:
            pass
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        print("\nTo set it:", file=sys.stderr)
        print("  Windows (PowerShell): $env:GEMINI_API_KEY = 'your-key'", file=sys.stderr)
        print("  Windows (CMD): set GEMINI_API_KEY=your-key", file=sys.stderr)
        print("  macOS/Linux: export GEMINI_API_KEY='your-key'", file=sys.stderr)
        print("\nGet a key at: https://aistudio.google.com/ (image generation requires billing)", file=sys.stderr)
        sys.exit(1)
    return api_key


def validate_image_size(size: str) -> str:
    """Validate and return the image size."""
    if size not in PRICE_PER_IMAGE:
        print(f"Warning: Invalid IMAGE_SIZE '{size}'. Using default '{DEFAULT_IMAGE_SIZE}'", file=sys.stderr)
        return DEFAULT_IMAGE_SIZE
    return size


def jpeg_output_path(output_path: Path) -> Path:
    """The API only returns JPEG, so save under a .jpg name even if another extension was given."""
    if output_path.suffix.lower() in JPEG_SUFFIXES:
        return output_path
    jpeg_path = output_path.with_suffix(".jpg")
    print(f"Note: the API only returns JPEG, so the image is saved as {jpeg_path} (not {output_path})")
    return jpeg_path


def create_output_dir(output_path: Path) -> None:
    """Create output directory if it doesn't exist."""
    output_dir = output_path.parent
    if output_dir and not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)


def build_request_body(model_id: str, prompt: str, image_size: str, aspect: str) -> bytes:
    """Build the JSON request body for the Interactions API."""
    request_data = {
        "model": model_id,
        "input": [{"type": "text", "text": prompt}],
        "response_format": {
            "type": "image",
            "mime_type": "image/jpeg",
            "aspect_ratio": aspect,
            "image_size": image_size,
        },
    }
    return json.dumps(request_data).encode("utf-8")


def make_api_request(api_key: str, request_body: bytes) -> dict:
    """Make the API request and return the response."""
    # The key goes in a header, not the URL, so it doesn't end up in logs or error messages
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    req = urllib.request.Request(API_ENDPOINT, data=request_body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        error_detail = ""

        # Try to extract error message from response
        if error_body:
            try:
                error_json = json.loads(error_body)
                error_detail = error_json.get("error", {}).get("message", "")
            except json.JSONDecodeError:
                error_detail = error_body

        # Provide user-friendly messages for common errors
        if e.code == 429:
            print("=" * 60, file=sys.stderr)
            print("ERROR: Gemini API rate limit or quota reached", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            print("\nToo many requests, or your usage limit has been reached.", file=sys.stderr)
            print("\nWhat to do:", file=sys.stderr)
            print("  1. Wait a minute and try again (per-minute limits reset quickly)", file=sys.stderr)
            print("  2. Check your usage and billing at: https://aistudio.google.com/", file=sys.stderr)
            if error_detail:
                print(f"\nAPI message: {error_detail}", file=sys.stderr)
        elif e.code == 403:
            print("=" * 60, file=sys.stderr)
            print("ERROR: Gemini API access denied", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            print("\nYour API key is invalid or lacks required permissions.", file=sys.stderr)
            print("\nWhat to do:", file=sys.stderr)
            print("  1. Verify your API key at: https://aistudio.google.com/", file=sys.stderr)
            print("  2. Ensure the Gemini API is enabled for your project", file=sys.stderr)
            print("  3. Check that billing is set up (image generation has no free tier)", file=sys.stderr)
            if error_detail:
                print(f"\nAPI message: {error_detail}", file=sys.stderr)
        elif e.code == 400:
            print("=" * 60, file=sys.stderr)
            print("ERROR: Invalid request to Gemini API", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            print("\nThe request was rejected by the API.", file=sys.stderr)
            print("\nPossible causes:", file=sys.stderr)
            print("  - Prompt may contain blocked content", file=sys.stderr)
            print("  - The model ID, size or aspect ratio may not be supported", file=sys.stderr)
            print("  - Image generation may not be available for this prompt", file=sys.stderr)
            if error_detail:
                print(f"\nAPI message: {error_detail}", file=sys.stderr)
        elif e.code >= 500:
            print("=" * 60, file=sys.stderr)
            print("ERROR: Gemini API server error", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            print(f"\nThe Gemini API returned a server error (HTTP {e.code}).", file=sys.stderr)
            print("\nWhat to do:", file=sys.stderr)
            print("  1. Wait a few minutes and try again", file=sys.stderr)
            print("  2. Check Gemini API status if the issue persists", file=sys.stderr)
            if error_detail:
                print(f"\nAPI message: {error_detail}", file=sys.stderr)
        else:
            print(f"Error: API request failed with HTTP status {e.code}", file=sys.stderr)
            if error_detail:
                print(f"API message: {error_detail}", file=sys.stderr)
            elif error_body:
                print(f"Response: {error_body}", file=sys.stderr)

        sys.exit(1)
    except urllib.error.URLError as e:
        print("=" * 60, file=sys.stderr)
        print("ERROR: Failed to connect to Gemini API", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print(f"\nConnection error: {e.reason}", file=sys.stderr)
        print("\nWhat to do:", file=sys.stderr)
        print("  1. Check your internet connection", file=sys.stderr)
        print("  2. Verify the API endpoint is accessible", file=sys.stderr)
        print("  3. Check if a firewall or proxy is blocking the request", file=sys.stderr)
        sys.exit(1)


def extract_image_data(response: dict) -> str:
    """Extract base64 image data from the API response (the first image in steps[].content[])."""
    for step in response.get("steps", []):
        # Skip steps without content (e.g. the model's thoughts)
        for part in step.get("content") or []:
            if part.get("type") == "image" and part.get("data"):
                return part["data"]

    print("Error: No image data found in the response (the prompt may have been refused)", file=sys.stderr)
    print(f"Response: {json.dumps(response, ensure_ascii=False)[:2000]}", file=sys.stderr)
    sys.exit(1)


def save_image(image_data: str, output_path: Path) -> None:
    """Decode and save the base64 image data."""
    try:
        image_bytes = base64.b64decode(image_data)
        output_path.write_bytes(image_bytes)
    # ValueError: broken base64 data (binascii.Error), OSError: the file could not be written
    except (ValueError, OSError) as e:
        print(f"Error: Failed to save image: {e}", file=sys.stderr)
        sys.exit(1)


def get_file_size(path: Path) -> str:
    """Get human-readable file size."""
    size = path.stat().st_size
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Google Gemini AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_image.py "A sunset over mountains"
  python generate_image.py "An app icon" ./icons/app.jpg
  python generate_image.py --size 2K --aspect 16:9 "High-res landscape" ./wallpaper.jpg
  python generate_image.py --model gemini-3.1-flash-image "A logo" ./logo.jpg

Environment Variables:
  GEMINI_API_KEY    Your Google Gemini API key (required)
  IMAGE_SIZE        Image size: 512, 1K (default), 2K or 4K
  GEMINI_MODEL      Model ID for image generation

Output is always JPEG. Image generation is billed (no free tier).
        """
    )
    parser.add_argument("prompt", help="Text description of the image to generate")
    parser.add_argument("output", nargs="?", default="./generated-image.jpg",
                        help="Output file path (default: ./generated-image.jpg; saved as .jpg)")
    parser.add_argument("--size", choices=list(PRICE_PER_IMAGE),
                        help="Image size (overrides IMAGE_SIZE env var)")
    parser.add_argument("--aspect", choices=VALID_ASPECTS, default=DEFAULT_ASPECT,
                        help=f"Aspect ratio (default: {DEFAULT_ASPECT})")
    parser.add_argument("--model", "-m",
                        help=f"Gemini model ID (default: {DEFAULT_MODEL_ID})")

    args = parser.parse_args()

    # Get configuration
    api_key = get_api_key()
    model_id = args.model or os.environ.get("GEMINI_MODEL", DEFAULT_MODEL_ID)
    image_size = args.size or os.environ.get("IMAGE_SIZE", DEFAULT_IMAGE_SIZE)
    image_size = validate_image_size(image_size)
    output_path = jpeg_output_path(Path(args.output))

    # Create output directory
    create_output_dir(output_path)

    # Display info
    print(f"Generating image with prompt: \"{args.prompt}\"")
    print(f"Model: {model_id}")
    print(f"Image size: {image_size}, aspect ratio: {args.aspect}")
    print(f"Estimated cost: about ${PRICE_PER_IMAGE[image_size]:.3f} (price of {DEFAULT_MODEL_ID}, 2026-09)")
    print(f"Output path: {output_path}")
    print()

    # Build and send request
    request_body = build_request_body(model_id, args.prompt, image_size, args.aspect)
    response = make_api_request(api_key, request_body)

    # Extract and save image
    image_data = extract_image_data(response)
    save_image(image_data, output_path)

    # Verify and report success
    if output_path.exists() and output_path.stat().st_size > 0:
        file_size = get_file_size(output_path)
        print("Success! Image generated and saved.")
        print(f"File: {output_path}")
        print(f"Size: {file_size}")
    else:
        print(f"Error: Failed to save image to {output_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
