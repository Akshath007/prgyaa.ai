"""
Benchmark NVIDIA Nemotron-Hinglish-v12 on Real Telephony Call Center Audio
Compares against the Ground Truth transcript from Gemini 3.5 Flash
"""

import os
import sys
import time
import torch
import torchaudio
import torchaudio.transforms as T
import nemo.collections.asr as nemo_asr
from huggingface_hub import hf_hub_download

# Levenshtein distance for WER and CER calculation
def levenshtein(seq1, seq2):
    size_x, size_y = len(seq1) + 1, len(seq2) + 1
    matrix = [[0] * size_y for _ in range(size_x)]
    for x in range(size_x):
        matrix[x][0] = x
    for y in range(size_y):
        matrix[0][y] = y
    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x - 1] == seq2[y - 1]:
                matrix[x][y] = matrix[x - 1][y - 1]
            else:
                matrix[x][y] = min(
                    matrix[x - 1][y] + 1,      # deletion
                    matrix[x - 1][y - 1] + 1,  # substitution
                    matrix[x][y - 1] + 1       # insertion
                )
    return matrix[size_x - 1][size_y - 1]

def compute_wer(reference: str, hypothesis: str):
    ref_words = reference.strip().split()
    hyp_words = hypothesis.strip().split()
    if not ref_words:
        return 0.0
    dist = levenshtein(ref_words, hyp_words)
    return (dist / len(ref_words)) * 100.0

def compute_cer(reference: str, hypothesis: str):
    ref_chars = list(reference.replace(" ", ""))
    hyp_chars = list(hypothesis.replace(" ", ""))
    if not ref_chars:
        return 0.0
    dist = levenshtein(ref_chars, hyp_chars)
    return (dist / len(ref_chars)) * 100.0

def benchmark_audio(audio_path, ground_truth=None):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[*] Running on device: {device.upper()}")
    
    # 1. Load Audio
    print(f"[*] Loading audio from: {audio_path}")
    sig, sr = torchaudio.load(audio_path)
    if sig.shape[0] > 1:
        sig = sig.mean(dim=0, keepdim=True)
    if sr != 16000:
        print(f"[*] Resampling from {sr}Hz to 16000Hz...")
        resampler = T.Resample(sr, 16000)
        sig = resampler(sig)
        sr = 16000

    audio_len_sec = sig.shape[1] / 16000.0
    print(f"[*] Audio Duration: {audio_len_sec:.2f} seconds ({audio_len_sec/60:.2f} mins)")

    # 2. Load Model
    print("[*] Loading Nemotron-Hinglish-v12...")
    model_path = hf_hub_download(repo_id="smajji/nemotron-hinglish-v12", filename="nemotron-hinglish-v12.nemo")
    asr_model = nemo_asr.models.ASRModel.restore_from(model_path, map_location=device)
    asr_model.eval()

    # 3. Direct GPU Inference
    print("[*] Running Forward & RNN-T Greedy Decoding...")
    sig = sig.to(device)
    sig_len = torch.tensor([sig.shape[1]], dtype=torch.long, device=device)
    prompt_idx = torch.tensor([101], dtype=torch.long, device=device) # auto LID

    start_time = time.time()
    with torch.inference_mode():
        enc, enc_len = asr_model.forward(
            input_signal=sig,
            input_signal_length=sig_len,
            prompt_indices=prompt_idx
        )
        res = asr_model.decoding.rnnt_decoder_predictions_tensor(
            encoder_output=enc,
            encoded_lengths=enc_len,
            return_hypotheses=False
        )
    end_time = time.time()

    if isinstance(res, tuple): res = res[0]
    if isinstance(res, list) and len(res) > 0:
        first = res[0]
        hyp_text = first.text if hasattr(first, 'text') else str(first)
    else:
        hyp_text = str(res)

    infer_time = end_time - start_time
    rtf = infer_time / audio_len_sec

    # 4. Print Benchmark Report
    print("\n" + "="*70)
    print(" 📊 NVIDIA NEMOTRON-HINGLISH-V12 BENCHMARK REPORT")
    print("="*70)
    print(f"⏱️  Audio Duration    : {audio_len_sec:.2f} seconds")
    print(f"⚡  Inference Time    : {infer_time:.3f} seconds")
    print(f"🚀  Real-Time Factor  : {rtf:.4f}x ({1/rtf:.1f}x faster than real-time)")
    print(f"🌐  Language / Prompt : auto (Index 101 - Hinglish code-switching)")
    
    if ground_truth:
        wer = compute_wer(ground_truth, hyp_text)
        cer = compute_cer(ground_truth, hyp_text)
        accuracy = max(0.0, 100.0 - wer)
        print(f"🎯  Word Error Rate   : {wer:.2f}%")
        print(f"🔤  Char Error Rate   : {cer:.2f}%")
        print(f"✅  Accuracy Score    : {accuracy:.2f}%")

    print("\n" + "-"*70)
    print("📝 PREDICTED TRANSCRIPTION:")
    print(f"\"{hyp_text.strip()}\"")
    print("="*70 + "\n")

    return {
        "duration": audio_len_sec,
        "inference_time": infer_time,
        "rtf": rtf,
        "transcription": hyp_text.strip(),
        "wer": wer if ground_truth else None,
        "accuracy": accuracy if ground_truth else None
    }

if __name__ == "__main__":
    test_audio = r"e:\PROJECTS\stt\pragyaa_dashboard\static\audio\kotak_call_center_30s.wav"
    gt = "मैं कोटक बैंक फाइनेंस से बात कर रही हूँ आपका लोन पेंडिंग है वो क्यों नहीं भर रहे हो सर आप कोटक का कौन सा सर कोटक का वो नहीं ना उसके पहले वाला बैंक का नाम बोलो उसके पहले वाली क्या वो बैंक का नाम बोलो क्या बोलूं कोटक नहीं उसके पहले वाली बैंक का नाम बोलो कोटक बोल रही हूँ कोटक कोटक बैंक अरे हाँ पर वो जो जो लोन ट्रांसफर हुई है ना आपके अकाउंट के उससे बैंक में तो उसके उसकी मैटर चल रही है कोर्ट के अंदर ऑलरेडी मेरी आपका बंदा पैसे लेके गया था स्लिप भी नहीं होना पर कोर्ट के अंदर जमा कराया था आज से आठ नौ साल पहले"
    
    if len(sys.argv) > 1:
        test_audio = sys.argv[1]
    
    benchmark_audio(test_audio, gt)

