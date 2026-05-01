"""Shared helpers for the RootFlowAI gpt-image-2 scripts.

Adapted from RyanWeb31110/rootflowai-image (MIT-style permissive use)
with minor changes:
- single skill folder layout (scripts/ alongside SKILL.md)
- merged metered + count profiles into one entry point
- only Python standard library
"""

from __future__ import annotations

import base64
import ipaddress
import json
import mimetypes
import os
import socket
import sys
import uuid
from pathlib import Path
from typing import Any
from urllib import error, parse, request

DEFAULT_BASE_URL = "https://api.rootflowai.com/v1"

# Models
MODEL_METERED = "gpt-image-2"
MODEL_COUNT_1K = "gpt-image-2-count"
MODEL_COUNT_2K = "gpt-image-2-hd-count"
MODEL_COUNT_4K = "gpt-image-2-4k-count"
DEFAULT_MODEL = MODEL_METERED

# Defaults
DEFAULT_SIZE = "1:1"
DEFAULT_QUALITY = "high"
SUPPORTED_QUALITIES = ("low", "medium", "high")

# Profiles
PROFILE_AUTO = "auto"
PROFILE_METERED = "metered"
PROFILE_COUNT = "count"
SUPPORTED_PROFILES = (PROFILE_AUTO, PROFILE_METERED, PROFILE_COUNT)

PROFILE_MODEL_DEFAULTS = {
    PROFILE_METERED: MODEL_METERED,
    PROFILE_COUNT: MODEL_COUNT_1K,
}

MODEL_PROFILE_MAP = {
    MODEL_METERED: PROFILE_METERED,
    MODEL_COUNT_1K: PROFILE_COUNT,
    MODEL_COUNT_2K: PROFILE_COUNT,
    MODEL_COUNT_4K: PROFILE_COUNT,
}

PROFILE_ENV_VARS = {
    PROFILE_METERED: ("ROOTFLOWAI_METERED_API_KEY", "ROOTFLOWAI_API_KEY"),
    PROFILE_COUNT: ("ROOTFLOWAI_COUNT_API_KEY", "ROOTFLOWAI_API_KEY"),
}

# Allowed sizes
RATIO_SIZES = (
    "1:1", "3:2", "2:3", "4:3", "3:4", "5:4", "4:5",
    "16:9", "9:16", "2:1", "1:2", "21:9", "9:21",
)
RATIO_4K_ALLOWED = ("16:9", "9:16", "2:1", "1:2", "21:9", "9:21")
PIXEL_SIZE_RATIO_MAP = {
    "1024x1024": "1:1",
    "1536x1024": "3:2",
    "1024x1536": "2:3",
    "1792x1024": "16:9",
    "1024x1792": "9:16",
}

ALLOWED_REMOTE_IMAGE_SCHEME = "https"
BLOCKED_HOSTNAMES = {"localhost", "localhost.localdomain"}

# Hostnames that we consider trusted output channels for the API (the service's
# own CDN). DNS-resolution checks are skipped for these so that local proxies /
# fake-IP DNS pools (e.g. 198.18.0.0/15) do not block legitimate downloads.
TRUSTED_DOWNLOAD_HOST_SUFFIXES = (
    ".rootflowai.com",
    "rootflowai.com",
)


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def _extract_ip_from_sockaddr(sockaddr: tuple) -> str:
    if not sockaddr:
        raise ValueError("Resolver returned an empty socket address.")
    return str(sockaddr[0])


def _hostname_is_trusted(hostname: str) -> bool:
    h = hostname.rstrip(".").lower()
    return any(h == suf.lstrip(".") or h.endswith(suf) for suf in TRUSTED_DOWNLOAD_HOST_SUFFIXES)


def validate_remote_image_url(url: str, resolver: Any | None = None,
                              skip_dns_check: bool = False) -> None:
    """Validate a URL provided by the *user* as a reference image.

    Strict by default: HTTPS-only, no localhost, no private/non-global IPs
    (SSRF guard). When ``skip_dns_check=True`` only the protocol + host
    blocklist is enforced — used for trusted download URLs returned by the
    API itself.
    """
    parsed = parse.urlparse(url)
    if parsed.scheme.lower() != ALLOWED_REMOTE_IMAGE_SCHEME:
        raise ValueError("Only HTTPS image URLs are allowed.")
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Remote image URL must include a hostname.")
    if hostname.rstrip(".").lower() in BLOCKED_HOSTNAMES:
        raise ValueError("Localhost image URLs are not allowed.")
    if skip_dns_check:
        return
    port = parsed.port or 443
    resolve = resolver or socket.getaddrinfo
    try:
        infos = resolve(hostname, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"Could not resolve remote image hostname: {hostname}") from exc
    if not infos:
        raise ValueError(f"Remote image hostname did not resolve: {hostname}")
    for info in infos:
        ip_text = _extract_ip_from_sockaddr(info[4])
        ip_obj = ipaddress.ip_address(ip_text)
        if not ip_obj.is_global:
            raise ValueError(f"Remote image URL resolved to a non-public address: {ip_text}")


