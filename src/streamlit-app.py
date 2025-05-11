import os
import time
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from lib import get_pdf_content, generate_xml_export
from pipelines import PipelineV2
from models import QuotationItem, QuotationItems
from streamlit_pdf_viewer import pdf_viewer
from streamlit.runtime.uploaded_file_manager import UploadedFile

load_dotenv()

OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")


@st.dialog("Analyzing PDF")
def analyze_pdf() -> None:
    sleep_time: float = 1.0
    progress_bar = st.progress(0, text="Loading PDF. Please be patient...")
    time.sleep(sleep_time)

    progress_bar.progress(0.10, "📄 Extracting text from PDF...")
    time.sleep(sleep_time)
    pdf_content: str = get_pdf_content(st.session_state["pdf_file_path"])

    page_count: int = len(pdf_content.split("\n\n"))
    progress_bar.progress(0.25, f"📜 Extracted {page_count} pages from PDF")
    time.sleep(sleep_time)

    quotation_items: QuotationItems = PipelineV2.extract_quotation_items_from_pdf(
        pdf_content=pdf_content,
        openrouter_api_key=OPENROUTER_API_KEY,
        progress_bar=progress_bar,
    )

    progress_bar.progress(
        0.99, f"📦 Found {len(quotation_items.items)} quotation items"
    )
    time.sleep(sleep_time)

    progress_bar.progress(1.0, "✅ PDF analysis completed")
    time.sleep(sleep_time)

    st.session_state["quotation_items"] = quotation_items
    st.session_state["analyzed"] = True
    st.session_state["show_analysis_success_toast"] = True


def render_quotation_items(quotation_items: QuotationItems) -> None:
    for i, quotation_item in enumerate(quotation_items.items):
        with st.expander(
            label=(
                f"**{quotation_item.commission.replace('LV-POS. ','')}** {quotation_item.name}"
            ),
            expanded=True,
        ):
            col0, col1 = st.columns([9, 1])
            with col0:
                st.markdown(f"#### {quotation_item.name}")
            with col1:
                edit_button = st.button(
                    label="", key=f"edit-{i}", type="secondary", icon="✏️"
                )
                if edit_button:
                    render_edit_quotation_item(i, quotation_item)

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


@st.dialog("Edit Quotation Item")
def render_edit_quotation_item(index: int, quotation_item: QuotationItem) -> None:
    edited_sku = st.text_input(
        label="SKU:",
        value=quotation_item.sku,
        key=f"edit-sku-{index}",
    )
    edited_commission = st.text_input(
        label="Commission:",
        value=quotation_item.commission,
        key=f"edit-commission-{index}",
    )
    col0, col1 = st.columns([1, 1])
    with col0:
        edited_quantity = st.number_input(
            label="Quantity:",
            value=quotation_item.quantity,
            key=f"edit-quantity-{index}",
        )
    with col1:
        edited_quantity_unit = st.text_input(
            label="Quantity Unit:",
            value=quotation_item.quantity_unit,
            key=f"edit-quantity-unit-{index}",
        )
    edited_name = st.text_input(
        label="Name:",
        value=quotation_item.name,
        key=f"edit-name-{index}",
    )
    edited_text = st.text_area(
        label="Text",
        value=quotation_item.text,
        height=200,
        key=f"edit-text-{index}",
    )
    if st.button(
        label="Save",
        type="primary",
        key=f"save-{index}",
        icon="💾",
    ):
        quotation_item.sku = edited_sku
        quotation_item.name = edited_name
        quotation_item.commission = edited_commission
        quotation_item.text = edited_text
        quotation_item.quantity = edited_quantity
        quotation_item.quantity_unit = edited_quantity_unit
        st.session_state["quotation_items"].items[index] = quotation_item
        st.session_state["show_quotation_item_update_toast"] = True
        st.rerun()


def main():
    st.set_page_config(
        page_title="ByteCook",
        page_icon="👨‍🍳",
        layout="wide",
    )
    st.title("👨‍🍳 ByteCook")

    if st.session_state.get("show_quotation_item_update_toast", False):
        st.toast("Quotation item updated successfully!", icon="✅")
        st.session_state["show_quotation_item_update_toast"] = False

    if st.session_state.get("show_analysis_success_toast", False):
        st.toast("PDF analysis completed successfully!", icon="✅")
        st.session_state["show_analysis_success_toast"] = False

    # PDF upload
    if not st.session_state.get("pdf", None):
        col0 = st.columns([1, 1, 1])[1]
        with col0:
            customer_id = st.text_input(
                label="Customer ID:",
                placeholder="Customer ID",
            )
            st.session_state["customer_id"] = customer_id

            pdf_upload: UploadedFile | None = st.file_uploader(
                label="Please upload your service specification document (PDF):",
                type=["pdf"],
            )

            analyze_button = st.button(
                label="Analyze PDF",
                type="primary",
                icon="🔍",
            )

            if customer_id and pdf_upload and analyze_button:
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
                data=generate_xml_export(
                    quotation_items=quotation_items,
                    customer_id=st.session_state["customer_id"],
                ),
                file_name=xml_file_name,
                mime="application/xml",
                type="primary",
                use_container_width=True,
                icon="💾",
                key="download-xml",
            )


if __name__ == "__main__":
    main()
