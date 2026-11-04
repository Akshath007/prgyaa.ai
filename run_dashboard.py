"""
pragyaa.ai - Speech-to-Text Benchmark & Telephony Evaluation Dashboard
Root Launcher
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(BASE_DIR, "pragyaa_dashboard")
sys.path.insert(0, DASHBOARD_DIR)

if __name__ == "__main__":
    import uvicorn
    print("=" * 72)
    print("  🚀 pragyaa.ai - Telephony STT Model Benchmark Dashboard")
    print("  🌐 Serving at: http://localhost:8501")
    print("  📦 Models: Bodhan 1.2B, Sarvam v1, Gemini 3.5, Nemotron, Whisper, Qwen2")
    print("=" * 72)
    uvicorn.run("pragyaa_dashboard.app:app", host="0.0.0.0", port=8501, reload=True)

