import os
import sys
import unittest.mock

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Mock packages for Windows NeMo 1.23.0 compatibility
sys.modules['youtokentome'] = unittest.mock.MagicMock()
sys.modules['pyannote.metrics'] = unittest.mock.MagicMock()
sys.modules['pyannote.metrics.diarization'] = unittest.mock.MagicMock()
sys.modules['IPython'] = unittest.mock.MagicMock()
sys.modules['IPython.display'] = unittest.mock.MagicMock()

import huggingface_hub
huggingface_hub.ModelFilter = object

import pytorch_lightning.loggers
if not hasattr(pytorch_lightning.loggers, 'NeptuneLogger'):
    pytorch_lightning.loggers.NeptuneLogger = object

import torch
import nemo.collections.asr as nemo_asr

NEMO_PATH = os.path.expanduser('~/.cache/huggingface/hub/models--smajji--nemotron-hinglish-v12/snapshots/d761d4c10ada563bf99dd9b033688a5366f7bccc/nemotron-hinglish-v12.nemo')

def main():
    print("=" * 65)
    print(" [*] Testing Nemotron-Hinglish-v12 Loading & Inference")
    print(f" [*] File: {NEMO_PATH}")
    print("=" * 65)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[*] Restoring ASRModel on {device.upper()}...")
    
    try:
        model = nemo_asr.models.ASRModel.restore_from(restore_path=NEMO_PATH, map_location=device)
        model.eval()
        print("[OK] Nemotron-Hinglish-v12 restored successfully!")
    except Exception as e:
        print(f"[!] Error loading on {device}: {e}")
        print("[*] Retrying on CPU...")
        model = nemo_asr.models.ASRModel.restore_from(restore_path=NEMO_PATH, map_location="cpu")
        model.eval()
        print("[OK] Nemotron-Hinglish-v12 restored on CPU!")

    if os.path.exists("test_speech.wav"):
        print("\n[*] Transcribing test_speech.wav...")
        import time
        t0 = time.time()
        res = model.transcribe(["test_speech.wav"])
        dt = time.time() - t0
        print("=" * 65)
        print(f"Transcription: {res[0] if isinstance(res, list) else res}")
        print(f"Time Taken: {dt:.2f}s")
        print("=" * 65)

if __name__ == "__main__":
    main()

