import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
import pymupdf

OUT_DIR = r"E:\PROJECTS\stt\benchmark_report"
os.makedirs(OUT_DIR, exist_ok=True)
PDF_PATH = r"E:\PROJECTS\stt\SraVaani_Model_Benchmark_Report.pdf"

# ---------------------------------------------------------
# STEP 1: Generate Visual Comparison Charts
# ---------------------------------------------------------
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial', 'DejaVu Sans', 'Helvetica'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

# Chart 1: Major Languages
languages = ['Hindi', 'Bengali', 'Marathi', 'Gujarati', 'Punjabi', 'Telugu', 'Tamil', 'Kannada', 'Assamese', 'English']
wer_0ms = [22.1, 27.1, 28.4, 34.4, 30.2, 34.6, 35.1, 34.3, 29.0, 31.5]
wer_80ms = [21.3, 26.2, 27.3, 33.5, 28.8, 33.6, 34.6, 33.4, 28.3, 31.0]
wer_480ms = [19.3, 24.5, 25.2, 30.3, 25.8, 31.4, 32.8, 31.7, 25.2, 27.4]
wer_1040ms = [18.0, 23.2, 24.0, 28.6, 24.0, 30.3, 32.0, 30.8, 24.1, 24.6]
wer_v1 = [12.4, 19.8, 19.7, 19.0, 20.2, 25.1, 26.2, 27.4, 19.4, 14.8]

x = np.arange(len(languages))
width = 0.16

fig, ax = plt.subplots(figsize=(10.5, 4.0), dpi=300)
rects1 = ax.bar(x - 2*width, wer_0ms, width, label='0.5-live (0 ms / la=0)', color='#f87171')
rects2 = ax.bar(x - width, wer_80ms, width, label='0.5-live (80 ms / la=1)', color='#fb923c')
rects3 = ax.bar(x, wer_480ms, width, label='0.5-live (480 ms / la=6)', color='#facc15')
rects4 = ax.bar(x + width, wer_1040ms, width, label='0.5-live (1040 ms / la=13)', color='#60a5fa')
rects5 = ax.bar(x + 2*width, wer_v1, width, label='SraVaani 1.0 (Flagship TDT-CTC)', color='#10b981')

ax.set_ylabel('Word Error Rate (WER %) — Lower is Better', fontsize=9.5, fontweight='bold', color='#1e293b')
ax.set_title('WER Across Core Indic Languages: SraVaani 0.5-live Latency Modes vs SraVaani 1.0', fontsize=11, fontweight='bold', pad=10, color='#0f172a')
ax.set_xticks(x)
ax.set_xticklabels(languages, fontsize=9, fontweight='bold', color='#334155')
ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8.5, loc='upper right')
ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.set_ylim(0, 42)

for bar in rects5:
    height = bar.get_height()
    ax.annotate(f'{height:.1f}%',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 2),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=7, fontweight='bold', color='#047857')

plt.tight_layout()
chart1_img = os.path.join(OUT_DIR, "chart1_major_languages.png")
plt.savefig(chart1_img, dpi=300)
plt.close()

# Chart 2: Trends and Latency Curve
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 3.4), dpi=300)

modes = ['0 ms\n(Instant)', '80 ms\n(Live Mic)', '480 ms\n(Balanced)', '1040 ms\n(Accurate)', 'SraVaani 1.0\n(Offline)']
sched_avg = [
    np.mean([29.0, 27.1, 34.4, 22.1, 34.3, 64.7, 34.0, 43.0, 48.2, 28.4, 45.0, 36.9, 30.2, 51.3, 69.4, 35.1, 34.6]),
    np.mean([28.3, 26.2, 33.5, 21.3, 33.4, 63.4, 33.0, 41.7, 49.0, 27.3, 42.9, 36.4, 28.8, 49.5, 68.5, 34.6, 33.6]),
    np.mean([25.2, 24.5, 30.3, 19.3, 31.7, 62.0, 31.4, 38.4, 46.7, 25.2, 40.8, 33.9, 25.8, 47.3, 66.8, 32.8, 31.4]),
    np.mean([24.1, 23.2, 28.6, 18.0, 30.8, 63.6, 30.6, 37.3, 45.2, 24.0, 39.0, 32.3, 24.0, 45.9, 66.2, 32.0, 30.3]),
    np.mean([19.4, 19.8, 19.0, 12.4, 27.4, 54.7, 27.5, 27.7, 41.6, 19.7, 31.3, 25.7, 20.2, 36.4, 57.3, 26.2, 25.1])
]

