"""Step 7: net margin and ROI."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Margin:
    net_sek: int
    roi: float | None


def margin(p25_sek: int, price_sek: int, transport_sek: int, net_ratio: float, fixed_fees_sek: int) -> Margin:
    """net = P25 x net_ratio - fixed_fees - transport - price; roi = net / price (None when price is 0)."""
    net = round(p25_sek * net_ratio - fixed_fees_sek - transport_sek - price_sek)
    return Margin(net, net / price_sek if price_sek > 0 else None)
