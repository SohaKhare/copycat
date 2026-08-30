from pathlib import Path

import cv2


def extract_frames(
    video_path: Path,
    output_dir: Path,
    interval_seconds: float = 1.0,
):
    """
    Extract one frame from the video at regular time intervals.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    video = cv2.VideoCapture(str(video_path))

    if not video.isOpened():
        raise ValueError("Could not open video file.")

    fps = video.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        video.release()
        raise ValueError("Could not determine video FPS.")

    frame_interval = max(int(fps * interval_seconds), 1)

    frame_number = 0
    saved_frames = []

    while True:
        success, frame = video.read()

        if not success:
            break

        if frame_number % frame_interval == 0:
            timestamp = frame_number / fps

            frame_filename = (
                f"frame_{len(saved_frames):03d}_"
                f"{timestamp:.2f}s.jpg"
            )

            frame_path = output_dir / frame_filename

            cv2.imwrite(str(frame_path), frame)

            saved_frames.append({
                "path": str(frame_path),
                "timestamp": round(timestamp, 2),
            })

        frame_number += 1

    video.release()

    return saved_frames