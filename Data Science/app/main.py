import base64
import os
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

import gradio as gr
from src.ingestion.parser import PDFMultimodalIngestor
from src.vector_store.store import VectorStoreManager
from src.generation.rag_engine import MultimodalRAGEngine

# Initialize pipeline modules once to share the single Qdrant client connection
ingestor = PDFMultimodalIngestor()
vstore = VectorStoreManager()
rag_engine = MultimodalRAGEngine(vector_store=vstore)


def upload_and_index_pdf(pdf_file):
    if pdf_file is None:
        return "Please select a PDF document first."

    try:
        pdf_path = pdf_file.name
        chunks = ingestor.process_pdf(pdf_path)
        
        # Use existing single vstore instance to index chunks
        vstore.index_chunks(chunks)
        
        return f"Document indexed successfully! ({len(chunks)} page chunks stored in Qdrant)"
    except Exception as e:
        return f"Error during indexing: {str(e)}"


def answer_question(user_query):
    if not user_query.strip():
        return "Please enter a question.", []

    try:
        result = rag_engine.answer_query(user_query)
        answer_text = result["answer"]
        sources = result["sources"]

        retrieved_images = []
        for src in sources:
            img_path = src.get("image_path")
            if img_path and os.path.exists(img_path):
                retrieved_images.append(img_path)

        # Deduplicate images so identical page snapshots aren't shown twice
        unique_images = list(dict.fromkeys(retrieved_images))

        return answer_text, unique_images
    except Exception as e:
        return f"Error generating answer: {str(e)}", []


def get_logo_html(logo_file_path="healthos.png"):
    if os.path.exists(logo_file_path):
        with open(logo_file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f'<img src="data:image/png;base64,{encoded_string}" class="healthos-logo-img" alt="HealthOS Logo" />'
    return '<span style="color:#0B839E; font-weight:bold; font-size:1.5rem;">HEALTHOS</span>'


# Custom HealthOS CSS styling
custom_css = """
body, .gradio-container {
    background-color: #F5F5F5 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

footer, .footer {
    display: none !important;
}

.healthos-header-row {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    padding: 10px 0;
}

.healthos-title-box h1 {
    color: #0B839E !important;
    font-size: 2.1rem !important;
    font-weight: 700 !important;
    margin-bottom: 4px !important;
}

.healthos-title-box p {
    color: #16303B !important;
    font-size: 1.05rem !important;
    margin: 0 !important;
}

.healthos-logo-img {
    width: 110px;
    height: auto;
    display: block;
    object-fit: contain;
}

.healthos-btn {
    background: #0B839E !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    transition: background 0.2s ease-in-out;
}

.healthos-btn:hover {
    background: #086b82 !important;
}

.section-title {
    color: #16303B !important;
    font-weight: 700 !important;
    margin-bottom: 12px !important;
    font-size: 1.25rem !important;
}

.gr-box, .gr-form, .gr-panel {
    border-color: #E2E8F0 !important;
    border-radius: 10px !important;
    background-color: #FFFFFF !important;
}

.custom-footer {
    text-align: center;
    padding: 24px 0 10px 0;
    margin-top: 30px;
    border-top: 1px solid #E2E8F0;
    color: #16303B;
    font-size: 0.95rem;
}

.custom-footer strong {
    color: #0B839E;
}
"""

with gr.Blocks(title="HealthOS") as demo:
    
    with gr.Row(elem_classes=["healthos-header-row"]):
        with gr.Column(scale=1, min_width=120):
            gr.HTML(get_logo_html("healthos.png"))
        with gr.Column(scale=6, elem_classes=["healthos-title-box"]):
            gr.Markdown(
                """
                # HEALTHOS Multimodal RAG & Health Facility QA System
                Enterprise Document Intelligence Engine — Extract insights from clinical specs, facility guidelines, and technical reports using vision-empowered AI context.
                """
            )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("<h3 class='section-title'>1. Ingest PDF Document</h3>")
            pdf_input = gr.File(
                label="Select Health Facility PDF Document",
                file_types=[".pdf"]
            )
            upload_button = gr.Button("Parse & Index to Qdrant", elem_classes=["healthos-btn"])
            upload_status = gr.Textbox(label="Ingestion Status Output", interactive=False, lines=2)

            upload_button.click(
                fn=upload_and_index_pdf,
                inputs=[pdf_input],
                outputs=[upload_status]
            )

        with gr.Column(scale=2):
            gr.Markdown("<h3 class='section-title'>2. Multimodal Query & QA Engine</h3>")
            query_input = gr.Textbox(
                label="Ask a Question",
                placeholder="e.g., What are the room layout specifications and operational guidelines on page 2?",
                lines=2
            )
            ask_button = gr.Button("Submit Multimodal Query", elem_classes=["healthos-btn"])
            answer_output = gr.Textbox(label="Generated Intelligence Response", lines=9, interactive=False)
            gallery_output = gr.Gallery(
                label="Retrieved Visual Context Snapshots (Qdrant Page Chunks)",
                columns=2,
                height="auto"
            )

            ask_button.click(
                fn=answer_question,
                inputs=[query_input],
                outputs=[answer_output, gallery_output]
            )

    with gr.Row(elem_classes=["custom-footer"]):
        gr.Markdown(
            """
            © 2026 **HealthOS™ Multimodal Document QA System**. All rights reserved. | Developed by **Keo**
            """
        )

if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        css=custom_css,
        theme=gr.themes.Soft(primary_hue="teal"),
        favicon_path="healthos.png" if os.path.exists("healthos.png") else None
    )