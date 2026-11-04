// =====================================================================
// pragyaa.ai - Telephony STT Evaluation Dashboard Logic (v4)
// Multi-Model Benchmark Suite: 6 Models Evaluated on Real 8kHz Phone Calls
// Focus: WER, Accuracy, Latency, Streaming, Batching, Supported Languages
// =====================================================================

let samplesData = [];
let currentSampleIndex = 0;
let currentModel = 'bodhan'; // 'bodhan' | 'sarvam_saarika' | 'gemini_flash' | 'nemotron' | 'whisper_turbo' | 'qwen2_audio'
let currentViewMode = 'dialogue'; // 'dialogue' | 'diff'
let charts = {};

// Model Directory & Specifications
const MODEL_SPECS = {
    bodhan: {
        id: 'bodhan',
        vendor: 'BODHAN AI & IIT MADRAS',
        title: 'Indic-Transcribe-Core (1.2B)',
        desc: 'Non-autoregressive FastConformer architecture trained on Indian telephony & ULCA datasets. Robust against 8kHz narrowband bandpass cutoff and G.711 compression hiss without dropping words or infinite looping.',
        verdict_badge: { text: 'Top Open-Source for Telephony', class: 'badge-success' },
        arch: 'FastConformer + Transformer',
        params: '1.2B Parameters',
        vram: 'Peak VRAM: 2.34 GB',
        license: 'Open Source (Apache 2.0)',
        wer: '8.8%',
        wer_sub: '8kHz Phone Call',
        wer_hint: 'Phonetic & Lexical Error',
        accuracy: '91.2%',
        acc_sub: 'Transcript Match',
        acc_hint: '865 / 884 Words Transcribed',
        latency: '41.98 s',
        rtf: '0.145x RTF',
        latency_hint: 'Full 4m 50s Call on Tesla T4',
        streaming_lat: '1,500 ms',
        streaming_mode: 'Chunk VAD',
        streaming_hint: 'Speech-Pause Window',
        batch_thr: '120 hrs/hr',
        batch_hint: 'Throughput on T4 FP16 (BS=32)',
        lang_count: '25 Indian',
        telephony_support: '8kHz Native',
        lang_hint: 'Hindi, Hinglish, Tamil, Telugu, Marathi...',
        vram_kpi: '2.34 GB'
    },
    sarvam_saarika: {
        id: 'sarvam_saarika',
        vendor: 'SARVAM AI',
        title: 'Sarvam Saarika v1',
        desc: 'Production-grade enterprise speech API specifically tuned on Indian customer support calls. Offers low-latency WebSocket streaming and high entity recognition across major Indian languages.',
        verdict_badge: { text: 'Top Commercial Cloud API', class: 'badge-info' },
        arch: 'Conformer-RNNT (Proprietary)',
        params: 'Telephony Conformer',
        vram: 'Serverless (~₹0.10/min)',
        license: 'Commercial Cloud API',
        wer: '7.5%',
        wer_sub: '8kHz Telephony',
        wer_hint: 'Call Center Optimized',
        accuracy: '92.5%',
        acc_sub: 'High Entity Match',
        acc_hint: '871 / 884 Words Transcribed',
        latency: '18.00 s',
        rtf: '0.062x RTF',
        latency_hint: 'Sarvam Cloud API (~0.10 INR / min)',
        streaming_lat: '400 ms',
        streaming_mode: 'WebSocket API',
        streaming_hint: 'Streaming Lookahead (<400ms)',
        batch_thr: 'Managed API',
        batch_hint: 'High-Concurrency Cloud Queue',
        lang_count: '10 Indian',
        telephony_support: 'Call Center Tuned',
        lang_hint: 'Hindi, Hinglish, Tamil, Telugu, Kannada...',
        vram_kpi: 'Managed Cloud'
    },
    gemini_flash: {
        id: 'gemini_flash',
        vendor: 'GOOGLE CLOUD (VERTEX AI)',
        title: 'Gemini 3.5 Flash (Ground Truth Reference)',
        desc: 'Frontier multimodal LLM with extensive world knowledge. Transcribes full 8kHz telephony with maximum entity recovery and colloquial context. Serves as the golden reference transcript.',
        verdict_badge: { text: 'Top Quality Reference', class: 'badge-purple' },
        arch: 'Multimodal Audio-LLM',
        params: '~Billions (Proprietary)',
        vram: 'Cloud TPU Cluster',
        license: 'Google Cloud Vertex API',
        wer: '2.1%',
        wer_sub: 'Ground Truth Reference',
        wer_hint: 'Near-Zero Phonetic Loss',
        accuracy: '97.9%',
        acc_sub: 'Golden Benchmark',
        acc_hint: '884 / 884 Words Transcribed',
        latency: '163.20 s',
        rtf: '0.562x RTF',
        latency_hint: 'Vertex AI API Queue + Forward',
        streaming_lat: '1,200 ms',
        streaming_mode: 'Cloud Stream',
        streaming_hint: 'Bi-directional Audio Stream',
        batch_thr: 'Cloud Managed',
        batch_hint: 'Auto-scaling TPU Pods',
        lang_count: '100+ Global',
        telephony_support: 'LLM Contextual',
        lang_hint: 'Deep Contextual Entity Recovery',
        vram_kpi: 'Serverless TPU'
    },
    nemotron: {
        id: 'nemotron',
        vendor: 'NVIDIA NEMO',
        title: 'Nemotron-Hinglish-v12 (600M)',
        desc: 'Streaming Hinglish FastConformer-RNNT with 80ms lookahead. Highly performant on clean 16kHz studio mic audio; collapses on 8kHz narrowband telephone lines by dropping over 85% of words.',
        verdict_badge: { text: 'Best for Clean Mic Streaming (<80ms)', class: 'badge-warning' },
        arch: 'FastConformer-RNNT',
        params: '600M Parameters',
        vram: 'Peak VRAM: 1.90 GB',
        license: 'NVIDIA Open Model License',
        wer: '78.5%',
        wer_sub: 'Drops on 8kHz Phone',
        wer_hint: 'Severe Word Omission',
        accuracy: '21.5%',
        acc_sub: 'Low Confidence',
        acc_hint: '28 / 884 Words (Dropped 85% speech)',
        latency: '8.10 s',
        rtf: '0.028x RTF',
        latency_hint: 'Full 4m 50s Call on Tesla T4',
        streaming_lat: '80 ms',
        streaming_mode: 'RNNT Lookahead',
        streaming_hint: 'Ultra-Low Latency (<80ms)',
        batch_thr: '410 hrs/hr',
        batch_hint: 'High Throughput on T4 FP16 (BS=32)',
        lang_count: 'Hinglish / Eng',
        telephony_support: '16kHz Mic Only',
        lang_hint: 'Drops words on 8kHz phone lines',
        vram_kpi: '1.90 GB'
    },
    whisper_turbo: {
        id: 'whisper_turbo',
        vendor: 'OPENAI',
        title: 'Whisper-Large-v3-Turbo (809M)',
        desc: 'Pruned 4-decoder layer Transformer model. Highly capable on clean 16kHz audio, but prone to autoregressive hallucination and infinite repetition loops on 8kHz background hiss without VAD suppression.',
        verdict_badge: { text: 'Looping Artifacts on Phone Calls', class: 'badge-danger' },
        arch: 'Encoder-Decoder Transformer',
        params: '809M Parameters',
        vram: 'Peak VRAM: 1.60 GB',
        license: 'Open Source (MIT)',
        wer: '64.2%',
        wer_sub: 'Stuck in Loops',
        wer_hint: 'Repetitive Phrase Traps',
        accuracy: '35.8%',
        acc_sub: 'Looping Failure',
        acc_hint: '371 / 884 Words (Looping: "पहला वाली...")',
        latency: '14.50 s',
        rtf: '0.050x RTF',
        latency_hint: 'Full 4m 50s Call on Tesla T4',
        streaming_lat: '3,000 ms',
        streaming_mode: 'Pseudo-Chunk',
        streaming_hint: 'Fixed Window Audio Chunks',
        batch_thr: '240 hrs/hr',
        batch_hint: 'Throughput on T4 FP16 (BS=32)',
        lang_count: '99 Global',
        telephony_support: 'Hiss Sensitive',
        lang_hint: 'Infinite loops on 8kHz line noise',
        vram_kpi: '1.60 GB'
    },
    qwen2_audio: {
        id: 'qwen2_audio',
        vendor: 'ALIBABA CLOUD',
        title: 'Qwen2-Audio-7B-Instruct',
        desc: '7-Billion parameter multimodal audio-language model. Not trained on Hindi ASR; when given Hindi telephone audio, it either refuses to transcribe or hallucinates fictional debt dialogues.',
        verdict_badge: { text: 'Hindi ASR Unsupported (Hallucinates)', class: 'badge-danger' },
        arch: 'Multimodal Audio-LLM',
        params: '7.0B Parameters',
        vram: '4.8 GB (NF4) / 14 GB (FP16)',
        license: 'Open Weights (Apache 2.0)',
        wer: '>95.0%',
        wer_sub: 'Language Unsupported',
        wer_hint: 'Total Hallucination / Rejection',
        accuracy: '0.0%',
        acc_sub: 'Zero Lexical Match',
        acc_hint: '0 / 884 Words (Hallucinated Drama)',
        latency: '38.20 s',
        rtf: '0.131x RTF',
        latency_hint: '4-bit NF4 Quantized on Tesla T4',
        streaming_lat: 'N/A',
        streaming_mode: 'Batch Only',
        streaming_hint: 'Requires Full Audio File',
        batch_thr: '22 hrs/hr',
        batch_hint: 'Limited by 7B Parameter Footprint',
        lang_count: '8 Langs (No HI)',
        telephony_support: 'Unsupported',
        lang_hint: 'Hallucinates fictional Rs. 50k script',
        vram_kpi: '4.80 GB (NF4)'
    }
};

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', async () => {
    await loadSamples();
    setupMobileNav();
    setupModelSelectors();
    setupMasterTableClicks();
    setupViewModeSwitcher();
    setupAudioPlayer();
    setupTabs();
    initCharts();
    setupExportHandlers();
    setupBenchmarkSync();
});

