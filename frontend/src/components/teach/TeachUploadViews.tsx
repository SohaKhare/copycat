"use client";

import { useRef, useState, type DragEvent } from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import {
  IconFile,
  IconUpload,
  IconVideo,
  IconX,
} from "@/components/ui/Icons";
import { cn, formatFileSize } from "@/lib/utils";

/**
 * Presentational states of the teach flow — FRONTEND_SPEC.md Phase 6.
 * The state machine lives in TeachUpload.tsx.
 */

export function DefaultDropZone({
  error,
  onFileAccepted,
}: {
  error: string | null;
  onFileAccepted: (file: File) => void;
}) {
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragActive(false);
    const dropped = event.dataTransfer.files?.[0];
    if (dropped) {
      onFileAccepted(dropped);
    }
  }

  return (
    <Card elevated className="flex flex-col gap-6 p-8">
      <div
        role="button"
        tabIndex={0}
        aria-label="Choose a screen recording to teach CopyCat"
        onClick={() => inputRef.current?.click()}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            inputRef.current?.click();
          }
        }}
        onDragOver={(event) => {
          event.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={(event) => {
          event.preventDefault();
          setDragActive(false);
        }}
        onDrop={handleDrop}
        className={cn(
          "flex cursor-pointer flex-col items-center gap-3 rounded-lg border border-dashed border-line bg-surface px-6 py-12 text-center transition-colors duration-200",
          "hover:border-accent hover:bg-beige",
          "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent",
          dragActive && "border-accent bg-beige",
        )}
      >
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-accent-soft text-accent">
          <IconUpload className="h-6 w-6" />
        </span>
        <p className="font-heading text-h3 font-bold text-ink">
          Drop your recording here
        </p>
        <p className="text-small text-ink-secondary">or click to choose a file</p>
      </div>

      {error && (
        <p role="alert" className="text-small text-error">
          {error}
        </p>
      )}

      <p
        id="teach-supported-files"
        className="text-center text-caption text-ink-muted"
      >
        Supported: screen recordings as video files (MP4, MOV, WebM, and other
        video formats). CopyCat learns complex, multi-step workflows — a
        recording of one click isn&rsquo;t a workflow.
      </p>

      <div className="flex justify-center">
        <Button size="lg" onClick={() => inputRef.current?.click()}>
          <IconUpload className="h-5 w-5" />
          Upload a screen recording
        </Button>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        onChange={(event) => {
          const selected = event.target.files?.[0];
          // Reset so choosing the same file again still fires onChange.
          event.target.value = "";
          if (selected) {
            onFileAccepted(selected);
          }
        }}
        className="sr-only"
        tabIndex={-1}
        aria-hidden="true"
      />
    </Card>
  );
}

export function SelectedFileView({
  file,
  onRemove,
  onUpload,
}: {
  file: File;
  onRemove: () => void;
  onUpload: () => void;
}) {
  return (
    <Card elevated className="flex flex-col gap-6 p-8">
      <div className="flex flex-wrap items-center gap-4 rounded-md border border-line bg-surface p-4">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent-soft text-accent">
          <IconVideo className="h-5 w-5" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="truncate font-medium text-ink">{file.name}</p>
          <p className="text-caption text-ink-muted">
            {formatFileSize(file.size)} · ready to upload
          </p>
        </div>
        <button
          type="button"
          onClick={onRemove}
          aria-label={`Remove ${file.name}`}
          className="flex h-8 w-8 items-center justify-center rounded-md text-ink-secondary transition-colors duration-200 hover:bg-beige hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          <IconX className="h-4 w-4" />
        </button>
      </div>

      <div className="flex flex-col items-center gap-3">
        <Button size="lg" onClick={onUpload}>
          <IconUpload className="h-5 w-5" />
          Upload a screen recording
        </Button>
        <p className="text-caption text-ink-muted">
          CopyCat will watch this recording and turn it into a skill.
        </p>
      </div>
    </Card>
  );
}

export function UploadingView({
  file,
  progress,
  onCancel,
}: {
  file: File;
  /** 0–100 when the browser reports a known total; null → indeterminate. */
  progress: number | null;
  onCancel: () => void;
}) {
  const hasRealProgress = progress !== null;

  return (
    <Card elevated className="flex flex-col items-center gap-6 p-8 text-center">
      <span className="flex h-12 w-12 items-center justify-center rounded-full bg-accent-soft text-accent">
        <IconVideo className="h-6 w-6 animate-pulse" />
      </span>
      <div>
        <p className="font-medium text-ink">Uploading your demonstration…</p>
        <p className="mt-1 text-small text-ink-secondary">
          Once uploaded, CopyCat reviews the recording and identifies the
          workflow — this can take a little while.
        </p>
      </div>

      <div className="w-full max-w-md">
        {hasRealProgress ? (
          <div
            role="progressbar"
            aria-valuenow={progress}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Upload progress"
            className="h-1.5 w-full overflow-hidden rounded-full bg-beige"
          >
            <div
              className="h-full rounded-full bg-accent transition-[width] duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        ) : (
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-beige">
            <div className="animate-indeterminate-slide h-full w-1/3 rounded-full bg-accent" />
          </div>
        )}
        <p className="mt-2 text-caption text-ink-muted">
          {hasRealProgress ? `${progress}% uploaded` : "Uploading…"}
        </p>
      </div>

      <div className="flex items-center gap-3 text-small text-ink-secondary">
        <IconFile className="h-4 w-4" />
        <span className="max-w-[16rem] truncate font-medium text-ink">
          {file.name}
        </span>
        <span>· {formatFileSize(file.size)}</span>
      </div>

      <Button variant="secondary" size="sm" onClick={onCancel}>
        Cancel upload
      </Button>
    </Card>
  );
}

export function UploadErrorView({
  message,
  fileName,
  onRetrySame,
  onStartOver,
}: {
  message: string;
  fileName: string | null;
  onRetrySame: () => void;
  onStartOver: () => void;
}) {
  return (
    <Card elevated className="flex flex-col items-center gap-4 p-8 text-center">
      <span className="flex h-12 w-12 items-center justify-center rounded-full bg-accent-soft text-accent">
        <IconX className="h-6 w-6" />
      </span>
      <h2 className="font-heading text-h3 font-bold text-ink">
        The upload didn&rsquo;t complete
      </h2>
      <p role="alert" className="max-w-md text-small text-ink-secondary">
        {message}
      </p>
      {fileName && (
        <p className="text-caption text-ink-muted">
          Attempted file: <span className="font-medium">{fileName}</span>
        </p>
      )}
      <div className="flex flex-wrap items-center justify-center gap-3">
        {fileName && (
          <Button size="sm" onClick={onRetrySame}>
            Try again
          </Button>
        )}
        <Button variant="secondary" size="sm" onClick={onStartOver}>
          {fileName ? "Choose a different file" : "Start over"}
        </Button>
      </div>
    </Card>
  );
}