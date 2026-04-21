import streamlit as st
from docxtpl import DocxTemplate
import io
import re

# --- SNIPPET LIBRARY (The "Manager-Approved" Comma-Perfect Text) ---
SNIPPETS = {
    [span_3](start_span)"workmanship": "The workmanship shall be of the highest quality and completed in accordance with Governmental and Industry Standards[span_3](end_span).",
    [span_4](start_span)"firestopping": "When telecommunications pathways penetrate the fire zone perimeter, the integrity of the barrier must be re-established IAW TIA/EIA 568[span_4](end_span).",
    "cleaning": "The work area will be always kept clean and free from debris. [span_5](start_span)[span_6](start_span)LAN rooms must be dust-free upon completion[span_5](end_span)[span_6](end_span)."
}

st.title("🚀 SSC/TCNDE SOW Generator")

# 1. Upload Template
template_file = st.file_uploader("Upload Official SOW Template", type=["docx"])

if template_file:
    doc = DocxTemplate(template_file)
    placeholders = sorted(list(doc.get_undeclared_template_variables()))
    
    # 2. Disaster Scraper (The Sorting Engine)
    st.subheader("Step 2: Paste 'Disaster' Data")
    raw_data = st.text_area("Paste Room/Rack/DVO info here (any order)")

    processed_data = {}
    
    if raw_data:
        # MAGIC: Find anything like "Room 101" or "RM 101" and sort them
        room_matches = re.findall(r"(?:Room|RM)\s*(\d+)", raw_data, re.IGNORECASE)
        if room_matches:
            sorted_rooms = sorted(list(set(room_matches))) # Numerically sorted
            processed_data['room_list'] = ", ".join(sorted_rooms)
            st.success(f"Successfully sorted rooms: {processed_data['room_list']}")

    # 3. Dynamic Form
    st.subheader("Step 3: Review Final Fields")
    data_input = {}
    for p in placeholders:
        # If the tag matches an SSC snippet, auto-fill it
        default_val = SNIPPETS.get(p.lower(), "")
        # If we scraped a room list, auto-fill that tag
        if p == 'room_list' and 'room_list' in processed_data:
            default_val = processed_data['room_list']
            
        data_input[p] = st.text_input(f"Value for {p}:", value=default_val)

    # 4. Generate
    if st.button("Generate Perfect SOW"):
        doc.render(data_input)
        output = io.BytesIO()
        doc.save(output)
        st.download_button("📩 Download Document", output.getvalue(), "SOW_Final.docx")
