# app/services/image_agent/image_agent.py

from __future__ import annotations

import json
import logging
import os
import time
import uuid
import urllib.parse
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

from app.core.config import settings

# ── Config ────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

GROQ_API_KEY           = settings.GROQ_API_KEY
GROQ_MODEL             = settings.GROQ_MODEL
GROQ_API_URL           = "https://api.groq.com/openai/v1/chat/completions"
RUNWAY_API_KEY         = settings.RUNWAY_API_KEY
RUNWAY_IMAGE_MODEL     = settings.RUNWAY_IMAGE_MODEL
RUNWAY_BASE_URL        = "https://api.dev.runwayml.com/v1"
RUNWAY_API_VERSION     = "2024-11-06"
POLLINATIONS_API_KEY   = settings.POLLINATIONS_API_KEY
POLLINATIONS_MODEL     = settings.POLLINATIONS_MODEL
POLLINATIONS_IMAGE_URL = "https://gen.pollinations.ai/image/"
IMAGE_BACKEND          = (settings.IMAGE_BACKEND or "auto").strip().lower()

OUTPUT_DIR = Path("uploads/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

_SIZE_TO_RUNWAY_RATIO = {
    "512x512": "1024:1024",
    "768x768": "1024:1024",
    "1024x1024": "1024:1024",
}


class ImageGenerationError(Exception):
    """Raised when the image backend cannot produce an image."""


# ── Enums ─────────────────────────────────────────────────────

class AdPlatform(str, Enum):
    INSTAGRAM = "instagram"
    FACEBOOK  = "facebook"
    TIKTOK    = "tiktok"
    LINKEDIN  = "linkedin"
    GENERAL   = "general"


class ImageSize(str, Enum):
    SQUARE = "512x512"
    MEDIUM = "768x768"
    HD     = "1024x1024"


class LogoPosition(str, Enum):
    BOTTOM_RIGHT = "bottom_right"
    BOTTOM_LEFT  = "bottom_left"
    TOP_RIGHT    = "top_right"
    TOP_LEFT     = "top_left"


# ── Dataclasses ───────────────────────────────────────────────

@dataclass
class LogoConfig:
    enabled:    bool        = False
    text:       str         = ""
    bg_color:   str         = ""
    text_color: str         = "#FFFFFF"
    position:   LogoPosition = LogoPosition.BOTTOM_RIGHT
    size_ratio: float       = 0.20
    opacity:    int         = 220
    shape:      str         = "circle"


@dataclass
class BrandProfile:
    brand_name:       str
    industry:         str
    target_audience:  str
    brand_voice:      str
    primary_colors:   list
    style_keywords:   list
    extra_guidelines: str = ""


@dataclass
class ImageRequest:
    brand:          BrandProfile
    campaign_goal:  str
    platform:       AdPlatform = AdPlatform.INSTAGRAM
    image_size:     ImageSize  = ImageSize.SQUARE
    num_variations: int        = 1
    ad_copy:        str        = ""
    logo:           LogoConfig = field(default_factory=LogoConfig)
    request_id:     str        = field(default_factory=lambda: str(uuid.uuid4())[:8])


@dataclass
class GeneratedImage:
    image_id:     str
    request_id:   str
    local_path:   str
    prompt_used:  str
    ad_copy:      str
    platform:     str
    size:         str
    model_used:   str
    logo_applied: bool = False
    metadata:     dict = field(default_factory=dict)


@dataclass
class ImageGenerationResult:
    request_id:          str
    brand_name:          str
    campaign_goal:       str
    images:              list
    ab_test_ready:       bool
    generation_time_sec: float
    knowledge_context:   str

    def to_dict(self):
        return asdict(self)


# ── Knowledge Base ────────────────────────────────────────────

class ImageKnowledgeBase:

    PLATFORM_RULES = {
        "instagram": (
            "Instagram ads: use bright vibrant colors, high contrast. "
            "Keep composition clean with single focal point. "
            "Lifestyle imagery with natural lighting works best."
        ),
        "facebook": (
            "Facebook ads: clear value proposition visually. "
            "Before/after imagery converts well. "
            "Faces increase engagement. Landscape format preferred."
        ),
        "tiktok": (
            "TikTok visuals: energetic, bold, Gen-Z aesthetic. "
            "Neon or electric color palettes. "
            "Trendy, authentic style — avoid corporate look."
        ),
        "linkedin": (
            "LinkedIn: professional clean imagery. Navy/grey/white palette. "
            "Minimal design, strong typography, trustworthy feel."
        ),
    }

    INDUSTRY_TIPS = {
        "beauty":  "Soft studio lighting, pastel tones, dewy skin textures, minimalist props.",
        "food":    "Warm lighting, overhead angle, fresh vibrant colors, steam effects.",
        "tech":    "Dark background with glowing UI, gradient blues and purples, geometric shapes.",
        "fashion": "Editorial lighting, model photography, bold colors, luxury aesthetic.",
        "fitness": "High energy, action shots, bold contrast, motivational imagery.",
        "default": "Clean composition, brand colors dominant, single focal point, professional lighting.",
    }

    def get_context(self, platform: str, industry: str) -> str:
        rule = self.PLATFORM_RULES.get(platform.lower(), self.PLATFORM_RULES["instagram"])
        key  = next((k for k in self.INDUSTRY_TIPS if k in industry.lower()), "default")
        return f"Platform rules: {rule}\nIndustry tips: {self.INDUSTRY_TIPS[key]}"


# ── LLM ───────────────────────────────────────────────────────

class GroqLLM:

    def __init__(self):
        self.available = bool(settings.GROQ_API_KEY)

    def call(self, system: str, user: str) -> str:
        if not self.available:
            return ""
        try:
            resp = requests.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model":       GROQ_MODEL,
                    "messages":    [
                        {"role": "system", "content": system},
                        {"role": "user",   "content": user},
                    ],
                    "temperature": 0.7,
                    "max_tokens":  400,
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            print(f"[GroqLLM] Error: {exc}")
            return ""


# ── Prompt Builder ────────────────────────────────────────────

class ImagePromptBuilder:

    VOICE_MAP = {
        "playful":      "vibrant, fun, energetic atmosphere",
        "professional": "clean, corporate, trustworthy composition",
        "bold":         "high contrast, dramatic lighting, strong visual impact",
        "warm":         "soft warm lighting, inviting, cosy feel",
        "luxury":       "premium, elegant, sophisticated, high-end aesthetic",
        "natural":      "organic, earthy, authentic, lifestyle photography",
    }
    PLATFORM_STYLE = {
        "instagram": "instagram-worthy, aesthetic, lifestyle",
        "facebook":  "clear, engaging, story-driven",
        "tiktok":    "bold, trendy, Gen-Z aesthetic, high energy",
        "linkedin":  "professional, clean, corporate",
    }
    VARIATION_MODS  = ["", ", warm golden tones", ", minimalist negative space", ", featuring people"]
    VARIATION_HINTS = {
        0: "primary creative — follow brand guidelines closely",
        1: "alternative warm golden color mood",
        2: "minimalist negative-space approach",
        3: "lifestyle people-centric scene",
    }

    def __init__(self, llm: GroqLLM):
        self.llm = llm

    def build_image_prompt(self, request: ImageRequest, context: str, variation_index: int = 0) -> str:
        hint = self.VARIATION_HINTS.get(variation_index, f"creative variation #{variation_index + 1}")
        if self.llm.available:
            result = self.llm.call(
                "You are an expert AI art director. Write a precise Stable Diffusion prompt "
                "for a professional marketing image. Output ONLY the prompt text. "
                "Include: subject, lighting, colors, style, mood, composition. Max 75 words.",
                f"Brand: {request.brand.brand_name} | Industry: {request.brand.industry}\n"
                f"Audience: {request.brand.target_audience}\n"
                f"Voice: {request.brand.brand_voice}\n"
                f"Colors: {', '.join(request.brand.primary_colors)}\n"
                f"Style: {', '.join(request.brand.style_keywords)}\n"
                f"Goal: {request.campaign_goal}\n"
                f"Platform: {request.platform.value}\n"
                f"Variation: {hint}\n"
                f"Context: {context}",
            )
            if result:
                return result
        return self._rule_based(request, variation_index)

    def _rule_based(self, request: ImageRequest, variation_index: int) -> str:
        colors = ", ".join(request.brand.primary_colors[:2])
        styles = ", ".join(request.brand.style_keywords[:3])
        mood   = self.VOICE_MAP.get(request.brand.brand_voice.lower(), "professional, clean")
        plat   = self.PLATFORM_STYLE.get(request.platform.value, "clean, professional")
        mod    = self.VARIATION_MODS[variation_index % len(self.VARIATION_MODS)]
        return (
            f"{request.brand.industry} advertisement, {request.campaign_goal}, "
            f"{mood}, color palette {colors}, {styles} style, "
            f"{plat}{mod}, professional photography, studio lighting, 8k sharp"
        )

    def build_ad_copy(self, request: ImageRequest) -> str:
        if request.ad_copy:
            return request.ad_copy
        if self.llm.available:
            result = self.llm.call(
                "Write punchy ad copy. Max 10 words. Output ONLY the copy text.",
                f"Brand: {request.brand.brand_name} | Goal: {request.campaign_goal} | Voice: {request.brand.brand_voice}",
            )
            if result:
                return result.strip('"').strip("'")
        return f"{request.brand.brand_name} — {request.campaign_goal[:40]}"


# ── Logo Overlay ──────────────────────────────────────────────

class LogoOverlay:

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple:
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def _get_initials(brand_name: str) -> str:
        words = brand_name.strip().split()
        if len(words) >= 2:
            return (words[0][0] + words[1][0]).upper()
        return brand_name[:2].upper()

    @staticmethod
    def _load_font(size: int):
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        ]
        for path in font_paths:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    def apply(self, image_path: str, cfg: LogoConfig, brand: BrandProfile) -> str:
        if not cfg.enabled:
            return image_path
        img = Image.open(image_path).convert("RGBA")
        W, H = img.size
        text    = cfg.text if cfg.text else self._get_initials(brand.brand_name)
        colors = brand.primary_colors or ["#2563EB"]
        bg_hex  = cfg.bg_color if cfg.bg_color else colors[0]
        bg_rgb  = self._hex_to_rgb(bg_hex)
        txt_rgb = self._hex_to_rgb(cfg.text_color.lstrip("#"))
        size    = int(min(W, H) * cfg.size_ratio)
        margin  = int(min(W, H) * 0.04)
        badge   = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw    = ImageDraw.Draw(badge)
        pad     = 3
        if cfg.shape == "circle":
            draw.ellipse([pad, pad, size - pad, size - pad], fill=(*bg_rgb, cfg.opacity))
        else:
            draw.rounded_rectangle([pad, pad, size - pad, size - pad], radius=size // 5, fill=(*bg_rgb, cfg.opacity))
        font   = self._load_font(size // 2)
        bbox   = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size - tw) // 2, (size - th) // 2 - 2), text, fill=(*txt_rgb, 255), font=font)
        positions = {
            "bottom_right": (W - size - margin, H - size - margin),
            "bottom_left":  (margin, H - size - margin),
            "top_right":    (W - size - margin, margin),
            "top_left":     (margin, margin),
        }
        img.paste(badge, positions.get(cfg.position.value, positions["bottom_right"]), badge)
        img.convert("RGB").save(image_path)
        return image_path


# ── Image Generator ───────────────────────────────────────────

def _resolve_image_backend() -> str:
    if IMAGE_BACKEND in ("runway", "pollinations"):
        return IMAGE_BACKEND
    if RUNWAY_API_KEY:
        return "runway"
    if POLLINATIONS_API_KEY:
        return "pollinations"
    return "local-fallback"


class RunwayImageGenerator:

    REQUEST_TIMEOUT = 60
    POLL_TIMEOUT_S  = 180
    PROMPT_MAX_CHARS = 1000

    def generate_and_save(self, prompt: str, image_id: str, size: ImageSize) -> tuple:
        if not RUNWAY_API_KEY:
            raise ImageGenerationError(
                "Runway API key is not configured. Set RUNWAY_API_KEY in .env."
            )

        prompt_text = " ".join((prompt or "").split())
        if not prompt_text:
            raise ImageGenerationError("Image prompt is empty.")
        if len(prompt_text) > self.PROMPT_MAX_CHARS:
            prompt_text = prompt_text[: self.PROMPT_MAX_CHARS - 3].rstrip() + "..."

        ratio = _SIZE_TO_RUNWAY_RATIO.get(size.value, "1024:1024")
        headers = {
            "Authorization": f"Bearer {RUNWAY_API_KEY}",
            "Content-Type": "application/json",
            "X-Runway-Version": RUNWAY_API_VERSION,
        }
        payload = {
            "model": RUNWAY_IMAGE_MODEL,
            "promptText": prompt_text,
            "ratio": ratio,
        }

        try:
            create_resp = requests.post(
                f"{RUNWAY_BASE_URL}/text_to_image",
                headers=headers,
                json=payload,
                timeout=self.REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            raise ImageGenerationError(f"Runway request failed: {exc}") from exc

        if not create_resp.ok:
            raise ImageGenerationError(
                f"Runway image request failed ({create_resp.status_code}): "
                f"{create_resp.text[:240]}"
            )

        job_id = create_resp.json().get("id")
        if not job_id:
            raise ImageGenerationError("Runway response missing job id.")

        image_url = self._poll_until_ready(str(job_id), headers)
        return self._download_and_save(image_url, image_id), f"runway-{RUNWAY_IMAGE_MODEL}"

    def _poll_until_ready(self, job_id: str, headers: dict) -> str:
        started = time.time()
        waiting = {"PENDING", "RUNNING", "THROTTLED"}
        while time.time() - started < self.POLL_TIMEOUT_S:
            try:
                resp = requests.get(
                    f"{RUNWAY_BASE_URL}/tasks/{job_id}",
                    headers=headers,
                    timeout=self.REQUEST_TIMEOUT,
                )
            except requests.RequestException as exc:
                raise ImageGenerationError(f"Runway polling failed: {exc}") from exc

            if not resp.ok:
                raise ImageGenerationError(
                    f"Runway polling failed ({resp.status_code}): {resp.text[:240]}"
                )

            data = resp.json()
            status = str(data.get("status", "")).upper()
            logger.info("[Runway Image] Job %s status: %s", job_id, status)

            if status == "SUCCEEDED":
                output = data.get("output", [])
                if isinstance(output, list) and output:
                    return str(output[0])
                raise ImageGenerationError("Runway job succeeded but output URL is missing.")
            if status == "FAILED":
                raise ImageGenerationError("Runway image generation failed.")
            if status in waiting:
                time.sleep(3)
                continue
            raise ImageGenerationError(f"Unexpected Runway status '{status}'.")

        raise ImageGenerationError(
            f"Runway image generation timed out after {self.POLL_TIMEOUT_S}s."
        )

    @staticmethod
    def _download_and_save(image_url: str, image_id: str) -> str:
        try:
            resp = requests.get(image_url, timeout=120)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise ImageGenerationError(f"Failed to download Runway image: {exc}") from exc

        path = OUTPUT_DIR / (image_id + ".png")
        path.write_bytes(resp.content)
        return str(path)


class PollinationsImageGenerator:

    MAX_RETRIES     = 3
    RETRY_DELAY_S   = 5
    REQUEST_TIMEOUT = 120

    def generate_and_save(self, prompt: str, image_id: str, size: ImageSize) -> tuple:
        if not POLLINATIONS_API_KEY:
            raise ImageGenerationError(
                "Pollinations API key is not configured. "
                "Set POLLINATIONS_API_KEY in .env (get one at https://enter.pollinations.ai)."
            )

        w, h = size.value.split("x")
        seed = abs(hash(image_id)) % 99999
        params = urllib.parse.urlencode(
            {
                "width": w,
                "height": h,
                "seed": seed,
                "model": POLLINATIONS_MODEL,
                "nologo": "true",
                "key": POLLINATIONS_API_KEY,
            }
        )
        url = f"{POLLINATIONS_IMAGE_URL}{urllib.parse.quote(prompt)}?{params}"
        headers = {"Authorization": f"Bearer {POLLINATIONS_API_KEY}"}
        last_error = "Unknown error"

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                resp = requests.get(
                    url,
                    headers=headers,
                    timeout=self.REQUEST_TIMEOUT,
                )
                content_type = resp.headers.get("content-type", "")
                if resp.ok and content_type.startswith("image"):
                    path = OUTPUT_DIR / (image_id + ".png")
                    path.write_bytes(resp.content)
                    return str(path), f"pollinations-{POLLINATIONS_MODEL}"

                last_error = self._extract_error(resp)
                logger.warning(
                    "Pollinations image attempt %s/%s failed: HTTP %s — %s",
                    attempt,
                    self.MAX_RETRIES,
                    resp.status_code,
                    last_error,
                )
                if resp.status_code in (401, 402, 403):
                    break
                time.sleep(self.RETRY_DELAY_S)
            except requests.exceptions.Timeout:
                last_error = "Request timed out"
                logger.warning(
                    "Pollinations image attempt %s/%s timed out",
                    attempt,
                    self.MAX_RETRIES,
                )
                time.sleep(self.RETRY_DELAY_S)

        raise ImageGenerationError(
            f"Image generation failed after {self.MAX_RETRIES} attempts: {last_error}"
        )

    @staticmethod
    def _extract_error(resp: requests.Response) -> str:
        content_type = resp.headers.get("content-type", "")
        if "json" in content_type:
            try:
                payload = resp.json()
                if isinstance(payload, dict):
                    err = payload.get("error")
                    if isinstance(err, dict) and err.get("message"):
                        return str(err["message"])
                    if payload.get("message"):
                        return str(payload["message"])
            except ValueError:
                pass
        text = (resp.text or "").strip()
        return text[:240] if text else f"HTTP {resp.status_code}"


def _build_image_generator():
    backend = _resolve_image_backend()
    if backend == "runway":
        return RunwayImageGenerator(), "runway"
    if backend == "pollinations":
        return PollinationsImageGenerator(), "pollinations"
    return LocalFallbackImageGenerator(), "local-fallback"


class LocalFallbackImageGenerator:

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        raw = (hex_color or "#2563EB").lstrip("#")
        if len(raw) != 6:
            raw = "2563EB"
        return tuple(int(raw[i:i+2], 16) for i in (0, 2, 4))

    def generate_and_save(self, prompt: str, image_id: str, size: ImageSize) -> tuple:
        width, height = map(int, size.value.split("x"))
        path = OUTPUT_DIR / (image_id + ".png")

        image = Image.new("RGB", (width, height), "#0F172A")
        draw = ImageDraw.Draw(image)

        primary = self._hex_to_rgb("#2563EB")
        secondary = self._hex_to_rgb("#7C3AED")
        for y in range(height):
            mix = y / max(height - 1, 1)
            color = tuple(
                int(primary[i] * (1 - mix) + secondary[i] * mix) for i in range(3)
            )
            draw.line([(0, y), (width, y)], fill=color)

        overlay_margin = max(16, width // 24)
        panel_top = height // 2 - height // 6
        panel_bottom = height - overlay_margin
        draw.rounded_rectangle(
            [overlay_margin, panel_top, width - overlay_margin, panel_bottom],
            radius=max(18, width // 18),
            fill=(8, 15, 29),
        )

        title_font = LogoOverlay._load_font(max(18, width // 16))
        body_font = LogoOverlay._load_font(max(12, width // 28))

        title = "CMO.ai image preview"
        detail = prompt[:140] + ("..." if len(prompt) > 140 else "")
        note = "Fallback image generated locally because no external image backend is configured."

        draw.text(
            (overlay_margin * 2, panel_top + overlay_margin),
            title,
            fill=(255, 255, 255),
            font=title_font,
        )
        draw.multiline_text(
            (overlay_margin * 2, panel_top + overlay_margin * 2 + 32),
            detail,
            fill=(226, 232, 240),
            font=body_font,
            spacing=6,
        )
        draw.multiline_text(
            (overlay_margin * 2, panel_bottom - overlay_margin * 3),
            note,
            fill=(191, 219, 254),
            font=body_font,
            spacing=5,
        )

        image.save(path)
        return str(path), "local-fallback"


# ── Main Agent ────────────────────────────────────────────────

class ImageGenerationAgent:

    def __init__(self):
        self.kb      = ImageKnowledgeBase()
        self.llm     = GroqLLM()
        self.builder = ImagePromptBuilder(self.llm)
        self.gen, self.image_backend = _build_image_generator()
        self.logo    = LogoOverlay()

    def run(self, request: ImageRequest) -> ImageGenerationResult:
        start   = time.time()
        context = self.kb.get_context(request.platform.value, request.brand.industry)
        ad_copy = self.builder.build_ad_copy(request)
        images  = []

        for i in range(request.num_variations):
            image_id   = request.request_id + "-v" + str(i + 1)
            prompt     = self.builder.build_image_prompt(request, context, variation_index=i)
            local_path, model_used = self.gen.generate_and_save(prompt, image_id, request.image_size)
            logo_applied = False
            if request.logo.enabled:
                local_path   = self.logo.apply(local_path, request.logo, request.brand)
                logo_applied = True
            images.append(GeneratedImage(
                image_id     = image_id,
                request_id   = request.request_id,
                local_path   = local_path,
                prompt_used  = prompt,
                ad_copy      = ad_copy,
                platform     = request.platform.value,
                size         = request.image_size.value,
                model_used   = model_used,
                logo_applied = logo_applied,
                metadata     = {
                    "brand":         request.brand.brand_name,
                    "campaign_goal": request.campaign_goal,
                    "variation":     i,
                },
            ))

        result = ImageGenerationResult(
            request_id          = request.request_id,
            brand_name          = request.brand.brand_name,
            campaign_goal       = request.campaign_goal,
            images              = images,
            ab_test_ready       = len(images) > 1,
            generation_time_sec = round(time.time() - start, 2),
            knowledge_context   = context,
        )

        json_path = OUTPUT_DIR / ("result_" + result.request_id + ".json")
        json_path.write_text(
            json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return result


# ── Public entry point ────────────────────────────────────────

def run_image_agent(request: ImageRequest) -> ImageGenerationResult:
    """Called by the FastAPI endpoint via asyncio.to_thread."""
    return ImageGenerationAgent().run(request)
