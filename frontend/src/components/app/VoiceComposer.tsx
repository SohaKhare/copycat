"use client";

import { type FormEvent } from "react";
import { Button } from "@/components/ui/Button";
import { IconMic } from "@/components/ui/Icons";
import { Input } from "@/components/ui/Input";
import { cn } from "@/lib/utils";

/**
 * Dashboard-style tap-to-speak + type box. Shared by command run and teach.
 */
export function VoiceComposer({
  recording,
  micUnavailable,
  busy,
  text,
  onTextChange,
  onToggleRecording,
  onSubmitText,
  speakLabel = "Tap to speak",
  listenLabel = "Listening… tap to send",
  hint = "or type your command below",
  listeningHint = "CopyCat will reply out loud",
  placeholder = "e.g. Organize my semester files by subject",
  submitLabel = "Run",
  textAriaLabel = "Type a command for CopyCat",
}: {
  recording: boolean;
  micUnavailable: boolean;
  busy: boolean;
  text: string;
  onTextChange: (value: string) => void;
  onToggleRecording: () => void;
  onSubmitText: (value: string) => void;
  speakLabel?: string;
  listenLabel?: string;
  hint?: string;
  listeningHint?: string;
  placeholder?: string;
  submitLabel?: string;
  textAriaLabel?: string;
}) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) return;
    onSubmitText(trimmed);
  }

  return (
    <div className="flex flex-col items-center gap-6">
      <button
        type="button"
        onClick={onToggleRecording}
        disabled={micUnavailable || busy}
        aria-label={recording ? "Stop recording" : "Start recording"}
        aria-pressed={recording}
        className={cn(
          "flex h-28 w-28 items-center justify-center rounded-full bg-accent text-white transition-colors duration-200 hover:bg-accent-hover disabled:opacity-40",
          recording && "animate-pulse-ring",
        )}
      >
        <IconMic className="h-10 w-10" />
      </button>

      <div aria-live="polite" className="text-center">
        <p className="font-medium text-ink">
          {recording ? listenLabel : speakLabel}
        </p>
        <p className="mt-1 text-small text-ink-secondary">
          {recording ? listeningHint : hint}
        </p>
        {micUnavailable && (
          <p className="mt-3 text-small text-info">
            Microphone isn&rsquo;t available here — type instead.
          </p>
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex w-full max-w-xl items-center gap-2"
      >
        <Input
          value={text}
          onChange={(event) => onTextChange(event.target.value)}
          placeholder={placeholder}
          aria-label={textAriaLabel}
          disabled={busy || recording}
        />
        <Button type="submit" disabled={!text.trim() || busy || recording}>
          {submitLabel}
        </Button>
      </form>
    </div>
  );
}
