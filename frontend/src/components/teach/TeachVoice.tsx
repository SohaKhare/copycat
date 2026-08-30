"use client";

import { useState } from "react";
import { VoiceComposer } from "@/components/app/VoiceComposer";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IconX } from "@/components/ui/Icons";
import { cn } from "@/lib/utils";
import { ApiError, teachSkill, type UploadVideoResponse } from "@/lib/api";
import { useMicRecorder } from "@/lib/use-mic-recorder";

type TeachVoiceState = "idle" | "working" | "error";

const WORK_STAGES = [
  { key: "hear", label: "Hearing your description" },
  { key: "shape", label: "Turning it into a skill" },
  { key: "save", label: "Saving a draft to review" },
] as const;

export function TeachVoice({
  onBack,
  onLearned,
}: {
  onBack: () => void;
  onLearned: (result: UploadVideoResponse) => void;
}) {
  const [state, setState] = useState<TeachVoiceState>("idle");
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { recording, micUnavailable, start, stop } = useMicRecorder();

  async function submit(
    payload:
      | { command: string; modality: "text" }
      | { audio_b64: string; audio_format: string; modality: "voice" },
  ) {
    setError(null);
    setState("working");
    try {
      const response = await teachSkill(payload);
      onLearned(response);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Could not turn that into a skill. Please try again.",
      );
      setState("error");
    }
  }

  function toggleRecording() {
    if (recording) {
      stop();
      return;
    }
    void start(
      (audioB64) =>
        submit({ audio_b64: audioB64, audio_format: "wav", modality: "voice" }),
      (message) => {
        setError(message);
        setState("error");
      },
    );
  }

  if (state === "working") {
    return (
      <Card elevated className="flex flex-col gap-5 p-8">
        <p className="text-caption font-medium uppercase tracking-[0.18em] text-ink-muted">
          Teaching from your description
        </p>
        <ul className="flex flex-col gap-3">
          {WORK_STAGES.map((stage, index) => (
            <li key={stage.key} className="flex items-center gap-3">
              <span
                className={cn(
                  "flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-caption",
                  index === 0
                    ? "border-accent text-accent"
                    : "border-line text-ink-muted",
                )}
              >
                {index === 0 ? (
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent" />
                ) : (
                  index + 1
                )}
              </span>
              <span
                className={cn(
                  "text-small",
                  index === 0 ? "text-ink" : "text-ink-muted",
                )}
              >
                {stage.label}
                {index === 0 ? "…" : ""}
              </span>
            </li>
          ))}
        </ul>
      </Card>
    );
  }

  if (state === "error") {
    return (
      <Card elevated className="flex flex-col items-center gap-4 p-8 text-center">
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-error/10 text-error">
          <IconX className="h-6 w-6" />
        </span>
        <h2 className="font-heading text-h3 font-bold text-ink">
          That description didn&rsquo;t become a skill
        </h2>
        <p role="alert" className="max-w-md text-small text-ink-secondary">
          {error}
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3">
          <Button size="sm" onClick={() => setState("idle")}>
            Try again
          </Button>
          <Button variant="secondary" size="sm" onClick={onBack}>
            Use a recording instead
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card elevated className="flex flex-col gap-6 p-8">
      <VoiceComposer
        recording={recording}
        micUnavailable={micUnavailable}
        busy={false}
        text={text}
        onTextChange={setText}
        onToggleRecording={toggleRecording}
        onSubmitText={(value) => {
          void submit({ command: value, modality: "text" });
        }}
        speakLabel="Tap to describe the skill"
        listenLabel="Listening… tap to send"
        hint="or type the workflow you want CopyCat to learn"
        listeningHint="Describe the steps the way you would teach a person"
        placeholder="e.g. Search Gmail for internship emails and summarize the latest one"
        submitLabel="Teach"
        textAriaLabel="Type a workflow for CopyCat to learn"
      />
    </Card>
  );
}