class SafeImageRedirectHandler(request.HTTPRedirectHandler):
    def __init__(self, skip_dns_check: bool = False) -> None:
        super().__init__()
        self._skip_dns_check = skip_dns_check

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_remote_image_url(newurl, skip_dns_check=self._skip_dns_check)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def encode_local_image_as_data_uri(path: Path) -> str:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"Image file not found: {path}")
    data = path.read_bytes()
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def infer_extension(data: bytes, content_type: str | None = None, source_url: str | None = None) -> str:
    if content_type:
        ct = content_type.lower()
        if "png" in ct:
            return ".png"
        if "jpeg" in ct or "jpg" in ct:
            return ".jpg"
        if "webp" in ct:
            return ".webp"
        if "gif" in ct:
            return ".gif"
        if "bmp" in ct:
            return ".bmp"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return ".gif"
    if data.startswith(b"BM"):
        return ".bmp"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp"
    if source_url:
        suffix = Path(parse.urlparse(source_url).path).suffix.lower()
        if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}:
            return ".jpg" if suffix == ".jpeg" else suffix
    return ".bin"


def fetch_url(url: str, timeout: float, trusted: bool = False) -> tuple[bytes, str | None]:
    """Download a remote image.

    ``trusted=True`` is for URLs returned by the API itself (CDN). It skips
    the SSRF DNS-resolution check so that local DNS proxies / fake-IP pools
    do not block legitimate downloads, while still enforcing HTTPS-only
    and the localhost blocklist. It also routes through any configured
    HTTP(S) proxy (``HTTPS_PROXY`` / ``HTTP_PROXY``).
    """
    validate_remote_image_url(url, skip_dns_check=trusted)
    req = request.Request(url, method="GET",
                          headers={"User-Agent": "rootflowai-image-skill/1.0"})
    handlers = [SafeImageRedirectHandler(skip_dns_check=trusted)]
    if trusted:
        # Honor system proxy env vars (HTTPS_PROXY / HTTP_PROXY / NO_PROXY)
        # so that downloads work behind local fake-IP DNS proxies.
        handlers.append(request.ProxyHandler())
    opener = request.build_opener(*handlers)
    with opener.open(req, timeout=timeout) as resp:
        data = resp.read()
        return data, resp.headers.get_content_type()


