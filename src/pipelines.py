import time

from abc import ABC
from pathlib import Path

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from models import QuotationItems
from streamlit.delta_generator import DeltaGenerator


class AbstractPipeline(ABC):
    @staticmethod
    def extract_quotation_items_from_pdf(
        pdf_content: str,
        openrouter_api_key: str,
        progress_bar: DeltaGenerator,
    ) -> QuotationItems:
        raise NotImplementedError()


class PipelineV1(AbstractPipeline):
    @staticmethod
    def extract_quotation_items_from_pdf(
        pdf_content: str,
        openrouter_api_key: str,
        progress_bar: DeltaGenerator,
    ) -> QuotationItems:
        llm = ChatOpenAI(
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=openrouter_api_key,
            model="openai/gpt-4o-mini",
        )
        parser = PydanticOutputParser(pydantic_object=QuotationItems)

        path_to_hackathon_challenge_guidelines = (
            Path(__file__).parents[1] / "HackathonChallengeGuidelines.md"
        )

        if not path_to_hackathon_challenge_guidelines.exists():
            raise FileNotFoundError(
                f"File not found: {path_to_hackathon_challenge_guidelines}"
            )

        prompt = PromptTemplate(
            template=path_to_hackathon_challenge_guidelines.read_text()
            + "\nThe following description is an excerpt from a service specification document. The specification might contain multiple requirements. Please extract each requirement separately.\n{text}\n{format_instructions}",
            input_variables=["text"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = LLMChain(llm=llm, prompt=prompt)

        progress_bar.progress(
            0.5,
            "🔍 Extracting, analyzing, and structuring relevant content from the PDF...",
        )
        output = chain.run(text=pdf_content)

        return parser.parse(output)


class PipelineV2(AbstractPipeline):
    @staticmethod
    def extract_quotation_items_from_pdf(
        pdf_content: str,
        openrouter_api_key: str,
        progress_bar: DeltaGenerator,
    ) -> QuotationItems:
        model = ChatOpenAI(
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=openrouter_api_key,
            model="o4-mini-2025-04-16",
        )

        extraction_template = """
        Sie sind ein hochspezialisierter Assistent für die Extraktion von Daten aus deutschen Leistungsverzeichnissen (LVs) im Bauwesen. Ihre Hauptaufgabe ist die präzise und vollständige Extraktion von Ordnungszahlen und den dazugehörigen Leistungsbeschreibungen. Ihre Arbeitsweise ist akribisch und detailorientiert, um höchste Genauigkeit zu gewährleisten.

        Bitte analysiere den folgenden Textauszug aus einem Leistungsverzeichnis. Extrahiere jede einzelne Position und ihre vollständige Leistungsbeschreibung gemäß den unten stehenden detaillierten Anweisungen und Definitionen.

        **Aufgabe:**
        Extrahiere alle Positionen aus dem bereitgestellten LV-Text. Eine Position besteht aus einer Ordnungszahl (OZ) und der dazugehörigen Leistungsbeschreibung.

        **Definitionen und Regeln für die Extraktion:**

        1.  **Ordnungszahl (OZ):**
            * Eine hierarchische Nummerierung, die eine Position eindeutig identifiziert (z.B. `1.`, `1.1.`, `1.1.10`, `1.1.10.A`).
            * Sie steht immer am Anfang der Zeile, die eine neue Position einleitet, eventuell mit führenden Leerzeichen.

        2.  **Leistungsbeschreibung:**
            * Beginnt direkt nach der Ordnungszahl in derselben Zeile und kann sich über mehrere nachfolgende Zeilen erstrecken.
            * Umfasst *allen* beschreibenden Text, inklusive:
                * Detaillierte Material- und Ausführungsangaben.
                * Maßangaben (z.B. `RBLM b/h = 0,76 x 2,135 m`).
                * Hinweise wie `wie Pos. XX, jedoch...`.
                * Zusatzinformationen wie `angebot. Fabrikat: '.................................................'`.
                * Angaben zum `Einbauort: ...`.
                * Markierungen wie `*** Bedarfsposition ohne GB` oder `*** Eventualposition`.
                * Aufzählungen innerhalb der Beschreibung (z.B. mit `•`).
            * Die Leistungsbeschreibung einer Position endet *unmittelbar bevor* eine der folgenden Bedingungen erfüllt ist:
                * Die Zeile(n) mit Mengenangabe, Mengeneinheit (ME), Einheitspreis (EP) und Gesamtbetrag (GB) beginnen (typisches Muster: `X,XXX Stk ......................... .........................` oder `X,XXX Stk ......................... Nur Einh.-Pr.`).
                * Die Ordnungszahl einer *neuen* Position beginnt.
                * Eine klare Summenzeile oder eine Überschrift für einen neuen Abschnitt/Titel beginnt (z.B. `Summe 1.1. ...`, `2. Nächster Titel`).

        3.  **Zu ignorierende Elemente (nicht Teil der Beschreibung oder OZ):**
            * Wiederkehrende Kopfzeilen jeder Seite (z.B. Firmenname wie "SF BAU MOSER GmbH & Co. KG", Adressdaten, Telefonnummern, Projektnamen, LV-Bezeichnung im Kopf).
            * Wiederkehrende Fußzeilen jeder Seite (z.B. "Druckdatum:", "Seite: X von Y").
            * Die allgemeine Spaltenüberschrift-Zeile des LVs (z.B. "Ordnungszahl Leistungsbeschreibung Menge ME Einheitspreis Gesamtbetrag").
            * Leerzeilen, die nicht logisch zur Formatierung einer mehrzeiligen Beschreibung gehören.
            * Die expliziten Werte für Menge, ME, Einheitspreis und Gesamtbetrag selbst. Diese markieren das Ende der Beschreibung.
            * Übergeordnete Titel-Überschriften, die keine auszuführenden Positionen sind (z.B. `1. Innentüren` ist ein Titel, `1.1. Holztüren mit Stahl-U-Zarge` ist auch ein Titel – die extrahierbaren Positionen beginnen typischerweise mit mindestens drei Gliederungsebenen, wie `1.1.10`). Prüfe sorgfältig, ob eine Zeile eine beschreibende Position oder nur eine strukturelle Überschrift ist. Extrahiere nur Zeilen, denen eine Mengenangabe folgen würde.

        **Ausgabeformat:**
        Bitte gib das Ergebnis als eine JSON-Liste von Objekten zurück. Jedes Objekt repräsentiert eine extrahierte Position und muss exakt die folgenden zwei Schlüssel enthalten:
        * `"ordnungszahl"`: Die extrahierte Ordnungszahl als String.
        * `"beschreibung"`: Die vollständige, mehrzeilige Leistungsbeschreibung als einzelner String. Zeilenumbrüche innerhalb der Originalbeschreibung sollen als `\n` im String erhalten bleiben.

        **Wichtige Hinweise zur Genauigkeit:**
        * Stelle sicher, dass die gesamte Leistungsbeschreibung für jede Position erfasst wird, ohne Kürzungen oder Auslassungen.
        * Achte darauf, keine Elemente der Menge/ME/Preis-Zeile oder Kopf-/Fußzeilen in die Beschreibung aufzunehmen.
        * Die Unterscheidung zwischen mehrzeiliger Beschreibung und dem Beginn der Menge/ME/Preis-Zeile ist kritisch.
        * Sei besonders sorgfältig bei Positionen, die sich über Seitenumbrüche erstrecken (obwohl der hier bereitgestellte Text bereits zusammenhängend sein sollte).

        Bitte beginne nun mit der Extraktion aus dem folgenden Text:{input_text}"""

        categorization_template = """# Rolle:  
        Sie sind ein hochspezialisierter KI-Assistent **ausschließlich für türbezogene Bauleistungen**. Ihre Aufgabe ist die präzise Filterung und Kategorisierung von LV-Positionen, die **direkt mit Türen** verbunden sind. Ignorieren Sie rigoros alle nicht-türbezogenen Elemente.

        # Aufgabe:  
        1. **Filterung**: Identifizieren Sie, ob die Position türbezogen ist.  
        2. **Kategorisierung**: Ordnen Sie türbezogene Positionen einer Kategorie (Elemente/Zubehör/Dienstleistungen) und Artikelnummer zu.  
        3. **Ausgabe**: Geben Sie **nur türbezogene Positionen** im JSON-Format aus.

        # Kategorisierungslogik:  

        ## Schritt 1: Türbezug prüfen  
        Eine Position ist **türbezogen**, wenn mindestens eines zutrifft:  
        - Enthält Keywords: *"Tür", "Zarge", "Türblatt", "Schloss", "Band", "Schließer", "Dichtung"*  
        - Bezieht sich auf Einbau, Wartung oder Änderung einer Tür.  

        **Ausschlusskriterien (ignorieren):**  
        - *"Fenster", "Lüftungsgitter", "WC-Beschlag", "Badarmatur", "Treppe", "Fassade", "Wand"* (sofern kein Türbezug)  
        - Allgemeine Baustellenarbeiten (*"Stundenlohn", "Aufmaß"* ohne Türkontext).

        ## Schritt 2: Kategoriezuordnung (nur bei Türbezug)  
        **A. LV-Hierarchie beachten**
        Kapitelstruktur dominiert:
        Beginnt ein Kapitel mit Holztüren (z. B. "1.1"), werden alle Unterpositionen 620001 zugeordnet, sofern nicht explizit Stahl genannt wird.
        Beginnt ein Kapitel mit Stahltüren (z. B. "1.2"), gelten die Stahlregeln.

        **B. Elemente**  
        - **Holztüren (620001)**:  
        - *"Holztürblatt", "Holzzarge", "Spanplatte", "HPL-Tür"*  
        - **Ausnahme**: Stahlzarge + Holztürblatt → 620001.  

        - **Stahltüren (670001)**:  
        - *"Stahlzarge", "Stahl-U-Profil", "Feuerschutztür", "Stahlrahmen"*  
        - **Sonderregel**: Oberlichter/Verglasungen in Stahlzarge → 670001.  

        **C. Zubehör**  
        - **Beschläge (240001)**:  
        - *"Türgriff", "Drückergarnitur", "Band", "Scharnier"*  
        - **Ausschluss**: *"Fenstergriff", "Möbelbeschlag"*.  

        - **Schlösser (360001)**:  
        - *"Einsteckschloss", "3-Punkt-Verriegelung", "Zylinder"*.  

        - **Türschließer (290001)**:  
        - *"Türschließer", "OTS", "GEZE TS"*.  

        **D. Dienstleistungen**  
        - *"Montage von Türen", "Einbau Stahlzarge", "Wartung Türschließer"* → **DL8110016**.  

        # Ausgabeformat:  
        {format_instructions} 

        Text:
        {input_text}
        """

        extraction_prompt = ChatPromptTemplate.from_template(extraction_template)
        extraction_chain = extraction_prompt | model

        progress_bar.progress(
            0.33,
            "🔍 Extracting and analyzing relevant content from the PDF...",
        )
        extraction_result = extraction_chain.invoke({"input_text": pdf_content})

        parser = PydanticOutputParser(pydantic_object=QuotationItems)
        classifcation_prompt = PromptTemplate(
            template=categorization_template,
            input_variables=["input_text"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        classifcation_chain = classifcation_prompt | model

        progress_bar.progress(
            0.66, "🛠️ Classifying and structuring detected requirements..."
        )
        categorization_result = classifcation_chain.invoke(
            {"input_text": extraction_result.content}
        )

        return parser.parse(categorization_result.content)
