# pragyaa.ai — Speech-to-Text Benchmark & Telephony Evaluation Suite

An enterprise-grade, metrics-focused evaluation dashboard and benchmarking suite for **multilingual Speech-to-Text (ASR) on authentic 8,000 Hz narrowband Indian telephony audio**.

Evaluated on an authentic **Kotak Bank Debt Recovery Call** (`290.16s` / `4m 50s`, G.711 μ-law, 82 micro-turns, heavy line noise and Hindi/Hinglish code-switching).

---

## 📊 Master Telephony Benchmark Matrix (All 6 Models)

| Model & Vendor | Architecture | Supported Languages | Telephony WER (8kHz) | Accuracy | Latency (290s call) | RTF | Streaming Latency | Batching (BS=32) | Peak VRAM / Cost | Verdict |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Bodhan Indic-Transcribe-Core** *(IIT Madras)* | FastConformer (1.2B) | **25 Indian Langs + 8kHz Native** | **8.8%** | **91.2%** | **41.98s** | `0.145x` | 1,500ms (VAD Chunk) | **120 hrs/hr** | 2.34 GB (T4) | **Top Open-Source for Telephony** |
| **Sarvam AI Saarika v1** *(Sarvam Cloud)* | Conformer-RNNT | 10 Indian Langs | **7.5%** | **92.5%** | **18.00s** | `0.062x` | **400ms** (WebSocket) | Cloud API | ₹0.10 / min | **Top Commercial Cloud API** |
| **Google Gemini 3.5 Flash** *(Vertex AI)* | Multimodal LLM (~B) | 100+ Global Langs | **2.1%** | **97.9%** | 163.20s | `0.562x` | 1,200ms (Cloud API) | Cloud TPUs | Vertex Cloud | **Top Quality Reference** |
| **NVIDIA Nemotron-Hinglish-v12** | FastConformer-RNNT (600M) | Hinglish (16kHz Mic Only) | 78.5% *(Drops 85%)* | 21.5% | 8.10s | `0.028x` | **80ms** (Lookahead) | **410 hrs/hr** | 1.90 GB (T4) | **Best for Clean Mic Streaming** |
| **OpenAI Whisper-Large-v3-Turbo** | Transformer (809M) | 99 Multilingual Langs | 64.2% *(Looping)* | 35.8% | 14.50s | `0.050x` | 3,000ms (Pseudo-Chunk) | 240 hrs/hr | 1.60 GB (T4) | **Stuck in Loops on Phone Audio** |
| **Alibaba Qwen2-Audio-7B-Instruct** | Audio-LLM (7.0B) | 8 Langs *(No Hindi)* | >95.0% *(Halluc.)* | 0.0% | 38.20s | `0.131x` | Unsupported (Batch) | 22 hrs/hr | 4.8 GB (NF4) | **Hindi Unsupported (Drama)** |

---

## 🎯 Key Engineering Insights

### 1. Why Standard ASR Fails on Telephony Phone Lines
- **8kHz Bandpass Cutoff (G.711)**: Phone networks cut off all acoustic frequencies above 4,000 Hz. Models trained on clean 16kHz YouTube or microphone data collapse on this bandpass cutoff.
- **NVIDIA Nemotron-Hinglish-v12**: Emits blank CTC tokens on 8kHz audio, dropping over 85% of spoken dialogue.
- **OpenAI Whisper-Large-v3-Turbo**: Without aggressive VAD, Whisper’s autoregressive decoder gets trapped in telephone line noise and enters infinite repetition loops (`पहला वाली पहला वाली... क्या क्या क्या... सब्सक्राइब करें`).
- **Alibaba Qwen2-Audio-7B**: Not pre-trained on Hindi speech. When forced to transcribe, its language prior hallucinates fictional English loan dialogues (`Rs. 50,000 due on 15th April`).

### 2. Why Bodhan AI (IIT Madras) Succeeds
- **Non-Autoregressive FastConformer**: Immune to infinite repetition loops.
- **ULCA Telephony Training**: Pre-trained on Bhashini / ULCA Indian IVR call datasets. Transcribes **865 of 884 words (97.8% word coverage)** on authentic 8kHz telephony.

---

## 🚀 Interactive Dashboard Features

- **Master Benchmark Matrix**: Single-click model switcher inspecting full scorecards, latency curves, and transcripts across all 6 models.
- **Synchronized Audio Player**: 82 second-by-second micro-turns (`[MM:SS-MM:SS]`). Clicking any timestamp seeks audio instantly to that exact moment.
- **Metric Scorecards**: WER, Accuracy, Latency, Streaming Lookahead, Batching Throughput (BS=32), and Supported Languages.
- **Deep-Dive Tabs**:
  1. *Streaming Latency vs Lookahead*: 80ms (Nemotron) vs 400ms (Sarvam) vs 1,500ms (Bodhan).
  2. *Batching & Throughput Scaling*: Scaling across BS 1 to 64 on Tesla T4 FP16 (optimal throughput at BS=32 = 120 hrs/hr).
  3. *Language & Telephony Matrix*: 14 Indian languages breakdown across 8kHz narrowband vs 16kHz studio audio.

---

## 🛠️ Quickstart & Local Installation

### 1. Clone Repository
```bash
git clone https://github.com/Akshath007/prgyaa.ai.git
cd prgyaa.ai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Dashboard
```bash
python run_dashboard.py
```
*Or double click `start_dashboard.bat` on Windows.*

Open your browser at:
```
http://localhost:8501
```

---

## 📁 Repository Structure

```
├── pragyaa_dashboard/
│   ├── app.py                         # FastAPI backend server
│   ├── bodhan_benchmark_results.json  # Raw GPU benchmark logs
│   └── static/
│       ├── index.html                 # Decluttered, metric-first dashboard
│       ├── style.css                  # Linear/Apple minimalist theme (#f8fafc)
│       ├── app.js                     # Multi-model switcher & Chart.js logic
│       ├── audio/                     # 5 telephony benchmark samples & metadata
│       └── Bodhan_Second_by_Second_Transcript_Report.pdf  # Comprehensive report
├── run_dashboard.py                   # Root launcher script
├── start_dashboard.bat                # Windows 1-click launcher
├── requirements.txt                   # Production dependencies
├── generate_second_by_second_report.py # Micro-turn transcript generator
├── Kotak_Second_by_Second_Transcript.txt # 82 diarized micro-turns
└── README.md
```

---

## 📜 License
Apache 2.0 / MIT. Built for the Indian speech AI developer community.
