import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os
import time
import requests

SAMPLERATE = 16000
SILENCE_THRESHOLD = 0.01
SILENCE_DURATION = 1.5
MAX_DURATION = 15

def listen() -> str:
    whisper_url = os.getenv("WHISPER_URL")
    if whisper_url:
        return _listen_remote(whisper_url)
    return listen_local()


def _listen_remote(base_url: str) -> str:
    response = requests.post(f"{base_url.rstrip('/')}/listen", timeout=MAX_DURATION + 300)
    response.raise_for_status()
    data = response.json()
    return data.get("text", "")


def listen_local() -> str:
    import torch
    from faster_whisper import WhisperModel

    model = WhisperModel(
        "small",
        device="cuda",
        compute_type="float16",
        download_root="./models/whisper"
    )

    audio_path = _record_until_silence()

    segments, _ = model.transcribe(audio_path, language="en")
    text = " ".join(seg.text.strip() for seg in segments)
    os.remove(audio_path)

    del model
    torch.cuda.empty_cache()

    print(f"Transcribed: {text}")
    return text


def _record_until_silence() -> str:
    time.sleep(1)
    print("Listening... speak now.")
    frames = []
    silent_frames = 0
    speaking = False
    chunk = int(SAMPLERATE * 0.1)

    with sd.InputStream(samplerate=SAMPLERATE, channels=1, dtype="float32") as stream:
        while len(frames) * chunk < SAMPLERATE * MAX_DURATION:
            audio_chunk, _ = stream.read(chunk)
            frames.append(audio_chunk)
            volume = np.abs(audio_chunk).mean()

            if volume > SILENCE_THRESHOLD:
                speaking = True
                silent_frames = 0
            elif speaking:
                silent_frames += chunk
                if silent_frames >= SAMPLERATE * SILENCE_DURATION:
                    break

    print("Done recording.")
    audio = np.concatenate(frames)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    sf.write(tmp.name, audio, SAMPLERATE)
    return tmp.name
