"""
Local privacy filter — OCR scan and black-box redaction before Gemini analysis.

Original frames stay on disk unchanged; redacted copies are written to a
``redacted/`` subfolder and only those paths are returned for AI analysis.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import cv2

from backend.logging_setup import log

# Lazy-loaded OCR engine — RapidOCR downloads models on first use.
_ocr_engine = None

EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)

PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[\s.\-]?)?"
    r"(?:\(?\d{3}\)?[\s.\-]?)"
    r"\d{3}[\s.\-]?\d{4}\b"
)

SSN_PATTERN = re.compile(r"\b\d{3}[\s.\-]?\d{2}[\s.\-]?\d{4}\b")

CREDIT_CARD_PATTERN = re.compile(
    r"\b(?:\d{4}[\s.\-]?){3}\d{4}\b"
)

ID_NUMBER_PATTERN = re.compile(r"\b\d{8,}\b")

PASSWORD_KEYWORDS = (
    "password",
    "passwd",
    "pwd",
    "pin",
    "passcode",
    "secret",
    "ssn",
    "social security",
    "api key",
    "apikey",
    "token",
    "credential",
)

SENSITIVE_TEXT_PATTERNS = (
    EMAIL_PATTERN,
    PHONE_PATTERN,
    SSN_PATTERN,
    CREDIT_CARD_PATTERN,
    ID_NUMBER_PATTERN,
)


@dataclass
class PrivacyFilterResult:
    applied: bool
    frames_processed: int = 0
    regions_redacted: int = 0
    errors: list[str] = field(default_factory=list)


def _get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        from rapidocr_onnxruntime import RapidOCR

        _ocr_engine = RapidOCR()
    return _ocr_engine


def _box_to_rect(box: list[list[float]]) -> tuple[int, int, int, int]:
    xs = [int(point[0]) for point in box]
    ys = [int(point[1]) for point in box]
    x1, x2 = min(xs), max(xs)
    y1, y2 = min(ys), max(ys)
    return x1, y1, x2 - x1, y2 - y1


def _expand_rect(
    x: int,
    y: int,
    w: int,
    h: int,
    *,
    img_w: int,
    img_h: int,
    padding: int = 4,
) -> tuple[int, int, int, int]:
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(img_w, x + w + padding)
    y2 = min(img_h, y + h + padding)
    return x1, y1, x2 - x1, y2 - y1


def _text_is_sensitive(text: str) -> bool:
    cleaned = text.strip()
    if not cleaned:
        return False
    return any(pattern.search(cleaned) for pattern in SENSITIVE_TEXT_PATTERNS)


def _is_password_keyword(text: str) -> bool:
    lowered = text.strip().lower()
    return any(keyword in lowered for keyword in PASSWORD_KEYWORDS)


def _detect_sensitive_regions(
    ocr_results: list,
    img_w: int,
    img_h: int,
) -> list[tuple[int, int, int, int]]:
    if not ocr_results:
        return []

    entries: list[dict] = []
    for item in ocr_results:
        if len(item) < 2:
            continue
        box, text = item[0], str(item[1])
        x, y, w, h = _box_to_rect(box)
        cx = x + w / 2
        cy = y + h / 2
        entries.append(
            {
                "text": text,
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "cx": cx,
                "cy": cy,
            }
        )

    regions: list[tuple[int, int, int, int]] = []

    for entry in entries:
        if _text_is_sensitive(entry["text"]):
            regions.append(
                _expand_rect(
                    entry["x"],
                    entry["y"],
                    entry["w"],
                    entry["h"],
                    img_w=img_w,
                    img_h=img_h,
                    padding=6,
                )
            )

    for index, entry in enumerate(entries):
        if not _is_password_keyword(entry["text"]):
            continue

        label_cy = entry["cy"]
        label_h = entry["h"]

        for candidate in entries:
            if candidate is entry:
                continue

            same_line = abs(candidate["cy"] - label_cy) <= label_h * 1.5
            to_the_right = candidate["cx"] > entry["cx"]

            below = (
                candidate["y"] >= entry["y"] + entry["h"] * 0.5
                and candidate["y"] <= entry["y"] + entry["h"] * 4
                and abs(candidate["cx"] - entry["cx"]) <= entry["w"] * 3
            )

            if same_line and to_the_right:
                regions.append(
                    _expand_rect(
                        candidate["x"],
                        candidate["y"],
                        candidate["w"],
                        candidate["h"],
                        img_w=img_w,
                        img_h=img_h,
                        padding=8,
                    )
                )
            elif below:
                regions.append(
                    _expand_rect(
                        candidate["x"],
                        candidate["y"],
                        candidate["w"],
                        candidate["h"],
                        img_w=img_w,
                        img_h=img_h,
                        padding=8,
                    )
                )

    return _merge_overlapping(regions)


def _merge_overlapping(
    regions: list[tuple[int, int, int, int]],
) -> list[tuple[int, int, int, int]]:
    if not regions:
        return []

    merged: list[tuple[int, int, int, int]] = []
    for region in sorted(regions):
        x, y, w, h = region
        placed = False
        for index, (mx, my, mw, mh) in enumerate(merged):
            if _rects_overlap(x, y, w, h, mx, my, mw, mh):
                nx1 = min(x, mx)
                ny1 = min(y, my)
                nx2 = max(x + w, mx + mw)
                ny2 = max(y + h, my + mh)
                merged[index] = (nx1, ny1, nx2 - nx1, ny2 - ny1)
                placed = True
                break
        if not placed:
            merged.append(region)

    return merged


def _rects_overlap(
    x1: int,
    y1: int,
    w1: int,
    h1: int,
    x2: int,
    y2: int,
    w2: int,
    h2: int,
) -> bool:
    return not (
        x1 + w1 < x2
        or x2 + w2 < x1
        or y1 + h1 < y2
        or y2 + h2 < y1
    )


def _redact_regions(
    image_path: Path,
    output_path: Path,
    regions: list[tuple[int, int, int, int]],
) -> int:
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read frame: {image_path}")

    for x, y, w, h in regions:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), thickness=-1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)
    return len(regions)


def _redact_frame(frame_path: Path, redacted_dir: Path) -> tuple[Path, int, str | None]:
    relative_name = frame_path.name
    output_path = redacted_dir / relative_name

    try:
        ocr_engine = _get_ocr_engine()
        ocr_results, _ = ocr_engine(str(frame_path))
    except Exception as error:
        return frame_path, 0, f"OCR failed for {frame_path.name}: {error}"

    image = cv2.imread(str(frame_path))
    if image is None:
        return frame_path, 0, f"Could not read frame: {frame_path.name}"

    img_h, img_w = image.shape[:2]
    regions = _detect_sensitive_regions(ocr_results or [], img_w, img_h)

    if not regions:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), image)
        return output_path, 0, None

    try:
        count = _redact_regions(frame_path, output_path, regions)
        return output_path, count, None
    except Exception as error:
        return frame_path, 0, f"Redaction failed for {frame_path.name}: {error}"


def apply_privacy_filter(
    frames: list[dict],
    *,
    enabled: bool = True,
) -> tuple[list[dict], PrivacyFilterResult]:
    """
    Scan extracted frames for sensitive text and write black-box redactions.

    Returns updated frame metadata (paths may point to ``redacted/`` copies)
    and a summary of what was applied.
    """

    if not enabled:
        return frames, PrivacyFilterResult(applied=False)

    if not frames:
        return frames, PrivacyFilterResult(applied=True, frames_processed=0)

    first_path = Path(frames[0]["path"])
    redacted_dir = first_path.parent / "redacted"

    redacted_frames: list[dict] = []
    total_regions = 0
    errors: list[str] = []

    for frame in frames:
        frame_path = Path(frame["path"])
        output_path, region_count, error = _redact_frame(frame_path, redacted_dir)

        redacted_frames.append(
            {
                "path": str(output_path),
                "timestamp": frame["timestamp"],
            }
        )
        total_regions += region_count

        if error:
            log.warning("privacy filter: %s", error)
            errors.append(error)

    log.info(
        "privacy filter applied to %d frame(s), %d region(s) redacted",
        len(redacted_frames),
        total_regions,
    )

    return redacted_frames, PrivacyFilterResult(
        applied=True,
        frames_processed=len(redacted_frames),
        regions_redacted=total_regions,
        errors=errors,
    )
