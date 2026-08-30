"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { useSearchParams } from "next/navigation";
import { VoiceComposer } from "@/components/app/VoiceComposer";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IconCheck } from "@/components/ui/Icons";
import { Markdown } from "@/components/ui/Markdown";
import { cn } from "@/lib/utils";
import { executeCommand, type ExecuteResponse } from "@/lib/api";
import { useMicRecorder } from "@/lib/use-mic-recorder";

/**
 * Voice interaction entry point.
 *
 * Voice: MediaRecorder captures the mic in one shot (tap to start, tap to
 * stop), the audio is sent to POST /execute where Gemini transcribes it, runs
 * the resolve -> plan -> execute pipeline, and returns a short spoken reply
 * that we play back. Typed commands run through the same endpoint but stay
 * silent ("speak only on voice turns").
 */

type VoiceState = "idle" | "recording" | "transcribing" | "running" | "result";

/**
 * Staged progress for a run in flight.
 *
 * `POST /execute` is a single request/response, so the frontend can't get true
 * per-stage callbacks. Instead the known stages advance on a timer tuned to
 * roughly how long each takes; the final "Running it" stage holds until the
 * real response lands. An elapsed timer makes it clear something is happening.
 */
const RUN_STAGES = {
  voice: [
    { key: "transcribe", label: "Transcribing your command", ms: 3500 },
    { key: "match", label: "Finding the matching skill", ms: 3500 },
    { key: "plan", label: "Building the plan", ms: 2500 },
    { key: "execute", label: "Running it", ms: null },
  ],
  text: [
    { key: "match", label: "Finding the matching skill", ms: 3500 },
    { key: "plan", label: "Building the plan", ms: 2500 },
    { key: "execute", label: "Running it", ms: null },
  ],
} as const;

function RunProgress({
  modality,
  title,
}: {
  modality: "text" | "voice";
  title: string;
}) {
  const stages = RUN_STAGES[modality];
  const [active, setActive] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const started = Date.now();
    const tick = setInterval(
      () => setElapsed(Math.floor((Date.now() - started) / 1000)),
      1000,
    );

    const timers: ReturnType<typeof setTimeout>[] = [];
    let acc = 0;
    stages.forEach((stage, index) => {
      if (stage.ms == null) return; // final stage holds until unmount
      acc += stage.ms;
      timers.push(
        setTimeout(
          () => setActive((current) => Math.max(current, index + 1)),
          acc,
        ),
      );
    });

    return () => {
      clearInterval(tick);
      timers.forEach(clearTimeout);
    };
    // stages is a stable module constant keyed by modality
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [modality]);

  const mmss = `${Math.floor(elapsed / 60)}:${String(elapsed % 60).padStart(2, "0")}`;

  return (
    <Card elevated className="flex flex-col gap-5 p-8">
      <div className="flex items-center justify-between gap-4">
        <p className="text-caption font-medium uppercase tracking-[0.18em] text-ink-muted">
          Running &ldquo;{title}&rdquo;
        </p>
        <span className="text-caption tabular-nums text-ink-muted">{mmss}</span>
      </div>

      <ul className="flex flex-col gap-3">
        {stages.map((stage, index) => {
          const done = index < active;
          const current = index === active;
          return (
            <li key={stage.key} className="flex items-center gap-3">
              <span
                className={cn(
                  "flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-caption",
                  done && "border-accent bg-accent text-white",
                  current && "border-accent text-accent",
                  !done && !current && "border-line text-ink-muted",
                )}
              >
                {done ? (
                  <IconCheck className="h-3 w-3" />
                ) : current ? (
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent" />
                ) : (
                  index + 1
                )}
              </span>
              <span
                className={cn(
                  "text-small",
                  current
                    ? "text-ink"
                    : done
                      ? "text-ink-secondary"
                      : "text-ink-muted",
                )}
              >
                {stage.label}
                {current ? "…" : ""}
              </span>
            </li>
          );
        })}
      </ul>
    </Card>
  );
}

