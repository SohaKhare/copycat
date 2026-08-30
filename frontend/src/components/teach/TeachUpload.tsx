"use client";

import { useCallback, useRef, useState } from "react";
import { uploadVideo, ApiError } from "@/lib/api";
import type { UploadVideoResponse } from "@/lib/api";
import { getHidePersonalDetails } from "@/lib/privacy-settings";
import { TeachSuccess } from "@/components/teach/TeachSuccess";
import {
  DefaultDropZone,
  SelectedFileView,
  UploadErrorView,
  UploadingView,
} from "@/components/teach/TeachUploadViews";

/**
 * Teach flow state machine — FRONTEND_SPEC.md Phase 6.
 *
 *   default → file selected → uploading → success
 *                                   ↘ error (retry / start over)
 *
 * Client-side pre-validation deliberately mirrors ONLY what the backend
 * enforces (backend/src/backend/main.py /upload-video): the file must be
 * video/* and non-empty. No size limit is invented.
 */

type TeachPhase = "default" | "file-selected" | "uploading" | "success" | "error";

function isVideoFile(file: File): boolean {
  return file.type.startsWith("video/");
}

export function TeachUpload() {
  const [phase, setPhase] = useState<TeachPhase>("default");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<number | null>(null);
  const [result, setResult] = useState<UploadVideoResponse | null>(null);

  const abortRef = useRef<AbortController | null>(null);

  const resetToDefault = useCallback(() => {
    setPhase("default");
    setFile(null);
    setError(null);
    setProgress(null);
    setResult(null);
  }, []);

  function handleFileAccepted(nextFile: File) {
    if (!isVideoFile(nextFile)) {
      setFile(null);
      setPhase("default");
      setError(
        "That file isn't a screen recording. CopyCat learns from video files (MP4, MOV, WebM, and other video formats).",
      );
      return;
    }
    if (nextFile.size === 0) {
      setFile(null);
      setPhase("default");
      setError(
        "That file is empty, so there's no demonstration to learn from. Choose a valid recording and try again.",
      );
      return;
    }

    setFile(nextFile);
    setError(null);
    setProgress(null);
    setPhase("file-selected");
  }

  async function handleUpload() {
    if (!file) return;

    setPhase("uploading");
    setError(null);
    setProgress(null);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await uploadVideo(file, {
        onProgress: (percent) => setProgress(percent),
        signal: controller.signal,
        privacyFilter: getHidePersonalDetails(),
      });
      setResult(response);
      setPhase("success");
    } catch (uploadError) {
      if (
        uploadError instanceof DOMException &&
        uploadError.name === "AbortError"
      ) {
        // User cancelled — back to the selected state, not an error.
        setPhase("file-selected");
        return;
      }
      setError(
        uploadError instanceof ApiError
          ? uploadError.message
          : "Something went wrong while uploading. Please try again.",
      );
      setPhase("error");
    } finally {
      abortRef.current = null;
    }
  }

  function handleCancelUpload() {
    abortRef.current?.abort();
  }

  if (phase === "success" && result) {
    return <TeachSuccess result={result} />;
  }

  if (phase === "error") {
    return (
      <UploadErrorView
        message={error ?? "Something went wrong while uploading."}
        fileName={file?.name ?? null}
        onRetrySame={handleUpload}
        onStartOver={resetToDefault}
      />
    );
  }

  if (phase === "uploading" && file) {
    return (
      <UploadingView
        file={file}
        progress={progress}
        onCancel={handleCancelUpload}
      />
    );
  }

  if (phase === "file-selected" && file) {
    return (
      <SelectedFileView
        file={file}
        onRemove={resetToDefault}
        onUpload={handleUpload}
      />
    );
  }

  return <DefaultDropZone error={error} onFileAccepted={handleFileAccepted} />;
}