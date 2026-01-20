"""Payment section parsers.

Each parser handles ONE section (SRP).
"""

from linkedin2md.parsers.base import BaseParser
from linkedin2md.registry import register_parser


@register_parser
class ReceiptsParser(BaseParser):
    """Parse payment receipts from both v1 and v2 formats."""

    @property
    def section_key(self) -> str:
        return "receipts"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        receipts = self._merge_csv_sources(raw_data, ["receipts", "receipts_v2"])
        result = []

        for r in receipts:
            date = r.get("Transaction Made At", "")

            entry = {
                "date": date or None,
                "description": r.get("Description", "") or None,
                "amount": r.get("Total Amount", "") or None,
                "currency": r.get("Currency Code", "") or None,
                "payment_method": r.get("Payment Method Type", "") or None,
                "invoice_number": r.get("Invoice Number", "") or None,
            }
            result.append(entry)

        return result