export function VoiceCommand() {
  const searchParams = useSearchParams();

  const [state, setState] = useState<VoiceState>("idle");
  const [command, setCommand] = useState(
    () => searchParams.get("command") ?? "",
  );
  const [captured, setCaptured] = useState("");
  const [result, setResult] = useState<ExecuteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Set by startRecording() when the browser lacks MediaRecorder or the mic
  // permission prompt is denied. No pre-mount probe, so SSR and the first
  // client render stay identical.
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const { recording, micUnavailable, start, stop } = useMicRecorder();

  const busy = state === "transcribing" || state === "running";

  const playAudio = useCallback((b64: string, mime: string | null) => {
    try {
      const el = audioRef.current ?? new Audio();
      audioRef.current = el;
      el.src = `data:${mime ?? "audio/wav"};base64,${b64}`;
      el.currentTime = 0;
      void el.play().catch(() => {});
    } catch {
      /* audio unavailable - the transcript/text still shows */
    }
  }, []);

  const run = useCallback(
    async (
      payload:
        | { command: string; modality: "text" }
        | { audio_b64: string; audio_format: string; modality: "voice" },
      label: string,
    ) => {
      setCaptured(label);
      setResult(null);
      setError(null);
      setState(payload.modality === "voice" ? "transcribing" : "running");

      try {
        const response = await executeCommand(payload);
        if (!response || typeof response !== "object") {
          throw new Error("The server returned an empty response.");
        }
        setResult(response);
        if (response.command) setCaptured(response.command);

        if (response.modality === "voice" && response.audio_b64) {
          // Autoplay often fails here — the mic-tap gesture has expired after a
          // long pipeline. The result card's "Play reply" button is the
          // reliable path; this is just the nice-to-have.
          playAudio(response.audio_b64, response.audio_mime);
        }
      } catch (err) {
        setError(
          err instanceof Error && err.message
            ? err.message
            : "Something went wrong.",
        );
        console.error("[VoiceCommand] execute failed", err);
      } finally {
        setState("result");
      }
    },
    [playAudio],
  );

  function toggleRecording() {
    if (recording) {
      stop();
      return;
    }

    void start(
      async (audioB64) => {
        setCaptured("Voice command");
        await run(
          { audio_b64: audioB64, audio_format: "wav", modality: "voice" },
          "Voice command",
        );
      },
      (message) => {
        setError(message);
        setState("result");
      },
    );
  }

  function reset() {
    audioRef.current?.pause();
    setState("idle");
    setCommand("");
    setCaptured("");
    setResult(null);
    setError(null);
  }

  if (state === "transcribing" || state === "running") {
    // Voice runs enter via "transcribing"; typed runs via "running".
    return (
      <RunProgress
        modality={state === "transcribing" ? "voice" : "text"}
        title={captured || "Voice command"}
      />
    );
  }

  if (state === "result") {
    const resolved = result?.resolved_skill ?? null;
    const executionResult = result?.execution_result ?? null;
    const succeeded = !error && executionResult?.success === true;
    const body =
      error ??
      result?.text ??
      executionResult?.message ??
      result?.message ??
      "Done.";

    return (
      <Card
        elevated
        className="flex flex-col items-center gap-4 p-8 text-center"
      >
        <span
          className={cn(
            "flex h-12 w-12 items-center justify-center rounded-full",
            succeeded ? "bg-accent-soft text-accent" : "bg-error/10 text-error",
          )}
        >
          <IconCheck className="h-6 w-6" />
        </span>

        {captured && (
          <p className="text-caption font-medium uppercase tracking-[0.18em] text-ink-muted">
            “{captured}”
          </p>
        )}

        <div className="flex flex-wrap items-center justify-center gap-2">
          <Badge tone={succeeded ? "success" : "error"}>
            {succeeded ? "Success" : "Failed"}
          </Badge>
          {resolved && <Badge tone="info">{resolved.environment}</Badge>}
          {resolved && <Badge>{resolved.match_confidence} match</Badge>}
        </div>

        {error ? (
          <p className="max-w-md whitespace-pre-wrap text-small text-error">
            {error}
          </p>
        ) : (
          <Markdown className="max-w-md text-left text-small text-ink-secondary">
            {body}
          </Markdown>
        )}

        <div className="flex flex-wrap items-center justify-center gap-2">
          {result?.audio_b64 && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() =>
                playAudio(result.audio_b64 as string, result.audio_mime)
              }
            >
              Play reply
            </Button>
          )}
          <Button variant="secondary" size="sm" onClick={reset}>
            Run another command
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <VoiceComposer
      recording={recording}
      micUnavailable={micUnavailable}
      busy={busy}
      text={command}
      onTextChange={setCommand}
      onToggleRecording={toggleRecording}
      onSubmitText={(value) => {
        void run({ command: value, modality: "text" }, value);
      }}
    />
  );
}
