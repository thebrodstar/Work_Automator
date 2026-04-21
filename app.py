import streamlit as st
from docxtpl import DocxTemplate
import io
import re
import pandas as pd

st.set_page_config(page_title="SSC SOW Automator", page_icon="📄")

# --- SNIPPET LIBRARY (Manager-Approved Text) ---
# [span_0](start_span)[span_1](start_span)[span_2](start_span)[span_3](start_span)These auto-fill when the template has these tags, ensuring perfect grammar[span_0](end_span)[span_1](end_span)[span_2](end_span)[span_3](end_span)
SNIPPETS = {
    [span_4](start_span)"workmanship": "The workmanship shall be of the highest quality and completed in accordance with Governmental and Industry Standards[span_4](end_span).",
    [span_5](start_span)"firestopping": "When telecommunications pathways penetrate the fire zone perimeter, the integrity of the barrier must be re-established IAW TIA/EIA 568[span_5](end_span).",
    "cleaning": "The work area will be always kept clean and free from debris. [span_6](start_span)[span_7](start_span)LAN rooms must be dust-free upon completion[span_6](end_span)[span_7](end_span).",
    [span_8](start_span)"as_builts": "As-built drawings are to show the installed cable routes, splice locations, terminal locations, and outlet identification numbers[span_8](end_span)."
}

st.title("📄 SSC/TCNDE Stealth Automator")
st.markdown("---")

# 1. TEMPLATE UPLOAD
st.subheader("Step 1: Upload Official Template")
template_file = st.file_uploader("Upload Word Template (.docx)", type=["docx"])

if template_file:
    doc = DocxTemplate(template_file)
    # This automatically finds all {{ placeholders }} in the doc
    placeholders = sorted(list(doc.get_undeclared_template_variables()))
    st.success(f"Detected {len(placeholders)} unique fields in this template.")

    # 2. THE DISASTER SCRAPER (The "Barely Touch a Button" Logic)
    st.subheader("Step 2: Paste Disaster Info")
    raw_data = st.text_area("Paste messy notes or room lists here...", height=150)
    
    # Logic to auto-sort rooms numerically even if Dave pasted them out of order
    auto_filled_values = {}
    if raw_data:
        # Regex to find numbers after 'Room', 'RM', or 'Rm'
        room_matches = re.findall(r"(?:Room|RM|Rm)\s*(\d+)", raw_data)
        if room_matches:
            # Convert to integers to sort properly (1, 2, 10 instead of 1, 10, 2)
            sorted_rooms = sorted([int(r) for r in set(room_matches)])
            room_string = ", ".join([f"Room {r}" for r in sorted_rooms])
            auto_filled_values['room_list'] = room_string
            st.info(f"✨ Auto-sorted Room Order: {room_string}")

    # 3. DYNAMIC FORM GENERATION
    st.subheader("Step 3: Review and Polish")
    data_input = {}
    
    # Split UI into two columns to handle many fields easily
    cols = st.columns(2)
    for i, p in enumerate(placeholders):
        col = cols[i % 2]
        
        # Check if we have a snippet or an auto-filled room list
        default_val = SNIPPETS.get(p.lower(), "")
        if p == 'room_list' and 'room_list' in auto_filled_values:
            default_val = auto_filled_values['room_list']
            
        data_input[p] = col.text_input(f"Value for {{ {p} }}", value=default_val)

    # 4. GENERATION ENGINE
    st.markdown("---")
    if st.button("🚀 Generate Final Document"):
        try:
            doc.render(data_input)
            
            # Save to memory (stealth mode - no local file footprint)
            output_stream = io.BytesIO()
            doc.save(output_stream)
            output_stream.seek(0)
            
            st.download_button(
                label="📩 Download Ready SOW",
                data=output_stream,
                file_name="Generated_Project_SOW.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            st.balloons()
        except Exception as e:
            st.error(f"Error generating document: {e}")
