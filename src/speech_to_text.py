from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")

def transcribe_audio(audio_path: str) -> str:
    segments, _ = model.transcribe(audio_path, language="ar")
    return " ".join(seg.text for seg in segments).strip()