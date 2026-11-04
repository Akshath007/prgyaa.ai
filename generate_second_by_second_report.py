import os
import re
import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_margins(cell, top=100, bottom=100, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="CBD5E1", sz="4"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

# 82 Second-by-Second Micro-Turns mapping
MICRO_TURNS = [
    ("00:00-00:01", "Customer", "Hello.", "हेलो"),
    ("00:01-00:02", "Agent", "Hello.", "हेलो"),
    ("00:02-00:03", "Customer", "Haan.", "हाँ"),
    ("00:03-00:04", "Agent", "Hello.", "हेलो"),
    ("00:04-00:05", "Customer", "Hello.", "हेलो"),
    ("00:05-00:07", "Agent", "Liyakat Ali baat kar rahe ho?", "लियाकत अली बात कर रहे हो"),
    ("00:07-00:09", "Customer", "Hello.", "हेलो"),
    ("00:09-00:11", "Customer", "Awaaz... awaaz kat kat ke aa rahi hai.", "आवाज आवाज टोटल कहाँ रही है"),
    ("00:11-00:13", "Customer", "Haan, bolo.", "हाँ बोलो"),
    ("00:13-00:15", "Agent", "Sir, Liyakat Ali baat kar rahe ho?", "सर लियाकत बात कर रहे हो मैं"),
    ("00:15-00:17", "Customer", "Haan, bolo.", "अरे हाँ बोलो"),
    ("00:17-00:21", "Agent", "Main Kotak Bank Finance se baat kar rahi hoon.", "मैं कोटक बैंक फाइनेंस से बात कर रही हूँ"),
    ("00:21-00:25", "Agent", "Aapka loan pending hai, woh kyun nahi bhar rahe ho, sir, aap?", "आपका जॉब पेंडिंग है वो क्यों नहीं भर रहे हो सर आप"),
    ("00:25-00:26", "Agent", "Kotak ka.", "कोटक का"),
    ("00:26-00:27", "Customer", "Kaun sa?", "कौन सा"),
    ("00:27-00:29", "Agent", "Sir, Kotak ka.", "सर कोटक का"),
    ("00:29-00:34", "Customer", "Woh nahi na, uske pehle wala... bank ka naam bolo uske pehle wali.", "वो नहीं ना उसकी अपना बैंक का नाम बोलो उसकी पहले वाली"),
    ("00:34-00:35", "Agent", "Kya?", "क्या?"),
    ("00:35-00:38", "Customer", "Woh bank ka naam bolo.", "वो बैंक का नाम बोलो"),
    ("00:38-00:39", "Agent", "Kya bolu?", "क्या बोलूँ"),
    ("00:39-00:42", "Customer", "Kotak nahi, uske pehle wali bank ka naam bolo.", "कोटक नहीं उसके पहले वाली बैंक का नाम बोलो"),
    ("00:42-00:45", "Agent", "Kotak bol rahi hoon, Kotak. Kotak Bank.", "कोटक बोल रही हूँ कोटक कोटक"),
    ("00:45-00:53", "Customer", "Arre haan, par woh jo... jo loan transfer hui hai na aapke account ke usse bank mein, toh uske... uski matter chal rahi hai court ke andar already meri.", "अरे हाँ अपन जो जो लोन जो लोन ट्रांसफर हुई है ना आपके अकाउंट से बैंक में उसका उसकी मैटर चल रही थी कोरट के अंदर ऑलरेडी मेरी"),
    ("00:53-01:00", "Customer", "Aapka banda paise leke gaya tha, slip bhi nahi hona par court ke andar jama karaya tha aaj se 8-9 saal pehle.", "आपका बंदा पैसे लेके गया था फिलिपीनियन ऑफर कोरट के अंदर चला रहा है आठ नौ साल पहले"),
    ("01:00-01:01", "Agent", "Kab leke gaya?", "कब लेके गया?"),
    ("01:01-01:04", "Customer", "8-9 saal, 10 saal upar ho gaye.", "आठ नौ साल दस साल ऊपर हो गए"),
    ("01:04-01:05", "Agent", "Kab leke gaya?", "कब लेके गया?"),
    ("01:05-01:11", "Customer", "Hello. Arre aap madam mic band kar lo, aap dusre log se baat karo aap leke.", "हेलो अरे मैडम माइक चेंज कर लो या तो दूसरी और से बात करो आप लेके"),
    ("01:11-01:12", "Agent", "Kya? Kya?", "क्या क्या"),
    ("01:12-01:14", "Customer", "Hello.", "हेलो"),
    ("01:14-01:16", "Agent", "Haan, boliye.", "हाँ बोलिए"),
    ("01:16-01:22", "Customer", "Haan, haan, bhai. Main yeh bol raha hoon, woh Fullerton India ki hogi, aapke paas jo hai na, woh Fullerton India ki hai.", "हाँ हाँ भाई मैं यूँ बोल रहा हूँ वो फ्लूटोन इंडिया की होगी आपके पास जो है ना वो फ्लूटोन इंडिया की है"),
    ("01:22-01:23", "Customer", "Sahi hai?", "सही है"),
    ("01:23-01:25", "Agent", "Kaun sa India ki hai?", "कौन सा इंडिया की है"),
    ("01:25-01:29", "Customer", "Arre Fullerton India ki thi na bank, jo bank... jo pehle pehle loan leti thi, woh uski baat kar raha hoon.", "अरे फ्रूट्स ऑन इंडिया कहते हैं ना बैच ऑफ़ बैंक जो मैंने पहले लोन ली थी वो उसकी बात कर रहा हूँ"),
    ("01:29-01:34", "Agent", "Nahi, nahi. Main woh baat nahi kar rahi hoon, aapka two-wheeler...", "नहीं नहीं मैं वो मैं तो अभी मेरी कोटा के अंदर"),
    ("01:34-01:38", "Customer", "Nahi, toh abhi meri Kotak ke andar koi loan nahi mili. Main... toh abhi wrong number hai.", "कोई लोन नहीं ले रही हूँ मैम तो अभी रोंग नंबर है"),
    ("01:38-01:41", "Agent", "Sir, sir, suniye.", "सर सर सुनिए"),
    ("01:41-01:45", "Agent", "Sayyad Liyakat Ali baat kar rahe ho na?", "हाँ सही सही है लक्की तली बात कर रहे हो ना"),
    ("01:45-01:49", "Customer", "Nahi, nahi, wrong number, madam. Rakh do aap, koi matlab nahi hai baat karke. Kyunki meri jo loan chal rahi hai na, woh Fullerton India ki chal rahi hai, barabar?", "नहीं नहीं नंबर मैडम रख दो आप वो मतलब नहीं बात करेंगे क्योंकि मेरे जो लोन चले हैं ना वो फ्रूट्स ऑन इंडिया की चल रही है बराबर"),
    ("01:49-01:54", "Agent", "Nahi, nahi, main...", "नहीं नहीं नहीं वो"),
    ("01:54-01:56", "Agent", "Two-wheeler ka loan ka...", "कोर्ट में मैडम चल रही है वो टू व्हीलर का लोन का"),
    ("01:56-02:00", "Customer", "Nahi hai, madam, maine liya hi nahi hai maine, liya hi nahi hai maine. Abhi kaise back up karu?", "नहीं लिया मैडम मैंने लिया ही नहीं है मैंने लिया ही नहीं है मैंने तो मैं कैसे बैकअप करूँ"),
    ("02:00-02:05", "Agent", "Aapka naam...", "आपका पर्सनल लोन नहीं हो जाएगा तो नहीं"),
    ("02:05-02:10", "Customer", "Personal loan nahi hai, Liyakat Ali naam hai mera, Liyakat Ali naam hai mera. Aap barabar... phone aapne barabar kiya hai, phone aapne barabar kiya hai.", "नाम ही है मेरा लियागा तो नहीं नाम ही है मेरा आप बराबर फ़ोन आपने बराबर किया है फ़ोन आपने बराबर किया है"),
    ("02:10-02:14", "Customer", "Aur aap jo loan bata rahi hai na, Kotak ki koi loan nahi hai mere paas.", "वरना आप जो लोन बता रही है ना वो है कि कोई लोन नहीं ले रहे हो"),
    ("02:14-02:17", "Agent", "Aaj... aaj ya kal ka loan nahi hai, sir, woh.", "आज आज या कल का लोन नहीं है सर वो"),
    ("02:17-02:20", "Customer", "Nahi hai, mam. Kahe ke liye zabardasti kar rahe ho? Peena rahe ho mere ko aap.", "नहीं है मैम आप नहीं ले रहे हो जबरदस्ती वो कर रहे हो बिना लोन ले रहे हो आप"),
    ("02:20-02:22", "Agent", "Suniye na, sir, two-wheeler...", "सुनिए ना सर टू व्हीलर"),
    ("02:22-02:27", "Customer", "Arre, madam, nahi hai, nahi hai. Ek toh main... aap bolti na ki bhai yeh loan hai toh main accept kar bhi leta main. Nahi li toh kyun accept karunga?", "अरे मैडम नहीं है नहीं है एक्सेप्ट ना आप बोलती ना कि भाई ये लोन है तो एक्सेप्ट कर भी लेता हूँ नहीं देती तो एक्सेप्ट करूँगा"),
    ("02:27-02:31", "Agent", "Meri baat suniye, please.", "मेरी बात सुनिए हाँ आप मैं क्या बोल रही हूँ"),
    ("02:31-02:38", "Agent", "Aap... main kya bol rahi hoon, aap bol rahe ho na ki aapka loan nahi hai, theek hai, aapka loan nahi hai toh idhar kaise kya document, loan ID, apna...", "आप बोल रहे हो ना कि आपका लोन नहीं है ठीक है आपका लोन नहीं है तो इधर कैसे क्या डॉक्यूमेंट लोन आई डी और अपना"),
    ("02:38-02:41", "Customer", "Woh sab aapke bank... woh sab aapke bank wale jaane na, woh...", "वो सब आपके बैंक वाला जाना है ना"),
    ("02:41-02:43", "Agent", "Gadi...", "गाड़ी..."),
    ("02:43-02:48", "Customer", "Aapke bank wale jaane, usme kya. ID... ID... ID meri baat suno, forward karke bhej nahi rakhti aaj bank walo ko ek dusre ko.", "वो आपके बैंक वाला जाना है वो सब आई आई आई डी आई डी मेरी बात सुनो फॉरवर्ड कर दे देर नहीं लगती आज बैंक वालों के दूसरे को"),
    ("02:48-02:52", "Agent", "Gadi... gadi ka number, sab kaise kya...", "गाड़ी का नंबर सब कैसे क्या"),
    ("02:52-02:57", "Customer", "Ab meri baat suno na, madam. Main short mein bolta hoon. Aap police... apna court case kar lo, aap mere pe, hum court mein dekh lenge, theek hai, madam? Mera time waste mat karo aap.", "मेरी बात सुनो ना मैडम मैं मैं थोड़ा बोलता हूँ पुलिस अपना कोर्ट केस कर दो आप मेरे पे अपना कोर्ट में देख लेंगे ठीक है मैम थोड़ा टाइम वेस्ट मत करो आप"),
    ("02:57-03:02", "Customer", "Nahi, nahi, mera court case chal raha hai, मेरे ko khabar hai, gadi nahi li maine. Jab maine gadi liya hi nahi toh main kahe ke liye accept karu main?", "नहीं नहीं नहीं मेरा ओ टी टी चल रहा है मेरे को खबर है कि इतना गाड़ी ली नहीं मैंने जब मैंने गाड़ी लिया ही नहीं तो फिर मैं काहे के लिए एक्सेप्ट करूँगा"),
    ("03:02-03:04", "Agent", "Sir, sir, gadi liya...", "सर सर गाड़ी लिया"),
    ("03:04-03:08", "Customer", "Aap court mein case kar do na aap. Arre court mein case kar do na, madam, aap. Main saaf bol raha hoon, aapke samne se bol raha hoon main.", "आप कोर्ट में केस कर दो ना अरे कोर्ट में केस कर दो ना मैम आप मैं सब आ रहा हूँ सामने सब बोल रहा हूँ मैं"),
    ("03:08-03:14", "Agent", "Suniye na, sir, samne se bhi bolenge toh bhi hoyega, nahi bolenge toh bhi hoyega, woh mat...", "सुनिए ना सर सामने हाँ फिर होएगा नहीं बोलेंगे तो भी होएगा वो मत बराबर तो कर दो आप"),
    ("03:14-03:17", "Customer", "Haan, bas toh kar do. Theek hai, madam, chalo, time pass mat karo bekar mein.", "ठीक है मैम चलो टाइम पास मत करो बेकार मत"),
    ("03:17-03:21", "Agent", "Sir, bekar mein aap time pass kar rahe ho, maan...", "सर बेकार में आप टाइम पास कर रहे हो"),
    ("03:21-03:23", "Customer", "Madam, jo bhi hai, haan, haan toh rakh do na, madam, chalo, theek hai.", "मैडम क्यों फिर हाँ हाँ तो रख दो मैम चलो ठीक है"),
    ("03:23-03:26", "Agent", "Hai toh maan rahe nahi kyun?", "तो मान रहे नहीं क्यों"),
    ("03:26-03:28", "Agent", "Maanne se kya chota ho jayenge?", "मानने से क्या छोटा हो जाए"),
    ("03:28-03:32", "Customer", "Arre par li hi nahi hai, main bol toh raha hoon, aapko pata bhi nahi, samne se main bank ka naam bata raha hoon. Kahan ki meri loan chal rahi hai.", "अरे अपन नहीं नहीं मेरे बोल तो रहा हूँ आपको तो पता भी नहीं सामने से भी नहीं जाना बता रहा हूँ यहाँ के मेरे लोन चालू है"),
    ("03:32-03:36", "Agent", "Idhar... idhar document hai, sab detail hai, fir aur...", "सब डॉक्यूमेंट है सब डिटेल है डॉक्टर मेरे साथ"),
    ("03:36-03:43", "Customer", "Document sab, madam, meri baat suno, bank walo ko kya hai, sahi baat kahun toh. Woh turant leke, yaani woh bande ko phasana, yeh karna, woh karna.", "नहीं नहीं मेरी बात सुनो बैंक वालों का क्या है ना सर एक बार दिखाओ आपको वो सूरत लेके है ना वो बंदों को फसाना है ये करना वो करना"),
    ("03:43-03:49", "Customer", "Genuine hai na, Kotak ki aapki waha par branch... Kotak ki jo branch hai na, waha par genuine jaake main milke aaya hoon, yeh cheez ke liye.", "जेन्युइन है ना कोटा की आपकी आपको ब्रांच कोटा की जो ब्रांच है ना वहाँ पर जेन्युइन जाके मैं मिल के आया हूँ ये चीज़ के लिए"),
    ("03:49-03:50", "Agent", "Haan.", "हाँ"),
    ("03:50-03:53", "Customer", "Yeh jo personal jo loan hai na, main uski baat kar raha hoon.", "ये जो पर्सनल जो लोन है ना मैं उसकी बात कर रहा हूँ"),
    ("03:53-03:54", "Agent", "Haan.", "ठीक है"),
    ("03:54-03:59", "Customer", "Theek hai? Aur aap ek nayi leke aaye, bole woh two-wheeler li hui hai. Saala two-wheeler main aaj tak chalayi nahi maine.", "और आप एक नई लेके आए बोले वो टू व्हीलर ली हुई है साला कूलर में आज तक चलाई नहीं है ना"),
    ("03:59-04:01", "Customer", "Four-wheeler mein hi ghumta hoon main, theek hai?", "फोर व्हीलर में ही घूमता हूँ मैं ठीक है"),
    ("04:01-04:04", "Customer", "Pehle background check kar lo, fir phone karo aap, theek hai, madam? Chalo, rakh do phone ab, time pass mat karo bekar mein.", "पहले बैकग्राउंड चेक कर लो फिर फ़ोन तोड़ो आप ठीक है मैम चलो रख दो फ़ोन रख दो टाइम पास मत करो बेकार में"),
    ("04:04-04:08", "Agent", "Sir, time pass nahi kar rahe hain, line pe rahiye, main aapko detail share karti hoon.", "टाइम पास नहीं कर रहे लाइन पर नहीं है मैं आपको डिटेल शेयर करती हूँ"),
    ("04:08-04:10", "Agent", "Ek photo ka...", "फोटो काट"),
    ("04:10-04:15", "Agent", "Photo nikali, upar ka niche.", "फोटो निकालो ऊपर का नीचे"),
    ("04:15-04:20", "Agent", "Yeh ek nikal aur niche karke uska bhi nikal.", "एक निकाल और नीचे करके उसका भी निकाल उसको भी निकाल"),
    ("04:20-04:25", "Agent", "Isko dikha ke aa. Cut kar diya kya? Bhejoon kya aapko?", "उसको दिखा दिया भैया"),
    ("04:25-04:30", "Agent", "Kisko dikha rahe?", "किसको दिखा रहे हैं")
]

def main():
    print(f"Loaded {len(MICRO_TURNS)} second-by-second micro-turns.")

    # 1. Save TXT file
    txt_out_path = r"E:\PROJECTS\stt\Kotak_Second_by_Second_Transcript.txt"
    txt_lines = [
        "# source: pragyaa.ai Telephony ASR Evaluation",
        "# model: Bodhan Indic-Transcribe-Core (1.2B)",
        "# audio: 20260710-172448_7575030388_2013-all.wav (290.16s / 4m 50s)",
        "# resolution: Second-by-Second Micro-Timestamps (82 turns)",
        ""
    ]
    for turn in MICRO_TURNS:
        txt_lines.append(f"[{turn[0]}] {turn[1]} : {turn[3]}")
    
    with open(txt_out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines))
    print(f"Saved text transcript to: {txt_out_path}")

    # 2. Build Word Document
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # Header Box
    banner_table = doc.add_table(rows=1, cols=1)
    banner_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    banner_cell = banner_table.cell(0, 0)
    set_cell_background(banner_cell, "0F172A")
    set_cell_margins(banner_cell, top=200, bottom=200, left=240, right=240)
    banner_cell.width = Inches(7.1)

    p_brand = banner_cell.paragraphs[0]
    p_brand.paragraph_format.space_after = Pt(2)
    r1 = p_brand.add_run("pragyaa")
    r1.font.size = Pt(18)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(255, 255, 255)
    r2 = p_brand.add_run(".ai")
    r2.font.size = Pt(18)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(56, 189, 248)
    r_sub = p_brand.add_run("  |  SECOND-BY-SECOND MICRO-TIMELINE TRANSCRIPT")
    r_sub.font.size = Pt(9)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(148, 163, 184)

    p_t = banner_cell.add_paragraph()
    p_t.paragraph_format.space_after = Pt(2)
    rt = p_t.add_run("Kotak Bank Debt Call — Full 82-Turn Second-by-Second Transcript")
    rt.font.size = Pt(12.5)
    rt.font.bold = True
    rt.font.color.rgb = RGBColor(241, 245, 249)

    p_meta = banner_cell.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(0)
    rm = p_meta.add_run("Bodhan Indic-Transcribe-Core (1.2B) vs Gemini 3.5 Flash • 290.16s Audio • Micro-resolution [MM:SS-MM:SS]")
    rm.font.size = Pt(8.5)
    rm.font.color.rgb = RGBColor(203, 213, 225)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Micro-Turn Table
    trans_table = doc.add_table(rows=len(MICRO_TURNS) + 1, cols=4)
    trans_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(trans_table, color="E2E8F0")

    t_headers = ["Time [Sec]", "Speaker", "Bodhan AI Transcription (Hindi)", "Gemini 3.5 Flash Reference (Hinglish)"]
    widths = [Inches(1.0), Inches(0.85), Inches(2.6), Inches(2.65)]

    for col_idx, (h_title, w) in enumerate(zip(t_headers, widths)):
        cell = trans_table.cell(0, col_idx)
        cell.width = w
        cell.text = h_title
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8)
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)

    for idx, turn in enumerate(MICRO_TURNS, start=1):
        row = trans_table.rows[idx]
        bg = "FFFFFF" if idx % 2 == 1 else "F8FAFC"
        
        # Col 0: Timestamp
        c0 = row.cells[0]
        c0.width = widths[0]
        c0.text = turn[0]
        set_cell_background(c0, bg)
        set_cell_margins(c0, top=70, bottom=70, left=70, right=70)
        p0 = c0.paragraphs[0]
        p0.runs[0].font.size = Pt(7.8)
        p0.runs[0].font.color.rgb = RGBColor(100, 116, 139)
        p0.runs[0].font.name = "Consolas"

        # Col 1: Speaker
        c1 = row.cells[1]
        c1.width = widths[1]
        spk = turn[1]
        c1.text = spk
        set_cell_background(c1, bg)
        set_cell_margins(c1, top=70, bottom=70, left=70, right=70)
        p1 = c1.paragraphs[0]
        p1.runs[0].font.size = Pt(7.8)
        p1.runs[0].font.bold = True
        if "Agent" in spk:
            p1.runs[0].font.color.rgb = RGBColor(2, 132, 199)
        else:
            p1.runs[0].font.color.rgb = RGBColor(124, 58, 237)

        # Col 2: Bodhan Devanagari text
        c2 = row.cells[2]
        c2.width = widths[2]
        c2.text = turn[3]
        set_cell_background(c2, bg)
        set_cell_margins(c2, top=70, bottom=70, left=90, right=90)
        p2 = c2.paragraphs[0]
        p2.runs[0].font.name = "Nirmala UI"
        p2.runs[0].font.size = Pt(8.2)
        p2.runs[0].font.color.rgb = RGBColor(15, 23, 42)

        # Col 3: Gemini Ground Truth
        c3 = row.cells[3]
        c3.width = widths[3]
        c3.text = turn[2]
        set_cell_background(c3, bg)
        set_cell_margins(c3, top=70, bottom=70, left=90, right=90)
        p3 = c3.paragraphs[0]
        p3.runs[0].font.size = Pt(8.0)
        p3.runs[0].font.color.rgb = RGBColor(71, 85, 105)

    docx_paths = [
        r"E:\PROJECTS\stt\Bodhan_Second_by_Second_Transcript_Report.docx",
        r"E:\Downloads\Chrome\Bodhan_Second_by_Second_Transcript_Report.docx",
        r"E:\PROJECTS\stt\pragyaa_dashboard\static\Bodhan_Second_by_Second_Transcript_Report.docx"
    ]
    for p in docx_paths:
        doc.save(p)
    print(f"Saved DOCX report with 82 turns to {docx_paths[0]}")

    # 3. Convert to PDF via Word COM
    print("Converting 82-turn DOCX to PDF via Word COM...")
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        abs_docx = os.path.abspath(docx_paths[0])
        pdf_paths = [
            r"E:\PROJECTS\stt\Bodhan_Second_by_Second_Transcript_Report.pdf",
            r"E:\Downloads\Chrome\Bodhan_Second_by_Second_Transcript_Report.pdf",
            r"E:\PROJECTS\stt\pragyaa_dashboard\static\Bodhan_Second_by_Second_Transcript_Report.pdf"
        ]
        w_doc = word.Documents.Open(abs_docx)
        for pdf_p in pdf_paths:
            w_doc.SaveAs(os.path.abspath(pdf_p), FileFormat=17)
        w_doc.Close()
        word.Quit()
        print(f"Saved PDF report with 82 turns to {pdf_paths[0]}")
    except Exception as e:
        print("Note on PDF export:", e)

    # 4. Update samples_metadata.json with 82 micro-turns
    meta_path = r"E:\PROJECTS\stt\pragyaa_dashboard\static\audio\samples_metadata.json"
    with open(meta_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    bodhan_diarized_lines = [f"[{t[0]}] {t[1]} : {t[3]}" for t in MICRO_TURNS]
    gt_diarized_lines = [f"[{t[0]}] {t[1]} : {t[2]}" for t in MICRO_TURNS]

    samples[0]["predicted_diarized"] = "\n".join(bodhan_diarized_lines)
    samples[0]["ground_truth_diarized"] = "\n".join(gt_diarized_lines)
    samples[0]["models"]["bodhan"]["predicted_diarized"] = "\n".join(bodhan_diarized_lines)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
    print("Updated samples_metadata.json with all 82 second-by-second micro-turns!")

if __name__ == "__main__":
    main()

