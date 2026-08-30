"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IconCheck, IconMic } from "@/components/ui/Icons";
import { Input } from "@/components/ui/Input";
import { cn } from "@/lib/utils";
import { ApiError, executeCommand, type ExecuteResponse } from "@/lib/api";

/**
 * Voice interaction entry point — Phase A.
 *
 * CopyCat is voice-first: the mic uses the browser's native Web Speech API
 * (Chrome/Edge) to transcribe locally, no external audio streaming needed.
 * Both voice and the text fallback run through the same real POST /execute
 * pipeline (resolve -> plan -> run -> log).
 */

type VoiceState = "idle" | "listening" | "running" | "result";

// Minimal shape of the Web Speech API - not in TS's default DOM lib.
type SpeechRecognitionLike = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  onresult:
    | ((event: {
        results: { [i: number]: { [j: number]: { transcript: string } } };
      }) => void)
    | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
};

export function VoiceCommand() {
  const searchParams = useSearchParams();
  const [state, setState] = useState<VoiceState>("idle");
  const [command, setCommand] = useState("");
  const [captured, setCaptured] = useState("");
  const [result, setResult] = useState<ExecuteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [voiceUnavailable, setVoiceUnavailable] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);

  const listening = state === "listening";

  useEffect(() => {
    const SpeechRecognitionCtor =
      (
        window as unknown as {
          SpeechRecognition?: new () => SpeechRecognitionLike;
        }
      ).SpeechRecognition ??
      (
        window as unknown as {
          webkitSpeechRecognition?: new () => SpeechRecognitionLike;
        }
      ).webkitSpeechRecognition;

    if (!SpeechRecognitionCtor) return;

    const recognition = new SpeechRecognitionCtor();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setCommand(transcript);
      runCommand(transcript);
    };
    recognition.onerror = () => {
      setState("idle");
      setVoiceUnavailable(true);
    };
    recognition.onend = () => {
      setState((prev) => (prev === "listening" ? "idle" : prev));
    };

    recognitionRef.current = recognition;
    setSpeechSupported(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function runCommand(text: string) {
    const trimmed = text.trim();
    if (!trimmed) return;

    setCaptured(trimmed);
    setState("running");
    setVoiceUnavailable(false);
    setError(null);

    try {
      const response = await executeCommand(trimmed);
      setResult(response);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setState("result");
    }
  }

  function toggleListening() {
    if (!speechSupported || !recognitionRef.current) {
      setVoiceUnavailable(true);
      return;
    }

    if (listening) {
      recognitionRef.current.stop();
      setState("idle");
    } else {
      setCommand("");
      setVoiceUnavailable(false);
      setState("listening");
      recognitionRef.current.start();
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runCommand(command);
  }

  function reset() {
    setState("idle");
    setCommand("");
    setCaptured("");
    setResult(null);
    setError(null);
    setVoiceUnavailable(false);
  }

  if (state === "running") {
    return (
      <Card
        elevated
        className="flex flex-col items-center gap-4 p-8 text-center"
      >
        <p className="text-caption font-medium uppercase tracking-[0.18em] text-ink-muted">
          Running &ldquo;{captured}&rdquo;
        </p>
        <p className="text-small text-ink-secondary">
          Resolving the matching skill and executing it…
        </p>
      </Card>
    );
  }

  if (state === "result") {
    const executionResult = result?.execution_result;
    const succeeded = !error && executionResult?.success;

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
        <p className="text-caption font-medium uppercase tracking-[0.18em] text-ink-muted">
          &ldquo;{captured}&rdquo;
        </p>
        <div className="flex flex-wrap items-center justify-center gap-2">
          <Badge tone={succeeded ? "success" : "error"}>
            {succeeded ? "Success" : "Failed"}
          </Badge>
          <Badge tone="info">{resolved_skill.environment}</Badge>
          <Badge>{resolved_skill.match_confidence} match</Badge>
        </div>
        <p className="max-w-md text-small text-ink-secondary">
          {error
            ? error
            : result?.resolved_skill === null
              ? result.message
              : (executionResult?.message ?? result?.message)}
        </p>
        <Button variant="secondary" size="sm" onClick={reset}>
          Run another command
        </Button>
      </Card>
    );
  }

  if (state === "no-match") {
    return (
      <Card
        elevated
        className="flex flex-col items-center gap-4 p-8 text-center"
      >
        <p className="text-caption font-medium uppercase tracking-[0.18em] text-ink-muted">
          No matching skill
        </p>
        <p className="font-heading text-h3 font-bold text-ink">
          CopyCat couldn&rsquo;t find a workflow for that
        </p>
        <p className="max-w-md text-small text-ink-secondary">
          &ldquo;{submittedCommand}&rdquo; didn&rsquo;t match any accepted
          skill. Teach CopyCat the workflow first, accept the skill, then try
          again with similar wording.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-2">
          <Button size="sm" href="/app/teach">
            Teach CopyCat
          </Button>
          <Button variant="secondary" size="sm" onClick={reset}>
            Try another command
          </Button>
        </div>
      </Card>
    );
  }

  if (state === "error") {
    return (
      <Card
        elevated
        className="flex flex-col items-center gap-4 p-8 text-center"
      >
        <p className="text-caption font-medium uppercase tracking-[0.18em] text-ink-muted">
          Could not run command
        </p>
        <p className="font-heading text-h3 font-bold text-ink">
          Something went wrong
        </p>
        <p className="max-w-md text-small text-error" role="alert">
          {errorMessage}
        </p>
        {errorMessage?.includes("No accepted skills") && (
          <p className="max-w-md text-small text-ink-secondary">
            Accept at least one skill from a teaching session before running
            commands.
          </p>
        )}
        <div className="flex flex-wrap items-center justify-center gap-2">
          <Button size="sm" href="/app/teach">
            Teach CopyCat
          </Button>
          <Button variant="secondary" size="sm" onClick={reset}>
            Try again
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="flex flex-col items-center gap-6">
      <button
        type="button"
        onClick={toggleListening}
        aria-label={listening ? "Stop listening" : "Start listening"}
        aria-pressed={listening}
        className={cn(
          "flex h-28 w-28 items-center justify-center rounded-full bg-accent text-white transition-colors duration-200 hover:bg-accent-hover",
          listening && "animate-pulse-ring",
        )}
      >
        <IconMic className="h-10 w-10" />
      </button>

      <div aria-live="polite" className="text-center">
        <p className="font-medium text-ink">
          {listening ? "Listening…" : "Tap to speak"}
        </p>
        <p className="mt-1 text-small text-ink-secondary">
          {listening ? "Tap again to stop" : "or type your command below"}
        </p>
        {voiceUnavailable && !listening && (
          <p className="mt-3 text-small text-info">
            {speechSupported
              ? "Didn't catch that — try again, or type your command."
              : "Voice recognition isn't supported in this browser — type your command for now."}
          </p>
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex w-full max-w-xl items-center gap-2"
      >
        <Input
          value={command}
          onChange={(event) => setCommand(event.target.value)}
          placeholder="e.g. Organize my semester files by subject"
          aria-label="Type a command for CopyCat"
          disabled={running}
        />
        <Button type="submit" disabled={!command.trim() || running}>
          Run
        </Button>
      </form>
    </div>
  );
}