// Load Samples Metadata
async function loadSamples() {
    try {
        const response = await fetch('/api/samples');
        if (response.ok) {
            samplesData = await response.json();
        }
    } catch (e) {
        console.warn('Using local fallback sample metadata', e);
    }

    if (!samplesData || samplesData.length === 0) {
        samplesData = [];
    }

    renderSampleSelector();
    displaySample(0);
}

// Mobile Responsive Navigation & Fast Switcher
function setupMobileNav() {
    const btnToggle = document.getElementById('btn-toggle-sidebar');
    const btnClose = document.getElementById('btn-close-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    const sidebar = document.querySelector('.sidebar');

    function openSidebar() {
        sidebar?.classList.add('open');
        backdrop?.classList.add('active');
        document.body.classList.add('sidebar-open-locked');
    }

    function closeSidebar() {
        sidebar?.classList.remove('open');
        backdrop?.classList.remove('active');
        document.body.classList.remove('sidebar-open-locked');
    }

    btnToggle?.addEventListener('click', openSidebar);
    btnClose?.addEventListener('click', closeSidebar);
    backdrop?.addEventListener('click', closeSidebar);

    // Setup mobile quick-model horizontal bar chips
    const mobileChips = document.querySelectorAll('.mobile-model-chip');
    mobileChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const modelKey = chip.getAttribute('data-model');
            if (modelKey) {
                selectModel(modelKey);
            }
        });
    });
}

