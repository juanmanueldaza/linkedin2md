"""Payment section formatters.

Each formatter handles ONE section (SRP).
"""

from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class ReceiptsFormatter(BaseFormatter):
    """Format receipts section."""

    @property
    def section_key(self) -> str:
        return "receipts"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Payment Receipts", ""]
        lines.append("| Date | Description | Amount | Currency |")
        lines.append("|------|-------------|--------|----------|")

        for receipt in data:
            date = self._escape_table_cell(receipt.get("date", ""))
            desc = self._escape_table_cell(receipt.get("description", ""))
            amount = self._escape_table_cell(receipt.get("amount", ""))
            currency = self._escape_table_cell(receipt.get("currency", ""))
            lines.append(f"| {date} | {desc} | {amount} | {currency} |")

        lines.append("")
        return "\n".join(lines)
