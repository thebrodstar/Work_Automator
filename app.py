import streamlit as st
from docxtpl import DocxTemplate
import io
import re

st.set_page_config(page_title="SOW Automator", page_icon="📄")

# --- SNIPPET LIBRARY ---
SNIPPETS = {
    "workmanship": "The workmanship shall be of the highest quality and completed in accordance with Governmental and Industry Standards.",
    "firestopping": "When telecommunications pathways penetrate the fire zone perimeter, any disruption will nullify the performance rating. Re-establish integrity IAW TIA/EIA 568.",
    "cleaning": "The work area will be always kept clean and free from debris. LAN rooms must be dust-free upon completion.",
    "as_builts": "As-built drawings are to show the installed cable routes, splice locations, terminal locations, and outlet identification numbers."
}

st.title("📄 SSC/TCNDE Stealth Automator")

# 1. TEMPLATE UPLOAD
template_file = st.file_uploader("Upload Official SOW Template", type=["docx"])

if template_file:
    doc = DocxTemplate(template_file)
    placeholders = sorted(list(doc.get_undeclared_template_variables()))
    st.success(f"Detected {len(placeholders)} fields.")

    # 2. DISASTER SCRAPER
    raw_data = st.text_area("Paste messy notes or room lists here...", height=150)
    
    auto_filled_values = {}
    if raw_data:
        room_matches = re.findall(r"(?:Room|RM|Rm)\s*(\d+)", raw_data)
        if room_matches:
            sorted_rooms = sorted([int(r) for r in set(room_matches)])
            room_string = ", ".join([f"Room {r}" for r in sorted_rooms])
            auto_filled_values['room_list'] = room_string
            st.info(f"✨ Sorted Rooms: {room_string}")

    # 3. DYNAMIC FORM
    data_input = {}
    cols = st.columns(2)
    for i, p in enumerate(placeholders):
        col = cols[i % 2]
        default_val = SNIPPETS.get(p.lower(), "")
        if p == 'room_list' and 'room_list' in auto_filled_values:
            default_val = auto_filled_values['room_list']
            
        data_input[p] = col.text_input(f"Value for {p}", value=default_val)

    # 4. GENERATION
    if st.button("🚀 Generate Final Document"):
        doc.render(data_input)
        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        st.download_button("📩 Download Ready SOW", output_stream, "Final_SOW.docx")