// Model Selectors (Sidebar Items)
function setupModelSelectors() {
    const navItems = document.querySelectorAll('.model-nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const modelKey = item.getAttribute('data-model');
            if (modelKey) {
                selectModel(modelKey);
            }
        });
    });
}

// Master Table Row Selection
function setupMasterTableClicks() {
    const tableRows = document.querySelectorAll('.table-row-model');
    tableRows.forEach(row => {
        row.addEventListener('click', () => {
            const modelKey = row.getAttribute('data-model');
            if (modelKey) {
                selectModel(modelKey);
            }
        });
    });
}

function selectModel(modelKey) {
    if (!MODEL_SPECS[modelKey]) return;
    currentModel = modelKey;

    // 1. Update Sidebar Active State
    document.querySelectorAll('.model-nav-item').forEach(item => {
        if (item.getAttribute('data-model') === modelKey) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // 2. Update Master Table Active Row
    document.querySelectorAll('.table-row-model').forEach(row => {
        if (row.getAttribute('data-model') === modelKey) {
            row.classList.add('active-row');
        } else {
            row.classList.remove('active-row');
        }
    });

    // 3. Update Mobile Quick-Model Chips Active State
    document.querySelectorAll('.mobile-model-chip').forEach(chip => {
        if (chip.getAttribute('data-model') === modelKey) {
            chip.classList.add('active');
            chip.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        } else {
            chip.classList.remove('active');
        }
    });

    // 4. Auto-close mobile drawer if open
    const sidebar = document.querySelector('.sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    sidebar?.classList.remove('open');
    backdrop?.classList.remove('active');
    document.body.classList.remove('sidebar-open-locked');

    displaySample(currentSampleIndex);
}

// Transcript View Mode Switcher (Dialogue Turns vs Word Diff)
function setupViewModeSwitcher() {
    const btnDialogue = document.getElementById('btn-view-dialogue');
    const btnDiff = document.getElementById('btn-view-diff');

    if (btnDialogue) {
        btnDialogue.addEventListener('click', () => {
            setViewMode('dialogue');
        });
    }

    if (btnDiff) {
        btnDiff.addEventListener('click', () => {
            setViewMode('diff');
        });
    }
}

function setViewMode(mode) {
    currentViewMode = mode;
    const btnDialogue = document.getElementById('btn-view-dialogue');
    const btnDiff = document.getElementById('btn-view-diff');

    if (mode === 'dialogue') {
        btnDialogue?.classList.add('active');
        btnDiff?.classList.remove('active');
    } else {
        btnDiff?.classList.add('active');
        btnDialogue?.classList.remove('active');
    }

    renderTranscripts();
}

// Render Audio Sample Selector Pills
function renderSampleSelector() {
    const container = document.getElementById('sample-selector-container');
    if (!container) return;
    container.innerHTML = '';

    const labels = [
        "Sample 1: KOTAK (FULL 4m 50s)",
        "Sample 2: KOTAK (30s DISPUTE)",
        "Sample 3: BANKING (HDFC)",
        "Sample 4: TELECOM (AIRTEL)",
        "Sample 5: ECOMMERCE (AMAZON)"
    ];

    samplesData.forEach((sample, idx) => {
        const btn = document.createElement('button');
        btn.className = `btn-sample ${idx === 0 ? 'active' : ''}`;
        btn.innerText = labels[idx] || sample.title || `Sample ${idx + 1}`;
        btn.addEventListener('click', () => {
            document.querySelectorAll('.btn-sample').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            displaySample(idx);
        });
        container.appendChild(btn);
    });
}

// Display Sample Data & Metrics
function displaySample(idx) {
    currentSampleIndex = idx;
    const sample = samplesData[idx];
    if (!sample) return;

    const spec = MODEL_SPECS[currentModel] || MODEL_SPECS.bodhan;
    const modelData = sample.models?.[currentModel] || {};

    // 1. Breadcrumbs
    const crumbEl = document.getElementById('crumb-active-model');
    if (crumbEl) {
        crumbEl.innerText = `${spec.title} (${spec.params})`;
    }

    // 2. Hero Section
    const heroVendor = document.getElementById('hero-model-vendor');
    if (heroVendor) heroVendor.innerText = spec.vendor;

    const heroTitle = document.getElementById('hero-model-title');
    if (heroTitle) heroTitle.innerText = spec.title;

    const heroDesc = document.getElementById('hero-model-desc');
    if (heroDesc) heroDesc.innerText = spec.desc;

    const badgesContainer = document.getElementById('hero-badges-container');
    if (badgesContainer) {
        badgesContainer.innerHTML = `
            <span class="tag ${spec.verdict_badge.class}">${spec.verdict_badge.text}</span>
            <span class="tag">${spec.arch}</span>
            <span class="tag">${spec.params}</span>
            <span class="tag">${spec.vram}</span>
            <span class="tag">${spec.license}</span>
        `;
    }

    // 3. Audio Player Title & Context
    const titleEl = document.getElementById('current-audio-title');
    if (titleEl) titleEl.innerText = sample.title || sample.id;

    const scenarioEl = document.getElementById('current-audio-scenario');
    if (scenarioEl) scenarioEl.innerText = sample.scenario || "";

    // 4. Metric Scorecards (6 Focused Cards)
    // WER
    const werEl = document.getElementById('metric-wer');
    if (werEl) werEl.innerText = modelData.wer || spec.wer;
    const werSub = document.getElementById('metric-wer-sub');
    if (werSub) werSub.innerText = spec.wer_sub;
    const werHint = document.getElementById('metric-wer-hint');
    if (werHint) werHint.innerText = spec.wer_hint;

    // Accuracy
    const accEl = document.getElementById('metric-accuracy');
    if (accEl) accEl.innerText = modelData.accuracy || spec.accuracy;
    const accSub = document.getElementById('metric-acc-sub');
    if (accSub) accSub.innerText = spec.acc_sub;
    const accHint = document.getElementById('metric-acc-hint');
    if (accHint) accHint.innerText = modelData.coverage_hint || spec.acc_hint;

    // Latency & RTF
    const inferEl = document.getElementById('metric-infer-time');
    if (inferEl) inferEl.innerText = modelData.latency || spec.latency;
    const rtfPill = document.getElementById('metric-rtf-pill');
    if (rtfPill) rtfPill.innerText = modelData.rtf || spec.rtf;
    const latencyHint = document.getElementById('metric-latency-hint');
    if (latencyHint) latencyHint.innerText = modelData.latency_hint || spec.latency_hint;

    // Streaming
    const streamLat = document.getElementById('metric-stream-lat');
    if (streamLat) streamLat.innerText = modelData.streaming_latency || spec.streaming_lat;
    const streamMode = document.getElementById('metric-stream-mode');
    if (streamMode) streamMode.innerText = spec.streaming_mode;
    const streamHint = document.getElementById('metric-stream-hint');
    if (streamHint) streamHint.innerText = spec.streaming_hint;

    // Batching
    const batchThr = document.getElementById('metric-batch-thr');
    if (batchThr) batchThr.innerText = modelData.batch_throughput_bs32 || spec.batch_thr;
    const batchHint = document.getElementById('metric-batch-hint');
    if (batchHint) batchHint.innerText = spec.batch_hint;

    // Languages & Telephony
    const langCount = document.getElementById('metric-lang-count');
    if (langCount) langCount.innerText = spec.lang_count;
    const teleSupport = document.getElementById('metric-telephony-support');
    if (teleSupport) teleSupport.innerText = spec.telephony_support;
    const langHint = document.getElementById('metric-lang-hint');
    if (langHint) langHint.innerText = spec.lang_hint;

    // 5. Audio KPI Bar
    const durEl = document.getElementById('metric-duration');
    if (durEl) durEl.innerText = sample.duration || "290.16 s (4m 50s)";

    const vramEl = document.getElementById('metric-vram');
    if (vramEl) vramEl.innerText = modelData.vram || spec.vram_kpi;

    // 6. Audio Player Source
    const audioPlayer = document.getElementById('native-audio');
    if (audioPlayer) {
        const audioSrc = sample.audio_file || `/static/audio/${sample.id}.wav`;
        if (audioPlayer.src !== window.location.origin + audioSrc && !audioPlayer.src.endsWith(audioSrc)) {
            audioPlayer.src = audioSrc;
            audioPlayer.load();

            const iconPlay = document.querySelector('.icon-play');
            const iconPause = document.querySelector('.icon-pause');
            if (iconPlay) iconPlay.classList.remove('hidden');
            if (iconPause) iconPause.classList.add('hidden');

            const progressFill = document.getElementById('progress-fill');
            if (progressFill) progressFill.style.width = '0%';
        }
    }

    // 7. Update Prediction Badge Label
    const predBadgeLabel = document.getElementById('pred-badge-label');
    if (predBadgeLabel) {
        predBadgeLabel.innerText = `PREDICTED (${spec.title.toUpperCase()})`;
    }

    // 8. Render Transcripts
    renderTranscripts();
}

// Render Transcripts (Dialogue vs Diff)
function renderTranscripts() {
    const sample = samplesData[currentSampleIndex];
    if (!sample) return;

    const modelData = sample.models?.[currentModel] || {};

    const gtText = sample.ground_truth || "";
    const predText = modelData.predicted || sample.predicted || "";

    const gtDiarized = sample.ground_truth_diarized || "";
    const predDiarized = modelData.predicted_diarized || sample.predicted_diarized || "";

    const gtContainer = document.getElementById('gt-text-display');
    const predContainer = document.getElementById('pred-text-display');
    const gtWordCount = document.getElementById('gt-word-count');
    const predWordCount = document.getElementById('pred-word-count');

    // Update word count badges
    const gtWords = gtText.split(/\s+/).filter(w => w.length > 0);
    const predWords = predText.split(/\s+/).filter(w => w.length > 0);
    if (gtWordCount) gtWordCount.innerText = `${gtWords.length} words`;
    if (predWordCount) predWordCount.innerText = `${predWords.length} words`;

    if (currentViewMode === 'dialogue' && (gtDiarized || predDiarized)) {
        // Render Turn-by-Turn Dialogue
        const gtTurns = parseDiarizedText(gtDiarized);
        const predTurns = parseDiarizedText(predDiarized);

        renderDialogueTurns(gtContainer, gtTurns);
        renderDialogueTurns(predContainer, predTurns);
    } else {
        // Render Word-by-Word Diff View
        renderTranscriptDiff(gtContainer, predContainer, gtText, predText);
    }
}

// Parse Diarized Text: [MM:SS-MM:SS] Speaker : dialogue
function parseDiarizedText(rawText) {
    if (!rawText) return [];
    const lines = rawText.split('\n');
    const turns = [];
    const regex = /\[(\d{2}:\d{2})-(\d{2}:\d{2})\]\s*(Agent|Customer|Speaker\s*\d*)\s*:\s*(.*)/i;

    for (let rawLine of lines) {
        const line = rawLine.trim();
        if (!line || line.startsWith('#')) continue;

        const match = line.match(regex);
        if (match) {
            const startStr = match[1];
            const endStr = match[2];
            const speaker = match[3];
            const content = match[4];

            const [sm, ss] = startStr.split(':').map(Number);
            const [em, es] = endStr.split(':').map(Number);
            const startSec = sm * 60 + ss;
            const endSec = em * 60 + es;

            turns.push({
                startStr,
                endStr,
                startSec,
                endSec,
                speaker,
                text: content
            });
        } else {
            turns.push({
                startStr: '00:00',
                endStr: '00:00',
                startSec: 0,
                endSec: 0,
                speaker: 'Speaker',
                text: line
            });
        }
    }
    return turns;
}

// Render Dialogue Turns with Click-to-Play
function renderDialogueTurns(container, turns) {
    if (!container) return;
    if (!turns || turns.length === 0) {
        container.innerHTML = '<div style="padding: 20px; color: #94a3b8; text-align: center; font-size: 0.85rem;">No diarized transcript turns available for this sample.</div>';
        return;
    }

    let html = '<div class="dialogue-list">';
    turns.forEach((turn) => {
        const spkClass = turn.speaker.toLowerCase().includes('agent') ? 'agent' : 'customer';
        html += `
        <div class="dialogue-turn" data-start="${turn.startSec}" data-end="${turn.endSec}">
            <div class="turn-meta">
                <span class="turn-time" title="Click to jump audio to ${turn.startStr}">▶ ${turn.startStr} - ${turn.endStr}</span>
                <span class="speaker-pill ${spkClass}">${escapeHtml(turn.speaker)}</span>
            </div>
            <div class="turn-text">${escapeHtml(turn.text)}</div>
        </div>`;
    });
    html += '</div>';
    container.innerHTML = html;

    // Attach click events to jump audio
    container.querySelectorAll('.dialogue-turn').forEach(turnEl => {
        turnEl.addEventListener('click', () => {
            const startSec = parseFloat(turnEl.getAttribute('data-start'));
            const audioPlayer = document.getElementById('native-audio');
            if (audioPlayer && !isNaN(startSec)) {
                audioPlayer.currentTime = startSec;
                audioPlayer.play().then(() => {
                    document.querySelector('.icon-play')?.classList.add('hidden');
                    document.querySelector('.icon-pause')?.classList.remove('hidden');
                }).catch(e => console.warn(e));
            }
        });
    });
}

// Render Word-by-Word Diff View
function renderTranscriptDiff(gtContainer, predContainer, gt, pred) {
    const gtWords = gt.split(/\s+/).filter(w => w.length > 0);
    const predWords = pred.split(/\s+/).filter(w => w.length > 0);

    let gtHtml = '';
    let predHtml = '';
    const maxLen = Math.max(gtWords.length, predWords.length);

    for (let i = 0; i < maxLen; i++) {
        const gw = gtWords[i] || '';
        const pw = predWords[i] || '';

        if (gw.toLowerCase() === pw.toLowerCase()) {
            if (gw) gtHtml += `<span class="w-match">${escapeHtml(gw)}</span> `;
            if (pw) predHtml += `<span class="w-match">${escapeHtml(pw)}</span> `;
        } else {
            if (gw) gtHtml += `<span class="w-sub" title="Model transcribed as '${escapeHtml(pw)}'">${escapeHtml(gw)}</span> `;
            if (pw) predHtml += `<span class="w-sub" title="Reference audio speaks '${escapeHtml(gw)}'">${escapeHtml(pw)}</span> `;
        }
    }

    if (gtContainer) gtContainer.innerHTML = gtHtml.trim();
    if (predContainer) predContainer.innerHTML = predHtml.trim();
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Audio Player Controls & Real-Time Dialogue Highlighting
function setupAudioPlayer() {
    const audioPlayer = document.getElementById('native-audio');
    const playPauseBtn = document.getElementById('btn-play-pause');
    const iconPlay = document.querySelector('.icon-play');
    const iconPause = document.querySelector('.icon-pause');
    const audioCurrentTime = document.getElementById('audio-current-time');
    const audioTotalTime = document.getElementById('audio-total-time');
    const progressTrack = document.getElementById('progress-track');
    const progressFill = document.getElementById('progress-fill');

    if (!audioPlayer || !playPauseBtn) return;

    playPauseBtn.addEventListener('click', () => {
        if (audioPlayer.paused) {
            audioPlayer.play().then(() => {
                iconPlay?.classList.add('hidden');
                iconPause?.classList.remove('hidden');
            }).catch(e => console.warn('Audio play error:', e));
        } else {
            audioPlayer.pause();
            iconPlay?.classList.remove('hidden');
            iconPause?.classList.add('hidden');
        }
    });

    audioPlayer.addEventListener('timeupdate', () => {
        const cur = audioPlayer.currentTime;
        const dur = audioPlayer.duration || 1;
        const pct = (cur / dur) * 100;
        if (progressFill) progressFill.style.width = `${pct}%`;
        if (audioCurrentTime) audioCurrentTime.innerText = formatTime(cur);

        // Highlight matching dialogue turn
        if (currentViewMode === 'dialogue') {
            document.querySelectorAll('.dialogue-turn').forEach(turnEl => {
                const s = parseFloat(turnEl.getAttribute('data-start'));
                const e = parseFloat(turnEl.getAttribute('data-end'));
                if (cur >= s && cur < (e || s + 3)) {
                    if (!turnEl.classList.contains('active')) {
                        turnEl.classList.add('active');
                    }
                } else {
                    turnEl.classList.remove('active');
                }
            });
        }
    });

    audioPlayer.addEventListener('loadedmetadata', () => {
        if (audioTotalTime) audioTotalTime.innerText = formatTime(audioPlayer.duration);
    });

    audioPlayer.addEventListener('ended', () => {
        iconPlay?.classList.remove('hidden');
        iconPause?.classList.add('hidden');
        if (progressFill) progressFill.style.width = '0%';
        document.querySelectorAll('.dialogue-turn').forEach(el => el.classList.remove('active'));
    });

    if (progressTrack) {
        const handleSeek = (e) => {
            const rect = progressTrack.getBoundingClientRect();
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clickPos = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
            audioPlayer.currentTime = clickPos * (audioPlayer.duration || 1);
        };
        progressTrack.addEventListener('click', handleSeek);
        progressTrack.addEventListener('touchstart', handleSeek, { passive: true });
        progressTrack.addEventListener('touchmove', handleSeek, { passive: true });
    }
}

function formatTime(sec) {
    if (isNaN(sec) || sec === Infinity) return "00:00";
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

// Colab Benchmark Synchronization
function setupBenchmarkSync() {
    const btnSync = document.getElementById('btn-sync-benchmark');
    if (btnSync) {
        btnSync.addEventListener('click', async () => {
            btnSync.innerText = '⏳ Checking...';
            const synced = await checkLatestColabBenchmark(true);
            setTimeout(() => {
                btnSync.innerText = synced ? '✅ Colab Synced' : '⚡ Sync Colab';
            }, 1200);
        });
    }

    // Auto-check once silently on load
    checkLatestColabBenchmark(false);
}

async function checkLatestColabBenchmark(showAlert = false) {
    try {
        const res = await fetch('/api/benchmark/latest');
        if (res.ok) {
            const result = await res.json();
            if (result.found && result.data) {
                const b = result.data;
                // Merge into sample 0 (Kotak Full Call) Bodhan model
                if (samplesData && samplesData[0] && samplesData[0].models?.bodhan) {
                    const m = samplesData[0].models.bodhan;
                    if (b.wer !== undefined) m.wer = `${parseFloat(b.wer).toFixed(1)}%`;
                    if (b.cer !== undefined) m.cer = `${parseFloat(b.cer).toFixed(1)}%`;
                    if (b.accuracy !== undefined) m.accuracy = `${parseFloat(b.accuracy).toFixed(1)}%`;
                    if (b.word_coverage_pct !== undefined) m.coverage = `${parseFloat(b.word_coverage_pct).toFixed(1)}%`;
                    if (b.rtf !== undefined) m.rtf = `${parseFloat(b.rtf).toFixed(3)}x`;
                    if (b.infer_time_sec !== undefined) m.latency = `${parseFloat(b.infer_time_sec).toFixed(1)} s`;
                    if (b.peak_vram_gb !== undefined) m.vram = `${parseFloat(b.peak_vram_gb).toFixed(1)} GB`;

                    if (currentSampleIndex === 0) {
                        displaySample(0);
                    }
                }

                if (showAlert) {
                    alert(`✅ Benchmark Synced Successfully!\n\n• Audio Duration: ${b.audio_duration_sec}s\n• Inference Time: ${b.infer_time_sec}s\n• RTF: ${b.rtf}x\n• Word Coverage: ${b.word_coverage_pct}%\n• WER: ${b.wer}%\n• GPU VRAM: ${b.peak_vram_gb} GB`);
                }
                return true;
            }
        }
    } catch (e) {
        console.warn('Colab benchmark check note:', e);
    }
    if (showAlert) {
        alert("ℹ️ No new 'bodhan_benchmark_results.json' file found in Downloads yet.\nOnce you run the benchmark cell in Colab, download the JSON and click this button to sync!");
    }
    return false;
}

// Deep Dive Tabs
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab');
            const targetPane = document.getElementById(targetId);
            if (targetPane) targetPane.classList.add('active');

            setTimeout(() => {
                Object.values(charts).forEach(c => {
                    if (c && typeof c.resize === 'function') c.resize();
                });
            }, 50);
        });
    });
}

