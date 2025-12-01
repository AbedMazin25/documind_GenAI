import pandas as pd
from pypdf import PdfReader
import io, re

class FinancialExtractor:
    def extract_tables(self, pdf_bytes: bytes) -> list[pd.DataFrame]:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        tables = []
        for page in reader.pages:
            text = page.extract_text() or ""
            table = self._parse_table(text)
            if table is not None:
                tables.append(table)
        return tables

    def _parse_table(self, text: str):
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        rows = []
        for line in lines:
            cols = re.split(r"\s{2,}", line)
            if len(cols) >= 2:
                rows.append(cols)
        if len(rows) < 3:
            return None
        try:
            return pd.DataFrame(rows[1:], columns=rows[0])
        except Exception:
            return None
