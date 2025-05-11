from pydantic import BaseModel, Field
from typing import List


class QuotationItem(BaseModel):
    sku: str | None = Field(
        ...,
        description="Kategoriezuordnung; The SKU (=article number) of the quotation item.",
        examples=["620001", "450001", "DL8110016"],
    )
    name: str = Field(
        description="The name of the quotation item (door/accessory/service).",
        examples=[
            "TVB - Türblatt 875x2125 mm",
            "Service- / Montagetechniker Bauhelfer",
        ],
    )
    text: str = Field(
        description="Beschreibung; A full-text description of the quotation item including item measures.",
        examples=[
            "Liefern und Einbauen von Innentür-Elementen.<br/>Elementgröße Richtmaß: 875 x 2.125 mm<br/>Angebotenes Fabrikat: Jeld-Wen Optima 30."
        ],
    )
    quantity: int = Field(
        description="The quantity of the quotation item.", examples=[1, 2, 3]
    )
    quantity_unit: str = Field(
        description="The unit of the quantity.", examples=["Stk", "m²", "lfm"]
    )
    commission: str = Field(
        description="Ordnungszahl; The commission of the quotation item (the quotation item's position ID in the service specification document).",
        examples=["LV-POS. 1.1.10"],
    )
    is_door_product_confidence: float = Field(
        description="Türbezug; Confidence score indicating the likelihood that the quotation item is related to door products. This includes door elements, door accessories, or services associated with door products. A higher score suggests a stronger association, while a lower score indicates less relevance. Minimum value is 0.0 and maximum value is 1.0. If the word `Tür` is part of the name or text, the confidence score should be very high. ",
    )


class QuotationItems(BaseModel):
    """
    The list of quotation items.
    """

    items: List[QuotationItem] = Field(description="The list of quotation items.")


def get_fake_quotation_items() -> QuotationItems:
    return QuotationItems(
        items=[
            QuotationItem(
                sku=None,
                name="Bürotür mit Stahl-U-Zarge (0,76 x 2,135 m)",
                text="Hörmann Stahlfutterzarge VarioFix für Mauerwerk oder TRB<br/>- Drückerhöhe 1050 mm<br/>- Meterrissmarkierung<br/>- Maulweitenkante 15 mm<br/>- Stahlblech verzinkt, Materialstärke 1,5 mm<br/>- Hörmann BaseLine HPL Türblatt<br/>- Türgewicht ca. 18,1 kg/m²<br/>- Türstärke ca. 40,7 mm",
                quantity=1,
                quantity_unit="Stk",
                commission="LV-POS. 1.1.10",
                is_door_product_confidence=0.99,
            ),
            QuotationItem(
                sku="620001",
                name="Bürotür mit Stahl-U-Zarge (0,885 x 2,135 m)",
                text="Wie Position 1.1.10, jedoch b = 0,885 m",
                quantity=3,
                quantity_unit="Stk",
                commission="LV-POS. 1.1.20",
                is_door_product_confidence=1.0,
            ),
            QuotationItem(
                sku="620001",
                name="Bürotür mit Stahl-U-Zarge (1,01 x 2,135 m)",
                text="Wie Position 1.1.10, jedoch b = 1,01 m",
                quantity=1,
                quantity_unit="Stk",
                commission="LV-POS. 1.1.30",
                is_door_product_confidence=0.96,
            ),
            QuotationItem(
                sku="620001",
                name="Bürotür mit Stahl-U-Zarge (1,01 x 2,135 m) + Naßraumanforderung",
                text="Wie Position 1.1.10, jedoch b = 1,01 m + Naßraumanforderung",
                quantity=1,
                quantity_unit="Stk",
                commission="LV-POS. 1.1.40",
                is_door_product_confidence=0.7,
            ),
            QuotationItem(
                sku="620001",
                name="Bürotür mit Stahl-U-Zarge (1,01 x 2,135 m) + Glasausschnitt voll VSG",
                text="Wie Position 1.1.10, jedoch b = 1,01 m + Glasausschnitt voll VSG",
                quantity=1,
                quantity_unit="Stk",
                commission="LV-POS. 1.1.50",
                is_door_product_confidence=1.0,
            ),
        ]
    )
