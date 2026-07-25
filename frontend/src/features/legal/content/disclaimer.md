This Disclaimer forms part of, and should be read together with, the Terms of Use and Privacy Policy.

## 3.1 Academic and prototype status

MBERE ML was developed as a Bachelor of Software Engineering capstone project at the African Leadership University, supervised by Emmanuel Adjei. It is a research prototype, not a certified commercial insurance, actuarial, or risk-management product. It has not been reviewed or approved by Rwanda's National Bank (BNR) or any insurance regulator, and no output from this Platform should be treated as regulator-approved.

## 3.2 Not insurance, actuarial, legal, or financial advice

Nothing produced by MBERE ML constitutes insurance, actuarial, legal, or financial advice. Risk scores, bands, and explanations are decision-support signals only. Any pricing, coverage, or employment decision must be made by a qualified human professional, informed by but not dictated by this Platform's output, and, where relevant, validated through proper actuarial and regulatory processes.

## 3.3 What the risk score actually means

The risk score MBERE ML produces is a **probability-weighted expected-severity index** — specifically, it is calculated as (P(Serious) + 2 × P(Fatal)) ÷ 2, giving a value between 0 and 1, which is then banded into Low, Medium, or High using fixed thresholds (0.34 and 0.67). This is a transparent business rule, not a value learned from data.

**The risk score is not a calibrated probability**, and should not be read as one. No probability calibration (such as Platt scaling or isotonic regression) has been applied, and our own research shows that the resampling techniques used to handle class imbalance can degrade calibration. The score should be interpreted as a **relative ranking signal** for triage and monitoring — useful for comparing contexts against each other — not as a statistically precise probability of any specific outcome.

**The risk score does not predict whether a specific driver will crash.** It estimates the severity a crash tends to have, given a context, drawing on patterns in historical crash records. It says nothing about the likelihood that a crash occurs in the first place.

## 3.4 Known model performance limitations

We disclose these limitations because we believe an honest accounting of what this system can and cannot do is essential to using it responsibly:

- On held-out test data, the best-performing model achieves a macro-F1 score of 0.347, against a transparent rule-based baseline of 0.336 — a real but modest improvement.
- **Recall on the rare, most severe (Fatal) outcome class is near zero.** In our held-out evaluation, the selected model correctly identified none of the 31 true Fatal-severity cases present. This is the most consequential limitation of the system: it is least reliable precisely where the stakes of an outcome are highest.
- Individual features carry weak predictive signal, a limitation of the underlying crash-record data rather than of any particular algorithm — our research systematically tested this and concluded that additional data, not further model tuning, is the more promising path to improvement.

## 3.5 Trained on Ethiopian data, not yet validated on Rwandan data

The model underlying MBERE ML was trained and evaluated exclusively on the Addis Ababa Road Traffic Accident dataset (Bedane, 2020) — real crash records from Ethiopia. **Reported performance figures are Addis-Ababa-only.** Applicability to the Rwandan context has not been demonstrated on real Rwandan data and remains a validation requirement, not an established fact. A separate synthetic Rwandan-context sample has been used only to confirm the system behaves sensibly on Rwanda-shaped inputs — never to report a performance metric — and this check itself has a limited scope (see §3.6).

## 3.6 Synthetic data disclosure

Where MBERE ML's documentation or interface references a "synthetic Rwandan-context" validation, that data was artificially generated using Tonic Fabricate. It does not describe real individuals, vehicles, or crashes, and was never used to calculate or report any performance metric. It exists solely to confirm the pipeline accepts and behaves sensibly on Rwanda-shaped inputs.

## 3.7 No automated pricing, coverage, or employment decisions

MBERE ML explicitly recommends against using driver attributes for automatic insurance pricing on the basis of this model. Any pricing-adjacent use would require independent actuarial and claims validation, probability calibration, and regulatory review beyond the scope of this Platform as currently built. The system contains no capability to automatically set a premium, approve or deny coverage, or make an employment decision — this is a deliberate design choice, not merely a policy statement.

## 3.8 Fairness and non-discrimination

Because severity-risk scores can influence decisions that affect people's livelihoods — insurance costs, employment, access to work — MBERE ML's design includes specific fairness safeguards: certain candidate features (including driver sex) were excluded from the model on the basis of weak predictive signal, which had the additional effect of removing a direct protected attribute; and the system is designed to support a fairness audit of outcomes across age, sex, vehicle type, and vehicle category before any operational recommendation is acted on. We nonetheless acknowledge the well-documented risk of proxy discrimination — that other, retained features may correlate with protected characteristics even after direct ones are removed — and recommend that any organisation using this Platform's output conduct its own disparate-impact review appropriate to its use case.

## 3.9 Human review requirement

Every output from MBERE ML is intended for review by a qualified human decision-maker. It should not be treated as a final, self-executing decision under any circumstances. This requirement is reflected structurally in the Platform — every prediction is delivered with an explanation, precisely so that a human reviewer can assess it — and contractually in §2.7 of the Terms of Use.

## 3.10 No liability for reliance on outputs

To the fullest extent permitted by law, MBERE ML and its developer(s) accept no liability for decisions made, actions taken, or outcomes arising from reliance on any risk score, band, explanation, or other output of this Platform. Use of MBERE ML's output is at your own risk and subject to the Limitation of Liability in §2.12 of the Terms of Use.

---

Questions about any section of this document set can be directed to terrymanzi@outlook.com.
