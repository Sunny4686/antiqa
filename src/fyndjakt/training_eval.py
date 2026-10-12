"""Evaluate a training round: the AI's verdict per listing against the owner's answer key or his judgement."""

from dataclasses import dataclass

from fyndjakt.pipeline.prefilter import contains_term, normalize

ALERTS = ("FYND", "KOLLA_SJALV")
NONE_WORDS = {"inget", "ingen", "nej", "vanlig", "vanlig möbel"}
# Verdicts the owner can give afterwards with one click on /traning
MANUAL = {
    "korrekt": "Rätt modell",
    "fel_modell": "Fel modell",
    "inte_design": "Ingen designmöbel",
    "missad": "Missad designmöbel",
    "inget": "Rätt: inget",
}


def verdict(expected: str | None, decision: str | None, model_label: str | None) -> str | None:
    """rätt | rätt_inget | fel_modell | falsklarm | missad, or None when there is no answer yet."""
    if not expected or not decision:
        return None
    exp = normalize(expected)
    alert = decision in ALERTS
    if exp in NONE_WORDS:
        return "falsklarm" if alert else "rätt_inget"
    if exp == "korrekt":
        return "rätt"
    if exp in ("fel_modell", "inte_design", "missad"):
        return {"fel_modell": "fel_modell", "inte_design": "falsklarm", "missad": "missad"}[exp]
    # An answer key naming the model: compare with the AI's candidate
    if not alert:
        return "missad"
    label = normalize(model_label or "")
    return "rätt" if label and (contains_term(label, exp) or contains_term(exp, label)) else "fel_modell"


@dataclass
class RoundStats:
    n: int = 0
    answered: int = 0
    alerts: int = 0
    correct: int = 0
    correct_none: int = 0
    wrong_model: int = 0
    false_alarms: int = 0
    missed: int = 0
    cost_usd: float = 0.0

    @property
    def precision(self) -> float | None:
        judged = self.correct + self.wrong_model + self.false_alarms
        return self.correct / judged if judged else None

    @property
    def false_alarm_rate(self) -> float | None:
        """Share of ordinary furniture the AI alerted on."""
        ordinary = self.false_alarms + self.correct_none
        return self.false_alarms / ordinary if ordinary else None

    @property
    def recall(self) -> float | None:
        design = self.correct + self.wrong_model + self.missed
        return self.correct / design if design else None


def summarize(rows: list[tuple[str | None, str | None, float]]) -> RoundStats:
    """rows: (decision, verdict, cost_usd) per listing."""
    s = RoundStats(n=len(rows))
    for decision, v, cost in rows:
        s.cost_usd += cost or 0.0
        s.alerts += decision in ALERTS
        if v is None:
            continue
        s.answered += 1
        if v == "rätt":
            s.correct += 1
        elif v == "rätt_inget":
            s.correct_none += 1
        elif v == "fel_modell":
            s.wrong_model += 1
        elif v == "falsklarm":
            s.false_alarms += 1
        elif v == "missad":
            s.missed += 1
    return s
