import os
import time
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from lib import get_pdf_content, generate_xml_export
from pipelines import PipelineV2
from models import QuotationItems
from streamlit_pdf_viewer import pdf_viewer
from streamlit.runtime.uploaded_file_manager import UploadedFile

load_dotenv()

OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")


@st.dialog("Analyzing PDF")
def analyze_pdf() -> None:
    progress_bar = st.progress(0, text="Loading PDF. Please be patient...")
    time.sleep(2)

    progress_bar.progress(0.10, "📄 Extracting text from PDF...")
    time.sleep(1)
    pdf_content: str = get_pdf_content(st.session_state["pdf_file_path"])

    page_count: int = len(pdf_content.split("\n\n"))
    progress_bar.progress(0.25, f"📜 Extracted {page_count} pages from PDF")
    time.sleep(2)

    quotation_items: QuotationItems = PipelineV2.extract_quotation_items_from_pdf(
        pdf_content=pdf_content,
        openrouter_api_key=OPENROUTER_API_KEY,
        progress_bar=progress_bar,
    )

    progress_bar.progress(
        0.99, f"📦 Found {len(quotation_items.items)} quotation items"
    )
    time.sleep(2)

    progress_bar.progress(1.0, "✅ PDF analysis completed")
    time.sleep(2)

    st.session_state["quotation_items"] = quotation_items
    st.session_state["analyzed"] = True


def render_quotation_items(quotation_items: QuotationItems) -> None:
    for i, quotation_item in enumerate(quotation_items.items):
        with st.expander(
            label=(
                f"**{quotation_item.commission.replace('LV-POS. ','')}** {quotation_item.name}"
            ),
            expanded=True,
        ):
            st.markdown(f"#### {quotation_item.name}")

            is_high_confidence: bool = quotation_item.is_door_product_confidence >= 0.75
            is_medium_confidence: bool = (
                quotation_item.is_door_product_confidence >= 0.5
                and quotation_item.is_door_product_confidence < 0.75
            )
            is_low_confidence: bool = quotation_item.is_door_product_confidence < 0.5

            confidence_color, confidence_icon = (
                ("green", ":material/check:")
                if is_high_confidence
                else (
                    ("orange", ":material/warning:")
                    if is_medium_confidence
                    else ("red", ":material/report:")
                )
            )

            st.markdown(
                f"""
                :gray-badge[:material/format_align_right: {quotation_item.commission}]
                :{'red' if quotation_item.sku is None else 'gray'}-badge[:material/barcode: SKU: {quotation_item.sku}]
                :gray-badge[:material/confirmation_number: Quantity: {quotation_item.quantity} {quotation_item.quantity_unit}]
                :{confidence_color}-badge[{confidence_icon} Confidence: {quotation_item.is_door_product_confidence*100:.0f} %]
                """
            )
            st.markdown(quotation_item.text, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="ByteCook",
        page_icon="👨‍🍳",
        layout="wide",
    )
    st.title("👨‍🍳 ByteCook")

    # PDF upload
    if not st.session_state.get("pdf", None):
        pdf_upload: UploadedFile | None = st.file_uploader(
            label="Please upload your service specification document (PDF)",
            type=["pdf"],
            label_visibility="collapsed",
        )
        if pdf_upload:
            st.session_state.pdf = pdf_upload
            upload_path = Path(Path(__file__).parents[1] / "uploads")
            upload_path.mkdir(parents=True, exist_ok=True)
            pdf_file_path = Path(upload_path / pdf_upload.name).resolve()
            pdf_file_path.write_bytes(pdf_upload.getvalue())
            st.session_state["pdf_uploaded"] = True
            st.session_state["pdf_file_path"] = pdf_file_path

            analyze_pdf()

            # Closes the dialog
            st.rerun()

        return

    pdf_column, quotation_items_column = st.columns([2, 3])

    with pdf_column:
        with st.container(border=True, height=740):
            st.markdown(
                "<h3 style='text-align: center'>Service Specification Document</h3>",
                unsafe_allow_html=True,
            )
            with st.container(border=True):
                pdf_viewer(
                    st.session_state.pdf.getvalue(),
                    height=600,
                )

    with quotation_items_column:
        with st.container(border=True, height=740):
            if not st.session_state.get("analyzed", False):
                st.rerun()

            quotation_items: QuotationItems = st.session_state["quotation_items"]

            st.markdown(
                f"<h3 style='text-align: center'>{len(quotation_items.items)} Quotation Items</h3>",
                unsafe_allow_html=True,
            )

            if not quotation_items.items:
                st.error("No quotation items found in the PDF.", icon="🚨")

            if st.session_state.get("quotation_items_expansion", None) is None:
                st.session_state["quotation_items_expansion"] = [
                    False for _ in enumerate(quotation_items.items)
                ]

            with st.container(border=False, height=580):
                render_quotation_items(quotation_items)

            # XML export button
            xml_file_name: str = (
                datetime.now().strftime("%Y-%d-%m-%H-%M-%S")
                + "-output-"
                + Path(st.session_state["pdf_file_path"]).name
                + ".xml"
            )
            st.download_button(
                label="Export as XML",
                data=generate_xml_export(quotation_items=quotation_items),
                file_name=xml_file_name,
                mime="application/xml",
                type="primary",
                use_container_width=True,
                icon="💾",
                key="download-xml",
            )


if __name__ == "__main__":
    main()
