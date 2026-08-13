import streamlit as st
import os
import sys
import tempfile

# Add src to sys.path to allow importing from src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from pii_redactor import PIIRedactor

st.set_page_config(
    page_title="PII Redaction Tool",
    page_icon="🔒",
    layout="centered"
)

st.title("🔒 PII Redaction Tool")
st.markdown("""
Upload a `.docx` file containing Personally Identifiable Information (PII). 
This tool will detect sensitive data and replace it with realistic fake data, preserving document structure.
""")

uploaded_file = st.file_uploader("Upload Document (DOCX)", type=['docx'])

if uploaded_file is not None:
    st.info("File uploaded successfully. Click below to redact.")
    
    if st.button("Run Redaction"):
        with st.spinner("Processing document... This may take a few moments for large files."):
            # Save uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_input:
                temp_input.write(uploaded_file.getbuffer())
                temp_input_path = temp_input.name
                
            # Create a temporary output path
            temp_output_path = temp_input_path.replace(".docx", "_redacted.docx")
            
            try:
                # Initialize redactor and process
                redactor = PIIRedactor()
                redactor.redact_document(temp_input_path, temp_output_path)
                
                st.success("Redaction completed successfully!")
                
                # Display statistics
                if redactor.stats:
                    st.subheader("📊 Detected PII Summary")
                    # Create columns for better display
                    cols = st.columns(3)
                    for i, (entity_type, count) in enumerate(redactor.stats.most_common()):
                        with cols[i % 3]:
                            st.metric(label=entity_type, value=count)
                else:
                    st.info("No PII was detected in this document.")
                
                # Provide download button
                with open(temp_output_path, "rb") as file:
                    st.download_button(
                        label="Download Redacted Document",
                        data=file,
                        file_name=f"redacted_{uploaded_file.name}",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                st.error(f"An error occurred during redaction: {str(e)}")
            finally:
                # Clean up temporary files to avoid logging/exposing data
                if os.path.exists(temp_input_path):
                    os.remove(temp_input_path)
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