def load_image_bytes(item: dict, timeout: float) -> tuple[bytes, str | None, str | None]:
    for key in ("b64_json", "image_base64", "base64", "b64"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return base64.b64decode(value), None, None
    for key in ("url", "image_url"):
        value = item.get(key)
        if isinstance(value, str) and value:
            parsed_host = parse.urlparse(value).hostname or ""
            trusted = _hostname_is_trusted(parsed_host)
            data, content_type = fetch_url(value, timeout, trusted=trusted)
            return data, content_type, value
    raise ValueError("Response item does not contain a supported image field.")


def save_raw_response(response_path: str, payload: dict) -> str:
    path = Path(response_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return str(path)


def parse_json_response(raw: str) -> dict:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": "API returned a non-JSON response.", "response": raw},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1) from exc
    if not isinstance(data, dict):
        print(json.dumps({"error": "API returned an unexpected JSON shape.", "response": data},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1)
    return data


def perform_request(req: request.Request, timeout: float, error_label: str) -> dict:
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(json.dumps({"error": error_label, "status": exc.code, "response": body},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1) from exc
    except error.URLError as exc:
        print(json.dumps({"error": "Could not reach the RootFlowAI API.", "reason": str(exc.reason)},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1) from exc
    return parse_json_response(raw)


def post_json_request(endpoint: str, api_key: str, base_url: str, payload: dict,
                      timeout: float, error_label: str) -> dict:
    url = f"{normalize_base_url(base_url)}{endpoint}"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    req = request.Request(url, data=body, headers=headers, method="POST")
    return perform_request(req, timeout, error_label)


def encode_multipart_form_data(fields: list[tuple[str, str]],
                               files: list[tuple[str, Path]]) -> tuple[bytes, str]:
    boundary = f"----rootflowaiimage{uuid.uuid4().hex}"
    body = bytearray()
    for name, value in fields:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.extend(value.encode("utf-8"))
        body.extend(b"\r\n")
    for field_name, file_path in files:
        file_bytes = file_path.read_bytes()
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            (f'Content-Disposition: form-data; name="{field_name}"; '
             f'filename="{file_path.name}"\r\n').encode("utf-8")
        )
        body.extend(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
        body.extend(file_bytes)
        body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    return bytes(body), f"multipart/form-data; boundary={boundary}"


def post_multipart_request(endpoint: str, api_key: str, base_url: str,
                           fields: list[tuple[str, str]], files: list[tuple[str, Path]],
                           timeout: float, error_label: str) -> dict:
    url = f"{normalize_base_url(base_url)}{endpoint}"
    body, content_type = encode_multipart_form_data(fields, files)
    headers = {"Authorization": f"Bearer {api_key}",
               "Content-Type": content_type,
               "Content-Length": str(len(body))}
    req = request.Request(url, data=body, headers=headers, method="POST")
    return perform_request(req, timeout, error_label)


def save_response_images(response_payload: dict, output_dir: str, prefix: str,
                         timeout: float, response_path: str | None = None
                         ) -> tuple[list[str], list[int], str | None]:
    output_path = Path(output_dir).expanduser().resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    raw_response_path = save_raw_response(response_path, response_payload) if response_path else None
    items = response_payload.get("data")
    if not isinstance(items, list) or not items:
        print(json.dumps({"error": "API response does not contain a non-empty data array.",
                          "response_path": raw_response_path, "response": response_payload},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1)
    saved_paths: list[str] = []
    skipped_items: list[dict] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            skipped_items.append({"index": index, "reason": "not an object"})
            continue
        try:
            image_bytes, content_type, source_url = load_image_bytes(item, timeout)
        except Exception as exc:  # noqa: BLE001 — surface the real cause
            skipped_items.append({"index": index, "reason": f"{type(exc).__name__}: {exc}"})
            continue
        ext = infer_extension(image_bytes, content_type=content_type, source_url=source_url)
        file_path = output_path / f"{prefix}-{index:02d}{ext}"
        file_path.write_bytes(image_bytes)
        saved_paths.append(str(file_path))
    if not saved_paths:
        print(json.dumps({"error": "API responded, but no image files could be extracted.",
                          "response_path": raw_response_path, "skipped_items": skipped_items,
                          "response": response_payload},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1)
    return saved_paths, skipped_items, raw_response_path


def add_profile_arguments(parser) -> None:
    parser.add_argument(
        "--profile",
        choices=SUPPORTED_PROFILES,
        default=PROFILE_AUTO,
        help=("Credential profile. auto: pick by --model. "
              "metered: usage-based gpt-image-2 lane. "
              "count: per-image gpt-image-2-count lane."),
    )


def resolve_profile(profile: str, model: str | None) -> str:
    if profile != PROFILE_AUTO:
        return profile
    if model and model in MODEL_PROFILE_MAP:
        return MODEL_PROFILE_MAP[model]
    return PROFILE_METERED


def resolve_model(profile: str, model: str | None) -> str:
    if model:
        return model
    if profile == PROFILE_AUTO:
        return DEFAULT_MODEL
    return PROFILE_MODEL_DEFAULTS.get(profile, DEFAULT_MODEL)


def get_api_key(explicit_api_key: str | None, profile: str = PROFILE_AUTO,
                model: str | None = None) -> tuple[str, str, str]:
    resolved_profile = resolve_profile(profile, model)
    if explicit_api_key:
        return explicit_api_key, resolved_profile, "--api-key"
    env_names = PROFILE_ENV_VARS.get(resolved_profile, ())
    for env_name in env_names:
        value = os.environ.get(env_name)
        if value:
            return value, resolved_profile, env_name
    if resolved_profile == PROFILE_METERED:
        raise SystemExit("Missing API key for the metered profile. "
                         "Set ROOTFLOWAI_METERED_API_KEY or ROOTFLOWAI_API_KEY, or use --api-key.")
    if resolved_profile == PROFILE_COUNT:
        raise SystemExit("Missing API key for the count profile. "
                         "Set ROOTFLOWAI_COUNT_API_KEY or ROOTFLOWAI_API_KEY, or use --api-key.")
    raise SystemExit("Missing API key. Use --api-key or configure the appropriate profile env var.")


def validate_size_for_model(size: str, model: str) -> None:
    """4K only supports a subset of ratios; 1K/2K support all 13 ratios."""
    if model != MODEL_COUNT_4K:
        return
    ratio = PIXEL_SIZE_RATIO_MAP.get(size, size)
    if ratio in RATIO_SIZES and ratio not in RATIO_4K_ALLOWED:
        raise SystemExit(
            f"Error: model {model} only supports ratios {list(RATIO_4K_ALLOWED)}, "
            f"but got '{size}' (equivalent ratio: {ratio}). "
            "Switch to 2K (gpt-image-2-hd-count) or use a supported ratio."
        )
