import pandas as pd
from pypdf import PdfReader
import io, re
import numpy as np

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

    def compute_ratios(self, income_df: pd.DataFrame, balance_df: pd.DataFrame) -> dict:
        def safe_get(df, key):
            row = df[df.iloc[:, 0].str.contains(key, case=False, na=False)]
            if row.empty:
                return np.nan
            try:
                return float(str(row.iloc[0, 1]).replace(",", "").replace("$", ""))
            except Exception:
                return np.nan

        revenue = safe_get(income_df, "Revenue|Net Sales")
        net_income = safe_get(income_df, "Net Income")
        total_assets = safe_get(balance_df, "Total Assets")
        equity = safe_get(balance_df, "Stockholders Equity|Total Equity")

        return {
            "profit_margin": net_income / revenue if revenue else None,
            "roa": net_income / total_assets if total_assets else None,
            "roe": net_income / equity if equity else None,
        }

    def dcf_valuation(
        self,
        free_cash_flows: list[float],
        wacc: float,
        terminal_growth: float = 0.03,
    ) -> dict:
        pv_fcfs = []
        for i, fcf in enumerate(free_cash_flows, 1):
            pv_fcfs.append(fcf / (1 + wacc) ** i)
        terminal_value = free_cash_flows[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
        pv_terminal = terminal_value / (1 + wacc) ** len(free_cash_flows)
        enterprise_value = sum(pv_fcfs) + pv_terminal
        return {
            "pv_fcfs": pv_fcfs,
            "terminal_value": terminal_value,
            "pv_terminal": pv_terminal,
            "enterprise_value": enterprise_value,
        }
