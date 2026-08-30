"use client";

import { useCallback, useRef, useState } from "react";
import { blobToWavBase64 } from "@/lib/audio";

/**
 * Shared one-shot mic capture used by the dashboard command box and
 * the Teach CopyCat voice path.
 */
export function useMicRecorder() {
  const [recording, setRecording] = useState(false);
  const [micUnavailable, setMicUnavailable] = useState(false);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const stop = useCallback(() => {
    recorderRef.current?.stop();
    recorderRef.current = null;
  }, []);

  const start = useCallback(
    async (
      onWav: (audioB64: string) => void | Promise<void>,
      onError?: (message: string) => void,
    ) => {
      if (micUnavailable) return;

      if (
        typeof window === "undefined" ||
        !navigator.mediaDevices?.getUserMedia ||
        !window.MediaRecorder
      ) {
        setMicUnavailable(true);
        return;
      }

      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      } catch {
        setMicUnavailable(true);
        return;
      }

      let recorder: MediaRecorder;
      try {
        recorder = new MediaRecorder(stream);
      } catch {
        stream.getTracks().forEach((track) => track.stop());
        setMicUnavailable(true);
        return;
      }

      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };

      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        setRecording(false);

        const mime = recorder.mimeType || "audio/webm";
        const blob = new Blob(chunksRef.current, { type: mime });
        if (blob.size === 0) return;

        try {
          const audioB64 = await blobToWavBase64(blob);
          await onWav(audioB64);
        } catch {
          onError?.("Couldn't process the recording. Try typing instead.");
        }
      };

      recorderRef.current = recorder;
      recorder.start();
      setRecording(true);
    },
    [micUnavailable],
  );

  return { recording, micUnavailable, start, stop };
}