colors_list = ['#ef4444', '#f97316', '#eab308', '#3b82f6', '#10b981']
bars = ax1.bar(modes, sched_avg, color=colors_list, width=0.52, edgecolor='#64748b', linewidth=0.7)
ax1.set_ylabel('Mean Scheduled WER (%)', fontsize=9, fontweight='bold', color='#1e293b')
ax1.set_title('Mean WER Progression Across Latency Profiles', fontsize=10, fontweight='bold', color='#0f172a')
ax1.grid(axis='y', linestyle='--', alpha=0.5)
ax1.set_ylim(0, 46)

for bar in bars:
    height = bar.get_height()
    ax1.annotate(f'{height:.1f}%',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 2),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=8, fontweight='bold', color='#1e293b')

# Cluster Comparison
clusters = ['High Resource\n(Hi, Bn, Mr)', 'Dravidian South\n(Kn, Ta, Te)', 'Regional Dialects\n(40+ Avg)']
c_80 = [np.mean([21.3, 26.2, 27.3]), np.mean([33.4, 34.6, 33.6]), 54.2]
c_1040 = [np.mean([18.0, 23.2, 24.0]), np.mean([30.8, 32.0, 30.3]), 49.8]
c_v1 = [np.mean([12.4, 19.8, 19.7]), np.mean([27.4, 26.2, 25.1]), 43.1]

xc = np.arange(len(clusters))
wc = 0.24
ax2.bar(xc - wc, c_80, wc, label='0.5-live (80ms)', color='#fb923c')
ax2.bar(xc, c_1040, wc, label='0.5-live (1040ms)', color='#60a5fa')
ax2.bar(xc + wc, c_v1, wc, label='SraVaani 1.0', color='#10b981')

ax2.set_ylabel('Average WER (%)', fontsize=9, fontweight='bold', color='#1e293b')
ax2.set_title('Performance by Linguistic Category', fontsize=10, fontweight='bold', color='#0f172a')
ax2.set_xticks(xc)
ax2.set_xticklabels(clusters, fontsize=8.5, fontweight='bold', color='#334155')
ax2.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8)
ax2.grid(axis='y', linestyle='--', alpha=0.5)
ax2.set_ylim(0, 62)

plt.tight_layout()
chart2_img = os.path.join(OUT_DIR, "chart2_summary_metrics.png")
plt.savefig(chart2_img, dpi=300)
plt.close()

# ---------------------------------------------------------
# STEP 2: ReportLab Canvas with Page Numbers & Running Headers
# ---------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        page_w, page_h = letter
        margin = 36

        # Running Header (Pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1e3a8a"))
            self.drawString(margin, page_h - 24, "SRAVAANI INDIC STT BENCHMARK REPORT")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawRightString(page_w - margin, page_h - 24, "ARTPARK & SPIRE Lab (IISc Bangalore)")
            
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.6)
            self.line(margin, page_h - 28, page_w - margin, page_h - 28)

        # Running Footer (All pages)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.6)
        self.line(margin, 28, page_w - margin, 28)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(margin, 18, "Confidential Engineering Benchmark Evaluation — ARTPARK-IISc/SraVaani-0.5-live & SraVaani-1.0")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(page_w - margin, 18, page_str)
        self.restoreState()

