"""
Voice-to-voice front end for CopyCat: mic -> Gemini Live -> detects an
actionable request -> runs it through the real skill pipeline
(voice.command_bridge.run_command, the same one POST /execute uses) ->
speaks the result back.

Run with: uv run python -m backend.voice
"""

import asyncio
import os
import traceback

import pyaudio
from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.voice.command_bridge import run_command

load_dotenv()

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

LIVE_MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"

API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)
pya = pyaudio.PyAudio()

RUN_COMMAND_TOOL = {
    "name": "run_command",
    "description": (
        "Performs a task the user has previously taught CopyCat - checking "
        "messages, organizing files, anything demonstrated and accepted as "
        "a skill. Use this whenever the user asks you to actually DO "
        "something, not just answer a question. Pass their request through "
        "close to verbatim, so it can be matched against learned skills."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": (
                    "The user's request, e.g. 'read my top 5 LinkedIn "
                    "messages' or 'rename my New folder to ZipSems'"
                ),
            }
        },
        "required": ["command"],
    },
    "behavior": "NON_BLOCKING",
}

CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=types.AudioTranscriptionConfig(),
    output_audio_transcription=types.AudioTranscriptionConfig(),
    system_instruction=(
        "You are CopyCat, a voice assistant that executes tasks the user "
        "has taught you by demonstration. When the user asks for something "
        "actionable, call run_command with their request, briefly "
        "acknowledge you're on it, and keep talking naturally while it "
        "runs. When the result comes back, report it out loud in a short, "
        "natural sentence. Keep all replies short and conversational."
    ),
    tools=[{"function_declarations": [RUN_COMMAND_TOOL]}],
)


class VoiceSession:
    def __init__(self):
        self.audio_in_queue = None
        self.out_queue = None
        self.session = None
        self.audio_stream = None
        self.model_speaking = False

    async def listen_mic(self):
        mic_info = pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        while True:
            data = await asyncio.to_thread(
                self.audio_stream.read, CHUNK_SIZE, exception_on_overflow=False
            )
            if self.model_speaking:
                continue
            await self.out_queue.put(data)

    async def send_to_model(self):
        while True:
            data = await self.out_queue.get()
            await self.session.send_realtime_input(
                audio=types.Blob(data=data, mime_type="audio/pcm;rate=16000")
            )

    async def handle_tool_call(self, tool_call):
        for fc in tool_call.function_calls:
            if fc.name != "run_command":
                continue

            command = dict(fc.args).get("command", "")
            print(f"\n[running command] {command}")

            # run_command is sync and the browser executor spins up its own
            # event loop internally - can't call it directly inside this
            # already-running loop, so hand it off to a thread.
            result_text = await asyncio.to_thread(run_command, command)

            print(f"[command done] {result_text}\n")

            await self.session.send_tool_response(
                function_responses=[
                    types.FunctionResponse(
                        id=fc.id,
                        name=fc.name,
                        response={"result": result_text},
                        scheduling="WHEN_IDLE",
                    )
                ]
            )

    async def receive_from_model(self):
        while True:
            turn = self.session.receive()
            async for response in turn:
                if response.data is not None:
                    self.audio_in_queue.put_nowait(response.data)

                sc = response.server_content
                if sc is not None:
                    if sc.input_transcription and sc.input_transcription.text:
                        print(f"You said:    {sc.input_transcription.text}")
                    if sc.output_transcription and sc.output_transcription.text:
                        print(f"CopyCat said: {sc.output_transcription.text}")

                if response.tool_call is not None:
                    asyncio.create_task(self.handle_tool_call(response.tool_call))

            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()

    async def play_audio(self):
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        while True:
            chunk = await self.audio_in_queue.get()
            self.model_speaking = True
            await asyncio.to_thread(stream.write, chunk)
            if self.audio_in_queue.empty():
                await asyncio.sleep(0.3)
                if self.audio_in_queue.empty():
                    self.model_speaking = False

    async def run(self):
        print("Connecting to CopyCat voice... Ctrl+C to hang up.\n")
        async with client.aio.live.connect(model=LIVE_MODEL, config=CONFIG) as session:
            self.session = session
            self.audio_in_queue = asyncio.Queue()
            self.out_queue = asyncio.Queue(maxsize=20)

            async with asyncio.TaskGroup() as tg:
                tg.create_task(self.send_to_model())
                tg.create_task(self.listen_mic())
                tg.create_task(self.receive_from_model())
                tg.create_task(self.play_audio())


def main():
    session = VoiceSession()
    try:
        asyncio.run(session.run())
    except KeyboardInterrupt:
        print("\nCall ended.")
    except ExceptionGroup as eg:
        for e in eg.exceptions:
            traceback.print_exception(e)
    finally:
        if session.audio_stream:
            session.audio_stream.close()
        pya.terminate()


if __name__ == "__main__":
    main()