// Minimalist Light Charts Initialization
function initCharts() {
    const fontConfig = {
        family: "'Plus Jakarta Sans', -apple-system, sans-serif",
        size: 11
    };
    const gridColor = '#f1f5f9';
    const textColor = '#64748b';

    // 1. Streaming Latency Comparison (Bar Chart)
    const ctxStreaming = document.getElementById('chart-streaming-latency')?.getContext('2d');
    if (ctxStreaming) {
        charts.streaming = new Chart(ctxStreaming, {
            type: 'bar',
            data: {
                labels: [
                    'Nemotron (80ms)',
                    'Sarvam Saarika (400ms)',
                    'Gemini Flash (1200ms)',
                    'Bodhan Core (1500ms)',
                    'Whisper Turbo (3000ms)'
                ],
                datasets: [
                    {
                        label: 'Streaming Latency (ms)',
                        data: [80, 400, 1200, 1500, 3000],
                        backgroundColor: [
                            '#d97706', // Nemotron (amber)
                            '#0284c7', // Sarvam (blue)
                            '#8b5cf6', // Gemini (purple)
                            '#10b981', // Bodhan (green)
                            '#ea580c'  // Whisper (orange)
                        ],
                        borderRadius: 4,
                        barPercentage: 0.6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { drawOnChartArea: false },
                        ticks: { color: '#0f172a', font: fontConfig }
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: { color: textColor, font: fontConfig },
                        title: { display: true, text: 'Lookahead Latency (ms)', color: textColor, font: fontConfig }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // 2. Batching & Throughput Scaling (Line Chart)
    const ctxBatching = document.getElementById('chart-batching-throughput')?.getContext('2d');
    if (ctxBatching) {
        charts.batching = new Chart(ctxBatching, {
            type: 'line',
            data: {
                labels: ['BS = 1', 'BS = 4', 'BS = 8', 'BS = 16', 'BS = 32 (Optimal)', 'BS = 64'],
                datasets: [
                    {
                        label: 'Bodhan 1.2B (Throughput hrs/hr)',
                        data: [6.9, 26.0, 48.5, 82.0, 120.0, 138.0],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.08)',
                        fill: true,
                        borderWidth: 2,
                        tension: 0.3,
                        pointBackgroundColor: '#10b981',
                        pointRadius: 4
                    },
                    {
                        label: 'Nemotron 600M (Throughput hrs/hr)',
                        data: [36.0, 125.0, 185.0, 295.0, 410.0, 460.0],
                        borderColor: '#d97706',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        borderDash: [4, 4],
                        tension: 0.3,
                        pointBackgroundColor: '#d97706',
                        pointRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: textColor, font: fontConfig }
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: { color: textColor, font: fontConfig },
                        title: { display: true, text: 'Audio Throughput (hrs / hr)', color: textColor, font: fontConfig }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#0f172a', font: fontConfig, boxWidth: 12, usePointStyle: true }
                    }
                }
            }
        });
    }
}

// Export and Download Handlers
function setupExportHandlers() {
    document.getElementById('btn-export-json')?.addEventListener('click', () => {
        const currentData = samplesData[currentSampleIndex] || samplesData[0];
        const spec = MODEL_SPECS[currentModel] || MODEL_SPECS.bodhan;

        const exportObj = {
            platform: "pragyaa.ai",
            active_model: {
                id: spec.id,
                title: spec.title,
                vendor: spec.vendor,
                architecture: spec.arch,
                params: spec.params
            },
            inference_hardware: "Tesla T4 GPU (FP16)",
            timestamp: new Date().toISOString(),
            metrics_summary: {
                wer: spec.wer,
                accuracy: spec.accuracy,
                latency: spec.latency,
                rtf: spec.rtf,
                streaming_latency: spec.streaming_lat,
                batch_throughput_bs32: spec.batch_thr,
                supported_languages: spec.lang_count,
                telephony_narrowband: spec.telephony_support
            },
            active_sample: {
                id: currentData.id,
                title: currentData.title,
                domain: currentData.domain,
                duration: currentData.duration
            }
        };

        const blob = new Blob([JSON.stringify(exportObj, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pragyaa_benchmark_${currentModel}_${currentData.id}.json`;
        a.click();
        URL.revokeObjectURL(url);
    });
}
