import pdfplumber
import time
from pathlib import Path

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import xml.etree.cElementTree as ET
from models import QuotationItems, get_fake_quotation_items
from xml.dom import minidom


def get_pdf_content(pdf_path: Path) -> str:
    text: str = ""
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=1, y_tolerance=1)
            if page_text:
                text += page_text + "\n\n"
    return text


def generate_xml_export(
    quotation_items: QuotationItems,
    customer_id: int = 102736,
    commission: str = "Cerdia Leitwarte",
    type: str = "A",
    shipping_condition_id: int = 2,
) -> bytes:
    order = ET.Element("order")

    ET.SubElement(order, "customerId").text = str(customer_id)
    ET.SubElement(order, "commission").text = commission
    ET.SubElement(order, "type").text = type
    ET.SubElement(order, "shippingConditionId").text = str(shipping_condition_id)

    items = ET.SubElement(order, "items")

    for quotation_item in quotation_items.items:
        item = ET.SubElement(items, "item")
        ET.SubElement(item, "sku").text = quotation_item.sku
        ET.SubElement(item, "name").text = quotation_item.name
        ET.SubElement(item, "text").text = quotation_item.text
        ET.SubElement(item, "quantity").text = str(quotation_item.quantity)
        ET.SubElement(item, "quantityUnit").text = quotation_item.quantity_unit
        ET.SubElement(item, "price").text = "695.00"
        ET.SubElement(item, "priceUnit").text = "€"
        ET.SubElement(item, "purchasePrice").text = ""
        ET.SubElement(item, "commission").text = quotation_item.commission

    rough_string: str = ET.tostring(order, encoding="utf-8", xml_declaration=True)

    parsed = minidom.parseString(rough_string)

    xml_bytes: bytes = parsed.toprettyxml(indent="   ", encoding="utf-8")
    return xml_bytes
