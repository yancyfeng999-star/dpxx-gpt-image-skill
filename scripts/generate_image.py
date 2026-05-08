#!/usr/bin/env python3
"""Generate GPT images via RootFlowAI (text-to-image / image-to-image)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Allow running both as `python3 generate_image.py` and via skill path.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from image_api_common import (  # noqa: E402
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_QUALITY,
    DEFAULT_SIZE,
    SUPPORTED_QUALITIES,
    add_profile_arguments,
    encode_local_image_as_data_uri,
    get_api_key,
    model_supports_quality,
    post_json_request,
    resolve_model,
    save_response_images,
    validate_remote_image_url,
    validate_size_for_model,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate images with RootFlowAI GPT-Image-2 models.")
    parser.add_argument("--prompt", required=True,
                        help="Text prompt for image generation.")
    parser.add_argument("--image", action="append",
                        help="Reference image (https URL or local path). Repeat up to 16 times for image-to-image.")
    parser.add_argument("--api-key",
                        help="Bearer token; overrides env-based profile resolution.")
    parser.add_argument("--base-url",
                        default=os.environ.get("ROOTFLOWAI_BASE_URL", DEFAULT_BASE_URL),
                        help="RootFlowAI API base URL.")
    parser.add_argument("--model",
                        help=("Model name. GPT: gpt-image-2-count (1K) / "
                              "gpt-image-2-hd-count (2K) / gpt-image-2-4k-count (4K). "
                              f"Defaults to {DEFAULT_MODEL}."))
    add_profile_arguments(parser)
    parser.add_argument("--size", default=DEFAULT_SIZE,
                        help=("Output size. Ratio: 1:1/3:2/2:3/4:3/3:4/5:4/4:5/16:9/9:16/2:1/1:2/21:9/9:21. "
                              "Pixels (e.g. 1024x1024) also accepted."))
    parser.add_argument("--quality", default=DEFAULT_QUALITY,
                        choices=SUPPORTED_QUALITIES,
                        help="GPT-Image-2 quality. Defaults to high.")
    parser.add_argument("--n", type=int, default=1, help="Number of images to request.")
    parser.add_argument("--output-dir", default="rootflowai-images",
                        help="Directory where generated images will be saved.")
    parser.add_argument("--prefix", default="image",
                        help="Filename prefix used for saved images.")
    parser.add_argument("--response-path",
                        help="Optional path where the raw JSON response will be saved.")
    parser.add_argument("--timeout", type=float, default=900.0,
                        help="HTTP timeout in seconds.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    effective_model = resolve_model(args.profile, args.model)

    try:
        api_key, resolved_profile, api_key_source = get_api_key(
            args.api_key, profile=args.profile, model=effective_model)
    except SystemExit as exc:
        parser.error(str(exc))

    if args.n < 1:
        parser.error("--n must be at least 1.")

    validate_size_for_model(args.size, effective_model)

    request_payload = {
        "model": effective_model,
        "prompt": args.prompt,
        "size": args.size,
        "n": args.n,
    }
    if model_supports_quality(effective_model):
        request_payload["quality"] = args.quality

    if args.image:
        if len(args.image) > 16:
            parser.error("At most 16 reference images are supported (--image).")
        image_list = []
        for img in args.image:
            if img.startswith("https://"):
                validate_remote_image_url(img)
                image_list.append(img)
            elif img.startswith("http://"):
                parser.error("Only HTTPS image URLs are accepted.")
            else:
                image_list.append(encode_local_image_as_data_uri(Path(img)))
        request_payload["image"] = image_list

    response_payload = post_json_request(
        endpoint="/images/generations",
        api_key=api_key,
        base_url=args.base_url,
        payload=request_payload,
        timeout=args.timeout,
        error_label="Image generation request failed.",
    )

    saved_paths, skipped_items, raw_response_path = save_response_images(
        response_payload=response_payload,
        output_dir=args.output_dir,
        prefix=args.prefix,
        timeout=args.timeout,
        response_path=args.response_path,
    )

    print(json.dumps({
        "saved": saved_paths,
        "skipped_items": skipped_items,
        "response_path": raw_response_path,
        "model": effective_model,
        "profile_requested": args.profile,
        "profile_resolved": resolved_profile,
        "api_key_source": api_key_source,
        "size": args.size,
        "quality": args.quality,
        "n_requested": args.n,
        "n_saved": len(saved_paths),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