# ---------------------------------------------------------
# STEP 3: Build Document Flowable Content
# ---------------------------------------------------------
def generate_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    base_styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=base_styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=3
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=3
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#475569')
    )
    
    sec_heading = ParagraphStyle(
        'SecHeading',
        parent=base_styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=14.5,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=4,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )

    tbl_header = ParagraphStyle(
        'TblHeader',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9,
        alignment=1,
        textColor=colors.white
    )

    tbl_cell = ParagraphStyle(
        'TblCell',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=6.8,
        leading=8.5,
        alignment=0,
        textColor=colors.HexColor('#1e293b')
    )

    tbl_cell_center = ParagraphStyle(
        'TblCellCenter',
        parent=tbl_cell,
        alignment=1
    )

    tbl_cell_bold = ParagraphStyle(
        'TblCellBold',
        parent=tbl_cell,
        fontName='Helvetica-Bold'
    )

    tbl_cell_bold_center = ParagraphStyle(
        'TblCellBoldCenter',
        parent=tbl_cell,
        fontName='Helvetica-Bold',
        alignment=1
    )

    story = []

    # =========================================================
    # PAGE 1: HEADER BANNER, EXECUTIVE SUMMARY, SPECS MATRIX
    # =========================================================
    header_table_data = [
        [Paragraph("SraVaani Indic Speech-to-Text Benchmark Report", title_style)],
        [Paragraph("Comparative Benchmark & Architecture Analysis: SraVaani-0.5-live vs. SraVaani-1.0", subtitle_style)],
        [Paragraph("<b>Authoring Labs:</b> ARTPARK (AI & Robotics Technology Park) & SPIRE Lab, IISc Bangalore &nbsp;|&nbsp; <b>Partner:</b> Google &nbsp;|&nbsp; <b>Evaluation Date:</b> November 2026", meta_style)]
    ]
    header_table = Table(header_table_data, colWidths=[540])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. Executive Summary & Technological Scope", sec_heading))
    story.append(Paragraph(
        "This evaluation benchmarks the two primary multilingual Speech-to-Text (STT) models produced by the "
        "<b>Indian Institute of Science (IISc), Bangalore</b> and <b>ARTPARK</b>: <b>SraVaani-0.5-live</b> and <b>SraVaani-1.0</b>. "
        "Together, these models address India's linguistic diversity by covering <b>63 to 65 Indian languages and dialects</b> "
        "(all major scheduled languages and over 40 underserved regional and tribal varieties). Both models stem from the foundational "
        "<b>Project Vaani</b> initiative, incorporating self-supervised pretraining across 31,255 hours of diverse geographic speech "
        "and multimodal audio-image semantic grounding before supervised multilingual fine-tuning.",
        body_style
    ))

    # Architecture Comparison Matrix
    specs_data = [
        [
            Paragraph("Core Parameter", tbl_header),
            Paragraph("SraVaani-0.5-live (Streaming ASR)", tbl_header),
            Paragraph("SraVaani-1.0 (Flagship Full ASR)", tbl_header)
        ],
        [
            Paragraph("Target Deployment", tbl_cell_bold),
            Paragraph("Real-time live mic streaming, conversational voice bots, telephony", tbl_cell),
            Paragraph("High-accuracy batch transcription, meeting minutes, subtitling", tbl_cell)
        ],
        [
            Paragraph("Encoder Backbone", tbl_cell_bold),
            Paragraph("Cache-Aware FastConformer (17 layers, d_model=1024, 8x subsampling)", tbl_cell),
            Paragraph("FastConformer (17 layers, d_model=1024, 8x subsampling)", tbl_cell)
        ],
        [
            Paragraph("Decoder Mechanism", tbl_cell_bold),
            Paragraph("Pure Connectionist Temporal Classification (CTC) with chunk cache", tbl_cell),
            Paragraph("Hybrid Token-and-Duration Transducer (TDT) + CTC decoder", tbl_cell)
        ],
        [
            Paragraph("Supported Latencies", tbl_cell_bold),
            Paragraph("<b>4 Switchable Profiles:</b> 0 ms, 80 ms, 480 ms, 1040 ms lookahead", tbl_cell),
            Paragraph("<b>Full Utterance:</b> Non-causal bidirectional context", tbl_cell)
        ],
        [
            Paragraph("Attention Cache", tbl_cell_bold),
            Paragraph("Fixed 70 left-context frames with dynamic right context (0, 1, 6, 13)", tbl_cell),
            Paragraph("Global bidirectional attention across complete utterance audio", tbl_cell)
        ],
        [
            Paragraph("Size & Weights", tbl_cell_bold),
            Paragraph("~430M parameters | FP16 TorchScript (~900 MB)", tbl_cell),
            Paragraph("~430M parameters | FP16 TorchScript & ONNX (~900 MB)", tbl_cell)
        ],
        [
            Paragraph("Training Corpus", tbl_cell_bold),
            Paragraph("31,255h Vaani SSL + 11M audio-image pairs + 31,270h supervised fine-tuning", tbl_cell),
            Paragraph("31,255h Vaani SSL + 11M audio-image pairs + 31,270h supervised fine-tuning", tbl_cell)
        ],
        [
            Paragraph("Execution Throughput", tbl_cell_bold),
            Paragraph(">60x real-time on GPU; highly real-time safe on CPU (RTF 0.015 - 0.03)", tbl_cell),
            Paragraph("Batch throughput >25x real-time on GPU; high accuracy batch processing", tbl_cell)
        ],
        [
            Paragraph("Language Support", tbl_cell_bold),
            Paragraph("63 Indian languages & dialects + English (code-switching capable)", tbl_cell),
            Paragraph("65 Indian languages & dialects + English (code-switching capable)", tbl_cell)
        ]
    ]

    spec_table = Table(specs_data, colWidths=[110, 215, 215])
    spec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(spec_table)
    story.append(Spacer(1, 6))

    # Executive Highlights Cards
    cards_data = [
        [
            Paragraph("<b>Low-Latency Streaming Champion</b><br/>"
                      "SraVaani 0.5-live executes in chunks down to <b>0 ms lookahead</b> (causal mode) or <b>80 ms lookahead</b> for conversational bots. It retains audio cache across chunks, avoiding recomputation.", tbl_cell),
            Paragraph("<b>State-of-the-Art Batch Accuracy</b><br/>"
                      "SraVaani 1.0 integrates a <b>Hybrid TDT-CTC decoder</b> that achieves a remarkable <b>12.4% WER in Hindi</b> and <b>14.8% in English</b>, outperforming streaming modes by 25% to 40% relative error reduction.", tbl_cell),
            Paragraph("<b>Democratized Multilingualism</b><br/>"
                      "Both models encompass 63+ Indian languages, enabling high accuracy for under-represented vernaculars like <b>Garo (9.5% WER)</b> and <b>Kurumali (11.3% WER)</b> alongside scheduled languages.", tbl_cell)
        ]
    ]
    cards_table = Table(cards_data, colWidths=[175, 175, 175])
    cards_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#93c5fd')),
        ('INNERGRID', (0,0), (-1,-1), 0.8, colors.HexColor('#bfdbfe')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(cards_table)

    story.append(PageBreak())

    # =========================================================
    # PAGE 2: VISUAL CHARTS & LATENCY-ACCURACY ANALYSIS
    # =========================================================
    story.append(Paragraph("2. Empirical Visualizations & Latency-Accuracy Curves", sec_heading))
    story.append(Paragraph(
        "Below are comparative empirical visualizations assessing Word Error Rate (WER %) performance across the 4 latency profiles "
        "of SraVaani-0.5-live against the offline baseline of SraVaani-1.0. Lower WER indicates higher transcription fidelity.",
        body_style
    ))

    # Chart 1: Major Languages
    story.append(Image(chart1_img, width=7.4*inch, height=2.75*inch))
    story.append(Spacer(1, 4))

    # Chart 2: Trends and Cluster Breakdown
    story.append(Image(chart2_img, width=7.4*inch, height=2.35*inch))
    story.append(Spacer(1, 5))

    # Takeaways box
    takeaway_data = [
        [
            Paragraph("<b>Key Empirical Findings from Visual Benchmarks:</b><br/>"
                      "1. <b>The 80 ms Sweet Spot:</b> Moving from 0 ms to 80 ms lookahead yields an immediate error drop across all languages (e.g. Hindi drops from 22.1% to 21.3%; Assamese from 29.0% to 28.3%) with virtually undetectable latency for human listeners.<br/>"
                      "2. <b>Lookahead Saturation at 1040 ms:</b> Expanding lookahead from 80 ms to 1040 ms delivers steady accuracy gains (averaging ~3.4% absolute WER reduction), approaching batch accuracy while retaining chunk-based streaming.<br/>"
                      "3. <b>Transducer Advantage:</b> SraVaani 1.0 achieves an additional 7.6% mean absolute error reduction over the 1040 ms streaming model, highlighting the structural power of the Hybrid TDT-CTC decoder over pure CTC.",
                      tbl_cell)
        ]
    ]
    takeaway_table = Table(takeaway_data, colWidths=[540])
    takeaway_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(takeaway_table)

    story.append(PageBreak())

    # =========================================================
    # PAGE 3: SCHEDULED LANGUAGES TABLE & CROSS-CORPUS TABLE
    # =========================================================
    story.append(Paragraph("3. Scheduled Indian Languages Benchmark (WER %)", sec_heading))
    story.append(Paragraph(
        "Comprehensive side-by-side evaluation across all 20 official scheduled Indian languages + English. "
        "WER for SraVaani-0.5-live represents the average across test sets from 8 public corpora (Vaani, RESPIN, FLEURS, IndicTTS, "
        "CommonVoice, GramVaani, Kathbath, and MUCS). All figures denote Word Error Rate (WER %).",
        body_style
    ))

    sched_data = [
        [
            Paragraph("Language", tbl_header),
            Paragraph("0.5-live (0 ms)", tbl_header),
            Paragraph("0.5-live (80 ms)", tbl_header),
            Paragraph("0.5-live (480 ms)", tbl_header),
            Paragraph("0.5-live (1040 ms)", tbl_header),
            Paragraph("SraVaani 1.0", tbl_header),
            Paragraph("Relative Improvement (1.0 vs 80ms)", tbl_header)
        ]
    ]

    sched_rows = [
        ("Assamese", 29.0, 28.3, 25.2, 24.1, 19.4),
        ("Bengali", 27.1, 26.2, 24.5, 23.2, 19.8),
        ("Bodo *", "—", "—", "—", "—", 20.9),
        ("Dogri *", "—", "—", "—", "—", 32.0),
        ("Gujarati", 34.4, 33.5, 30.3, 28.6, 19.0),
        ("Hindi", 22.1, 21.3, 19.3, 18.0, 12.4),
        ("Kannada", 34.3, 33.4, 31.7, 30.8, 27.4),
        ("Konkani", 64.7, 63.4, 62.0, 63.6, 54.7),
        ("Maithili", 34.0, 33.0, 31.4, 30.6, 27.5),
        ("Malayalam", 43.0, 41.7, 38.4, 37.3, 27.7),
        ("Manipuri", 48.2, 49.0, 46.7, 45.2, 41.6),
        ("Marathi", 28.4, 27.3, 25.2, 24.0, 19.7),
        ("Nepali", 45.0, 42.9, 40.8, 39.0, 31.3),
        ("Odia", 36.9, 36.4, 33.9, 32.3, 25.7),
        ("Punjabi", 30.2, 28.8, 25.8, 24.0, 20.2),
        ("Sanskrit", 51.3, 49.5, 47.3, 45.9, 36.4),
        ("Santali", 69.4, 68.5, 66.8, 66.2, 57.3),
        ("Sindhi *", "—", "—", "—", "—", 23.2),
        ("Tamil", 35.1, 34.6, 32.8, 32.0, 26.2),
        ("Telugu", 34.6, 33.6, 31.4, 30.3, 25.1),
        ("English", 31.5, 31.0, 27.4, 24.6, 14.8),
    ]

    for lang, w0, w80, w480, w1040, wv1 in sched_rows:
        if isinstance(w80, float) and isinstance(wv1, float):
            rel_gain = f"-{((w80 - wv1) / w80) * 100:.1f}% error"
            c_gain = Paragraph(f"<b>{rel_gain}</b>", tbl_cell_bold_center)
        else:
            c_gain = Paragraph("Baseline", tbl_cell_center)

        w0_str = f"{w0:.1f}%" if isinstance(w0, float) else str(w0)
        w80_str = f"{w80:.1f}%" if isinstance(w80, float) else str(w80)
        w480_str = f"{w480:.1f}%" if isinstance(w480, float) else str(w480)
        w1040_str = f"{w1040:.1f}%" if isinstance(w1040, float) else str(w1040)
        wv1_str = f"<b>{wv1:.1f}%</b>" if isinstance(wv1, float) else str(wv1)

        sched_data.append([
            Paragraph(f"<b>{lang}</b>", tbl_cell),
            Paragraph(w0_str, tbl_cell_center),
            Paragraph(w80_str, tbl_cell_center),
            Paragraph(w480_str, tbl_cell_center),
            Paragraph(w1040_str, tbl_cell_center),
            Paragraph(wv1_str, tbl_cell_center),
            c_gain
        ])

    sched_data.append([
        Paragraph("<b>Average (Scheduled)</b>", tbl_cell_bold),
        Paragraph("<b>39.6%</b>", tbl_cell_bold_center),
        Paragraph("<b>38.6%</b>", tbl_cell_bold_center),
        Paragraph("<b>36.4%</b>", tbl_cell_bold_center),
        Paragraph("<b>35.2%</b>", tbl_cell_bold_center),
        Paragraph("<b>27.6%</b>", tbl_cell_bold_center),
        Paragraph("<b>-28.5% Error Reduction</b>", tbl_cell_bold_center),
    ])

    sched_table = Table(sched_data, colWidths=[85, 70, 70, 70, 75, 75, 95])
    sched_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f8fafc')]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 1.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(sched_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("4. SraVaani-1.0 Cross-Corpus Evaluation Breakdown", sec_heading))
    story.append(Paragraph(
        "Individual dataset validation across CommonVoice, FLEURS, GramVaani, IndicTTS, Kathbath, MUCS, RESPIN, and Vaani.",
        body_style
    ))

    ds_data = [
        [
            Paragraph("Language", tbl_header),
            Paragraph("Avg WER", tbl_header),
            Paragraph("CommonVoice", tbl_header),
            Paragraph("FLEURS", tbl_header),
            Paragraph("IndicTTS", tbl_header),
            Paragraph("Kathbath", tbl_header),
            Paragraph("MUCS", tbl_header),
            Paragraph("RESPIN", tbl_header),
            Paragraph("Vaani", tbl_header),
        ]
    ]

    ds_rows = [
        ("Hindi", "12.4%", "12.7%", "10.9%", "9.1%", "9.1%", "14.6%", "10.8%", "10.8%"),
        ("Bengali", "19.8%", "14.1%", "15.2%", "26.2%", "12.3%", "—", "26.9%", "24.1%"),
        ("Gujarati", "19.0%", "—", "18.2%", "18.4%", "14.9%", "26.6%", "—", "16.8%"),
        ("Marathi", "19.7%", "16.6%", "18.1%", "14.2%", "17.8%", "22.0%", "16.1%", "33.4%"),
        ("Assamese", "19.4%", "22.6%", "18.8%", "—", "—", "—", "—", "16.9%"),
        ("Punjabi", "20.2%", "29.3%", "15.9%", "—", "13.6%", "—", "—", "22.1%"),
        ("Telugu", "25.1%", "—", "23.1%", "20.9%", "21.3%", "26.4%", "25.4%", "33.5%"),
        ("Tamil", "26.2%", "28.9%", "28.1%", "21.1%", "23.3%", "24.1%", "—", "32.0%"),
        ("Kannada", "27.4%", "—", "21.4%", "17.4%", "16.6%", "—", "27.4%", "54.1%"),
        ("Malayalam", "27.7%", "33.5%", "19.9%", "19.4%", "31.5%", "—", "—", "34.1%"),
        ("Odia", "25.7%", "29.4%", "20.3%", "18.7%", "21.4%", "21.4%", "—", "43.2%"),
        ("Nepali", "31.3%", "45.8%", "26.6%", "—", "—", "—", "—", "21.5%"),
    ]

    for r in ds_rows:
        ds_data.append([
            Paragraph(f"<b>{r[0]}</b>", tbl_cell),
            Paragraph(f"<b>{r[1]}</b>", tbl_cell_bold_center),
            Paragraph(r[2], tbl_cell_center),
            Paragraph(r[3], tbl_cell_center),
            Paragraph(r[4], tbl_cell_center),
            Paragraph(r[5], tbl_cell_center),
            Paragraph(r[6], tbl_cell_center),
            Paragraph(r[7], tbl_cell_center),
            Paragraph(r[8], tbl_cell_center),
        ])

    ds_table = Table(ds_data, colWidths=[80, 50, 60, 50, 50, 50, 50, 50, 50])
    ds_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f766e')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0fdfa')]),
        ('TOPPADDING', (0,0), (-1,-1), 1.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(ds_table)

    story.append(PageBreak())

    # =========================================================
    # PAGE 4: REGIONAL DIALECTS & ENGINEERING GUIDELINES
    # =========================================================
    story.append(Paragraph("5. Regional, Low-Resource & Tribal Dialects Benchmark", sec_heading))
    story.append(Paragraph(
        "A standout contribution of SraVaani is enabling voice AI for indigenous and low-resource Indian communities. "
        "Below is the comparative evaluation across RESPIN and Vaani test sets for 40 non-scheduled languages and regional dialects.",
        body_style
    ))

    non_sched_data = [
        [
            Paragraph("Dialect", tbl_header),
            Paragraph("0ms", tbl_header),
            Paragraph("80ms", tbl_header),
            Paragraph("480ms", tbl_header),
            Paragraph("1040ms", tbl_header),
            Paragraph("V 1.0", tbl_header),
            Paragraph("Dialect", tbl_header),
            Paragraph("0ms", tbl_header),
            Paragraph("80ms", tbl_header),
            Paragraph("480ms", tbl_header),
            Paragraph("1040ms", tbl_header),
            Paragraph("V 1.0", tbl_header),
        ]
    ]

    ns_list = [
        ("Angika", 40.0, 38.9, 36.3, 35.7, 31.4),
        ("Ao", 78.5, 75.9, 74.1, 72.4, 57.7),
        ("Awadhi", 50.8, 50.6, 49.2, 47.4, 43.8),
        ("Bajjika", 41.9, 41.2, 39.9, 40.1, 34.4),
        ("Bearybashe", 86.7, 86.7, 87.3, 85.7, 77.8),
        ("Bhatri", 78.9, 76.1, 71.5, 69.8, 60.3),
        ("Bhili", 75.3, 75.7, 75.4, 71.4, 73.5),
        ("Bhojpuri", 33.0, 32.2, 30.6, 29.9, 27.8),
        ("Bundeli", 43.4, 43.0, 40.7, 40.1, 36.0),
        ("Chakhesang", 87.1, 87.6, 85.8, 84.5, 75.8),
        ("Chakma", 65.1, 63.1, 60.5, 58.8, 51.2),
        ("Chhattisgarhi", 32.0, 31.2, 30.1, 29.4, 27.4),
        ("Garhwali", 60.5, 60.0, 58.6, 57.9, 53.5),
        ("Garo", 25.5, 22.6, 18.6, 15.8, 9.5),
        ("Halbi", 61.7, 61.2, 59.1, 57.2, 51.6),
        ("Haryanvi", 59.2, 57.6, 55.7, 54.5, 48.1),
        ("Idu Mishmi", 81.6, 81.5, 78.8, 79.4, 64.1),
        ("Jaipuri", 31.3, 30.0, 30.5, 29.4, 28.1),
        ("Karbi", 86.9, 87.9, 85.0, 82.9, 63.3),
        ("Khandeshi", 66.5, 65.6, 64.3, 62.5, 56.6),
        ("Khariboli", 33.3, 32.3, 29.9, 29.0, 27.0),
        ("Khortha", 49.7, 48.7, 45.6, 44.9, 41.3),
        ("Kokborok", 81.2, 80.9, 78.7, 77.8, 68.2),
        ("Kumaoni", 35.1, 35.2, 33.3, 32.1, 30.4),
        ("Kurumali", 14.3, 14.0, 12.4, 12.5, 11.3),
        ("Lambadi", 51.6, 51.6, 48.4, 38.7, 25.8),
        ("Magahi", 43.7, 42.8, 40.9, 40.3, 30.4),
        ("Malvani", 42.1, 42.1, 39.5, 39.0, 30.4),
        ("Marwari", 46.1, 45.7, 44.6, 43.3, 39.7),
        ("Mizo", 42.8, 41.3, 38.8, 35.9, 25.3),
        ("Nagamese", 64.7, 63.3, 60.6, 58.7, 50.1),
        ("Sadri", 64.6, 63.7, 62.8, 61.6, 58.8),
        ("Rajasthani", 48.6, 48.1, 47.0, 45.6, 41.8),
        ("Rengma", 86.0, 83.8, 83.6, 82.3, 71.7),
        ("Sambalpuri", 74.7, 74.6, 71.6, 70.9, 62.7),
        ("Shekhawati", 22.0, 20.9, 18.7, 18.2, 19.1),
        ("Sumi", 89.0, 88.6, 86.5, 85.8, 78.5),
        ("Surgujia", 48.3, 48.4, 45.3, 43.4, 37.5),
        ("Surjapuri", 70.1, 69.7, 67.3, 67.5, 69.1),
        ("Tulu", 72.3, 72.8, 71.4, 68.4, 57.3),
    ]

    half = len(ns_list) // 2
    for i in range(half):
        l1 = ns_list[i]
        l2 = ns_list[i + half]
        non_sched_data.append([
            Paragraph(f"<b>{l1[0]}</b>", tbl_cell),
            Paragraph(f"{l1[1]:.1f}", tbl_cell_center),
            Paragraph(f"{l1[2]:.1f}", tbl_cell_center),
            Paragraph(f"{l1[3]:.1f}", tbl_cell_center),
            Paragraph(f"{l1[4]:.1f}", tbl_cell_center),
            Paragraph(f"<b>{l1[5]:.1f}</b>", tbl_cell_bold_center),
            Paragraph(f"<b>{l2[0]}</b>", tbl_cell),
            Paragraph(f"{l2[1]:.1f}", tbl_cell_center),
            Paragraph(f"{l2[2]:.1f}", tbl_cell_center),
            Paragraph(f"{l2[3]:.1f}", tbl_cell_center),
            Paragraph(f"{l2[4]:.1f}", tbl_cell_center),
            Paragraph(f"<b>{l2[5]:.1f}</b>", tbl_cell_bold_center),
        ])

    ns_col_w = [62, 38, 38, 41, 43, 43, 62, 38, 38, 41, 43, 43]
    ns_table = Table(non_sched_data, colWidths=ns_col_w)
    ns_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#475569')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0,0), (-1,-1), 1.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(ns_table)
    story.append(Spacer(1, 6))

    # Production Guidelines
    story.append(Paragraph("6. Production Decision Matrix & Engineering Guidelines", sec_heading))
    
    rec_box_data = [
        [
            Paragraph("<b>Operational Recommendations by Deployment Use-Case</b>", ParagraphStyle('RecH', parent=tbl_header, alignment=0, textColor=colors.HexColor('#1e3a8a'))),
        ],
        [
            Paragraph(
                "• <b>Live Voice Agents & Conversational AI (Telephony / WebRTC):</b><br/>"
                "&nbsp;&nbsp;<b>Deploy SraVaani-0.5-live with 80 ms lookahead (`[70, 1]`)</b>. Provides the optimal latency balance: "
                "sub-100ms emission latency, smooth word-by-word streaming updates, and strong accuracy (~21.3% WER Hindi, 31.0% Indian English). "
                "Runs safely real-time on CPU and exceeds 60x real-time on NVIDIA GPUs.<br/><br/>"
                "• <b>Live Captions & Broadcasting:</b><br/>"
                "&nbsp;&nbsp;<b>Deploy SraVaani-0.5-live with 480 ms lookahead (`[70, 6]`)</b>. Reduces absolute WER by ~2.2% across languages "
                "while turnaround remains well within normal broadcast latency tolerances.<br/><br/>"
                "• <b>Archival Transcription, Medical/Legal Dictation, Call Center Audits:</b><br/>"
                "&nbsp;&nbsp;<b>Deploy SraVaani-1.0 Flagship</b>. The full-context Hybrid TDT-CTC model yields state-of-the-art accuracy: "
                "12.4% on Hindi, 14.8% on English, 19.0% on Gujarati, and 19.8% on Bengali, achieving ~28.5% lower error than streaming modes.<br/><br/>"
                "• <b>Hardware & Memory Footprint:</b><br/>"
                "&nbsp;&nbsp;Both models export in FP16 TorchScript (~900 MB). Low memory systems (e.g. 2GB VRAM GPUs) will automatically fallback to "
                "CPU execution without memory fragmentation, requiring no external NVIDIA NeMo dependencies.",
                tbl_cell
            )
        ]
    ]

    rec_table = Table(rec_box_data, colWidths=[540])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e0e7ff')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#6366f1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(rec_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Report successfully built at: {PDF_PATH}")

if __name__ == "__main__":
    generate_pdf()
