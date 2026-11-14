"""
===================================================================
  LIVE ACCENT TRANSLATION BRIDGE FOR ZOOM / GOOGLE MEET
===================================================================
1. Listens to your microphone continuously.
2. Detects when you speak and pause (VAD).
3. Converts your Indian English into an authentic American accent.
4. Streams the American speech directly to:
   - "CABLE Input (VB-Audio)" (so Zoom/GMeet hears it)
===================================================================
"""

import os
import sys
import time
import queue
import numpy as np
import sounddevice as sd
import soundfile as sf
import soxr
from faster_whisper import WhisperModel
from gtts import gTTS

# Suppress urllib3 warnings
import warnings
warnings.filterwarnings("ignore")

# --- 1. Find Audio Devices ---
devices = sd.query_devices()
mic_id = None
output_id = None

print("\nScanning Audio Devices...")
# Prioritize CABLE Input WASAPI or MME
for idx, dev in enumerate(devices):
    name = dev['name']
    if "CABLE Input" in name and dev['max_output_channels'] > 0:
        output_id = idx
        break

for idx, dev in enumerate(devices):
    name = dev['name']
    if mic_id is None and dev['max_input_channels'] > 0 and ("Realtek" in name or "Microphone" in name):
        mic_id = idx
        break

if output_id is not None:
    print(f"[*] Found Virtual Mic for Zoom: [{output_id}] {devices[output_id]['name']}")
else:
    print("[!] VB-Cable not detected. Routing audio to default Speakers.")
    output_id = sd.default.device[1]

if mic_id is None:
    mic_id = sd.default.device[0]

out_dev_info = sd.query_devices(output_id)
TARGET_SR = int(out_dev_info['default_samplerate'])
OUT_CHANNELS = out_dev_info['max_output_channels']

print(f"[*] Using Input Mic: [{mic_id}] {devices[mic_id]['name']}")
print(f"[*] Using Output Device: [{output_id}] {devices[output_id]['name']} (Native SR: {TARGET_SR}Hz, {OUT_CHANNELS}ch)")

# --- 2. Load Whisper Model ---
print("\nLoading fast ASR model (faster-whisper)...")
asr = WhisperModel('tiny.en', device='cpu', compute_type='int8')
print("ASR model ready!")

# --- 3. Audio Streaming Configuration ---
SAMPLE_RATE = 16000
CHUNK_DURATION = 0.5  # 500ms audio chunks
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION)
SILENCE_THRESHOLD = 0.02  # Energy threshold for speech detection
SILENCE_TIMEOUT = 1.0     # Pause duration to trigger conversion

audio_q = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    if status:
        pass
    audio_q.put(indata.copy())

def convert_and_stream(audio_buffer):
    """Transcribes audio, resamples, and plays American accent to the output device."""
    sf.write("temp_live_in.wav", audio_buffer, SAMPLE_RATE)
    
    # 1. Transcribe
    segments, _ = asr.transcribe("temp_live_in.wav", beam_size=1)
    text = " ".join([s.text for s in segments]).strip()
    
    if not text or len(text) < 2:
        return
        
    print(f"\n[You Spoke]: {text}")
    
    # 2. American TTS
    tts = gTTS(text=text, lang='en', tld='com')
    tts.save("temp_live_out.mp3")
    
    raw_data, orig_sr = sf.read("temp_live_out.mp3", dtype='float32')
    
    # 3. Resample to match VB-Cable's exact native sample rate (e.g. 48000 Hz)
    if orig_sr != TARGET_SR:
        data_resampled = soxr.resample(raw_data, orig_sr, TARGET_SR)
    else:
        data_resampled = raw_data
        
    # Match stereo/channel requirements of the output device
    if OUT_CHANNELS > 1 and data_resampled.ndim == 1:
        data_resampled = np.column_stack([data_resampled] * OUT_CHANNELS)
    
    print(f"[Streaming to Zoom/GMeet] -> '{text}'")
    
    # 4. Stream to Zoom virtual mic
    sd.play(data_resampled, TARGET_SR, device=output_id)
    sd.wait()
    print("[Ready for next sentence... speak anytime]")

def start_live_listener():
    print("\n" + "="*60)
    print(" LIVE ACCENT TRANSLATOR IS RUNNING!")
    print(" 1. Speak an English sentence into your mic naturally.")
    print(" 2. In Zoom / Google Meet, set Microphone to: 'CABLE Output'")
    print(" Press Ctrl+C to stop.")
    print("="*60 + "\n")
    
    is_speaking = False
    speech_frames = []
    silence_start = None
    
    with sd.InputStream(device=mic_id, channels=1, samplerate=SAMPLE_RATE,
                        blocksize=CHUNK_SAMPLES, callback=audio_callback):
        while True:
            chunk = audio_q.get()
            energy = np.sqrt(np.mean(chunk**2))
            
            if energy > SILENCE_THRESHOLD:
                if not is_speaking:
                    is_speaking = True
                    print("[*] Speech detected... listening...", end="\r", flush=True)
                speech_frames.append(chunk)
                silence_start = None
            else:
                if is_speaking:
                    speech_frames.append(chunk)
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > SILENCE_TIMEOUT:
                        # User stopped speaking -> Convert now
                        full_audio = np.concatenate(speech_frames, axis=0)
                        speech_frames = []
                        is_speaking = False
                        silence_start = None
                        convert_and_stream(full_audio)

if __name__ == "__main__":
    try:
        start_live_listener()
    except KeyboardInterrupt:
        print("\nStopped.")
        for f in ["temp_live_in.wav", "temp_live_out.mp3"]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
