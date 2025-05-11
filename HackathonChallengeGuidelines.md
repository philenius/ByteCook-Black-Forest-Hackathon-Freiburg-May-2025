# Hackathon Challenge Guidelines

## Overview

Participants must create a system that automates the classification and organization of construction elements and services according to specified categories and requirements. The challenge involves managing various types of doors, accessories, and services while ensuring compliance with specific standards.
The goal is to develop an interface where users can enter a customer ID and upload a Service Specification Document (Leistungsverzeichnis). The system should automatically extract and classify the information into products and services, then reformat them into editable Quotation Items that can be exported as XML for ERP integration.

The functionality of the interface can be simplified as follows:

#### INPUT:

- Customer ID
- Service Specification Document

#### OUTPUT:

- Offer in XML format, ready for ERP import

### To support the challenge, we will provide the following:

- Product and Service Catalog (later in this document)
- Two examples, each containing the Sample Service Specification Document, a generated offer for an ERP system, and the expected XML output for the challenge.

Here is an example of the expected format for the XML output:

```
<?xml version="1.0" encoding="UTF-8"?>
<order>
   <customerId>102736</customerId>
   <commission>Cerdia Leitwarte</commission>
   <type>A</type>
   <shippingConditionId>2</shippingConditionId>
   <items>
      <item>
         <sku>620001</sku>
         <name>Bürotür mit Stahl-U-Zarge (0,76 x 2,135 m)</name>
         <text>Hörmann Stahlfutterzarge VarioFix für Mauerwerk oder TRB<br/>- Drückerhöhe 1050 mm<br/>- Meterrissmarkierung<br/>- Maulweitenkante 15 mm<br/>- Stahlblech verzinkt, Materialstärke 1,5 mm<br/>- Hörmann BaseLine HPL Türblatt<br/>- Türgewicht ca. 18,1 kg/m²<br/>- Türstärke ca. 40,7 mm</text>
         <quantity>1</quantity>
         <quantityUnit>Stk</quantityUnit>
         <price>695.00</price>
         <priceUnit>€</priceUnit>
         <commission>LV-POS. 1.1.10</commission>
      </item>
      ...here there will be as many items as there are in the Service Specification Document (Leistungsverzeichnis)
   </items>
</order>
```

#### Format explanation:

- customerId: The ID of the customer, which should be prompted in the interface.
- commission: The commission for the customer.
- type: The type of the offer; it can be a static value, such as "A," which stands for 'Angebot' (offer).
- shippingConditionId: The ID of the shipping condition, also a static value, for example, "2," which represents shipping with DHL.
- items: The items included in the offer, represented as an array. Each item is an object with the following properties:
  - sku: The SKU of the item, corresponding to the article numbers from the product and service catalog.
  - name: The name of the item.
  - text: The description of the item.
  - quantity: The quantity of the item.
  - quantityUnit: The unit of measurement for the quantity.
  - price: The price of the item.
  - priceUnit: The unit of measurement for the price.
  - commission: The commission for the item.

## Additional Guidelines:

- Supplier Information: Store supplier in item (according to make, only for elements, not for accessories and services)
- Review and List Requirements:
  - Check the specifications and output a list of required trades/articles with page references as preparation for forwarding to manufacturers, including quantities.
  - Example: 50 wooden elements (pp. 7 - 15), 10 steel doors (pp. 16 - 20), 60 fittings (pp. 21 - 23), 3 overhead door closers, 1 revolving door drive.
  - Suggestions for Distribution: Provide suggestions on who the specifications or individual parts can be sent to.
- The UI interface should be easy to use and understand, it should be self explanatory.
- All kinds of advanced UX that simplify the generation of offers are appreciated. For example, a live representation of the offer as a PDF, which users can edit inline before exporting the desired output, would be beneficial.

#### Breakdown by product groups:

- Wooden Doors
- Steel Doors
- Tubular Frame Doors
- Gates
- Steel Frames
- Accessories (such as handle sets, overhead door closers)
- Revolving Door Drives
- Front Doors
- Escape route security / escape door control

#### Identification of specific requirements

- Soundproofing
- Burglary Protection
- Fire Protection
- Smoke Protection
- Wet Room
- Humid Room
- Climate Class
- External Doors
- Post and Beam Construction
- Thermal Insulation (U-Value)
- Radiation Protection
- Accessibility
- Simple Rebate
- Flush
- Double Rebate

## General Overview of Service Specification Document

What is included in the specifications?

- Which products?
- What quantity of each product?
- What requirements do these products have? (Summed up by product group)
- Which brands are required? (Within the product group)
  Example: Wooden doors, 20 pcs, soundproof class 3, climate class 3, rebated, brand Jeld-Wen

List optional positions / on-demand positions separately and do not include them in the total quantity of the product groups.
Provide a separate overview of any additional allowances required in the specifications.
(Example 02, service-specification.pdf: Pos. 01.6 HPL-Beschichtung)

## Product and Service Catalog with article numbers mapping:

### Elements

- Wooden Doors, Wooden Frames - article number: 620001
- Steel Doors, Steel Frames, Tubular Frame Doors - article number: 670001
- Front Doors - article number: 660001
- Glass Doors - article number: 610001
- Gates - article number: 680001
- Extra guideline:
  - The door leaf is decisive. For instance, if a wooden door leaf with a steel frame is listed, classify it under 620001.
  - For glazing, the frame is decisive, such as fixed glazing with steel frame classified under 670001.

### Accessories

- Fittings - article number: 240001
- Door Stoppers - article number: 330001
- Ventilation Grilles - article number: 450001
- Door Closers - article number: 290001
- Locks / Electric Openers - article number: 360001

### Services

- Maintenance - article number: DL8110016
- Hourly Work - article number: DL5010008
- Other Works (e.g. construction site equipment, measurements, sample door leaf, etc.) - article number: DL5019990
