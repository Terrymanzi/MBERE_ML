<!--
DRAFTING NOTE TO TERRY  read before publishing, then delete this comment block.

This document was drafted by Claude (Anthropic) based on your MBERE ML capstone proposal.
It is NOT legal advice. I am not a lawyer, and neither of these documents has been reviewed
by one. Please treat this as a strong first draft, not a final artefact.

Before you publish this anywhere real (a signup form, a live sitemap link), you should:

1. Have a Rwandan-qualified lawyer review it  particularly the Terms of Use liability,
   indemnification, and governing-law clauses, which are the highest-risk sections to get
   wrong, and the Privacy Policy's compliance claims, since MBERE ML would be a "data
   controller" under Rwandan law the moment it stores a real operator's account or a real
   driver record.
2. Fill in every [BRACKETED PLACEHOLDER]  legal entity name, contact email, physical
   address, effective date. I've left these open because I don't know them and won't guess.
3. Decide your actual data-hosting location and retention periods precisely  I've used
   conservative, generic language where your report doesn't specify exact numbers (e.g.
   "as long as necessary," rather than inventing a retention period in days).
4. Register with Rwanda's National Cyber Security Authority (NCSA) as the data protection
   supervisory authority if you process any real personal data operationally  this is a
   legal requirement under Law N° 058/2021, not just a courtesy. For an academic capstone
   demo running on synthetic/test accounts, this is very likely not yet triggered, but it
   is the moment you use real driver names, real emails beyond your own testing, or real
   Rwandan institutional data.

Grounding used:
- Rwanda's data protection statute is Law N° 058/2021 of 13/10/2021 Relating to the
  Protection of Personal Data and Privacy, in force since 15/10/2021, supervised by the
  National Cyber Security Authority (NCSA). Verified via web search on 25 July 2026 against
  RwandaLII, RISA, and the NCSA's own Data Protection & Privacy Office. Administrative
  penalties under the law run RWF 2,000,000–5,000,000, or 1% of global turnover for
  corporate bodies  I've referenced this factually, not as legal advice.
- Every technical and methodological claim below (what data the model was trained on, what
  the risk score does and doesn't mean, what limitations are disclosed, what the system
  guardrails are) is pulled directly from your capstone proposal, not invented. Where your
  report doesn't specify something (e.g. an exact data retention period, a named DPO, a
  physical office address), I've left a placeholder rather than fabricate one.

Delete this comment block before publishing  it's for you, not your users.
-->

# MBERE ML Legal Terms

**Document set:** Privacy Policy · Terms of Use · Disclaimer
**Effective date:** 6th July 2026
**Last updated:** 25th July 2026
**Applies to:** the MBERE ML web platform, API, and any associated mobile or desktop clients (together, the "Platform" or "Service")

> These three documents can be published as one combined page or split into three linked pages (e.g. `/privacy`, `/terms`, `/disclaimer`) from your site footer or signup form. Each section is written to stand alone if split out.

---

# 1. Privacy Policy

## 1.1 Who this policy covers

This Privacy Policy explains how MBERE ML ("we," "us," "the Platform") collects, uses, stores, and protects information when you use our driver-context crash-severity risk profiling service. It applies to:

- **Registered operators** insurers, fleet or moto-taxi operators, and system administrators who create accounts to use the Platform.
- **Visitors** to our public pages who have not created an account.

MBERE ML is a research-originated decision-support tool developed as a Bachelor of Software Engineering capstone project at the African Leadership University (ALU), under the supervision of Emmanuel Adjei. It is currently operated as a prototype. This policy describes how it handles data in that capacity, and will be updated if and when the Platform moves beyond a prototype/pilot stage.

**Data controller.** [LEGAL ENTITY NAME / TERRY MANZI, PENDING FORMAL REGISTRATION] is the data controller for personal data processed through the Platform, for purposes of Rwanda's Law N° 058/2021 Relating to the Protection of Personal Data and Privacy.

## 1.2 What we collect

**Account information.** When you register, we collect your name, email address, organisation, and role (Insurer, Fleet Manager, or System Administrator). Your password is never stored in plain text it is hashed using bcrypt before storage, and we cannot recover or view your original password.

**Driver and vehicle records you enter.** Operators may create driver-context records for the purpose of requesting a severity-risk assessment. These records may include: driver age band, driving experience, vehicle type, vehicle service year, road surface, weather and light conditions, time of day, and related contextual attributes. **We do not require and do not request full names, national ID numbers, phone numbers, or other direct identifiers of the individual driver as part of the model's feature set** the underlying model was trained on, and expects, contextual attributes rather than identity fields. If your organisation chooses to store a driver's name or other identifying information alongside a record for your own internal reference, that information is your responsibility to collect lawfully and disclose to the driver in question; MBERE ML does not use it in any prediction.

**Prediction and audit records.** Every risk assessment we generate is persisted together with: the feature record used to produce it, the resulting risk score, band, and class probabilities, the SHAP explanation returned with it, the model version that produced it, and the account that requested it. This audit trail exists so that every prediction is traceable, reviewable, and auditable it is not optional and cannot be disabled, because it is a structural safeguard against unexplained or unaccountable predictions.

**Technical and log data.** Like most web platforms, we automatically log standard technical data needed to operate and secure the Service for example authentication timestamps, session tokens (JWT), and basic request metadata. [Terry: if you add analytics, cookies, or third-party trackers, describe them here specifically this section currently only covers what your report's tech stack implies.]

## 1.3 What the model was and was not trained on

We believe in being specific here rather than vague, because it materially affects what the Platform can and can't tell you about any individual.

- The underlying machine-learning model was trained and evaluated on the **Addis Ababa Road Traffic Accident dataset** (Bedane, 2020; Mendeley Data), a publicly available dataset of 12,316 real crash records from Ethiopia. This dataset **contains no personal identifiers** no names, no contact details, no identifiers traceable to any individual driver.
- A separate **synthetic Rwandan-context sample**, generated using Tonic Fabricate, was used only to check that the system behaves sensibly on Rwanda-shaped inputs. This sample is **entirely artificial** it was not derived from, and does not describe, any real person. It was never used to calculate or report any performance metric.
- No real Rwandan institutional crash, insurance, or driver data has been used to train this model as of this writing. Should real institutional data (for example from Rwanda National Police or Rwanda Biomedical Centre) be obtained in future, it would be subject to a separate data-sharing agreement, ethics review, and update to this policy before any use.

## 1.4 How we use your data

We use the information described above to:

- Generate a driver-context severity-risk assessment (a risk band, a risk score, and class probabilities) and an accompanying SHAP explanation for every prediction requested.
- Maintain the audit trail described in §1.2, so that any prediction can be traced back to the model version, inputs, and account that produced it.
- Authenticate accounts and enforce role-based access control between operator and administrator functions.
- Operate, secure, and improve the Platform.

**We do not use your data to make automated pricing, employment, or coverage decisions.** The Platform is designed as human-reviewed decision support. No component of MBERE ML sets a premium, approves or denies coverage, or makes an employment decision automatically. See the Disclaimer (Part 3) and §2.7 of the Terms of Use for more on this.

## 1.5 Legal basis and compliance

MBERE ML processes personal data in accordance with **Law N° 058/2021 of 13/10/2021 Relating to the Protection of Personal Data and Privacy**, Rwanda's data protection statute, which is supervised by the **National Cyber Security Authority (NCSA)**. Where we process personal data, we do so on the basis of your consent (given at account registration), our legitimate interest in operating and securing the Platform, or as necessary to perform our obligations to you as a registered user.

[Terry: if the Platform moves beyond an academic prototype and begins processing real personal data at any meaningful scale, you are required under this law to maintain a formal Record of Processing Activities and may be required to register with, or notify, the NCSA. This is a genuine legal obligation, not boilerplate confirm the current registration threshold and process directly with the NCSA or a Rwandan data protection lawyer before scaling up.]

## 1.6 Data storage and security

Account and prediction data is stored in a relational database SQLite in our development environment, PostgreSQL in production. Authentication uses JSON Web Tokens (JWT), and passwords are hashed with bcrypt before storage. Administrative functions (model training, deployment, user management) are access-controlled separately from operator functions.

We are transparent that, as an academic prototype, MBERE ML's security posture has not undergone an independent third-party security audit or penetration test. We apply standard practices hashed credentials, token-based authentication, role separation, an immutable audit trail but we do not claim enterprise-grade or certified security, and you should not submit data you are not comfortable being handled by a system at this maturity level.

## 1.7 Data sharing with third parties

We do not sell your data. We do not share driver-context records, predictions, or account information with third parties for marketing or advertising purposes. We do not currently share data with any external insurer, government body, or commercial partner beyond your own organisation's account.

If MBERE ML enters into a data-sharing arrangement with an institutional partner (for example, Rwanda National Police or Rwanda Biomedical Centre, as contemplated in our research design), any such arrangement would be governed by a separate data-sharing agreement, would require appropriate data-protection and ethics approvals, and this policy would be updated before that sharing began.

## 1.8 Data retention

We retain account information for as long as your account remains active, and prediction/audit records for as long as necessary to preserve the integrity of the audit trail described in §1.2. [Terry: if you have or adopt a specific retention period e.g. "prediction records are retained for 24 months after an account is closed" insert it here. Vague retention language is a common weak point in data protection reviews, so a concrete number is worth adding once you've decided one.]

## 1.9 Your rights

Subject to Rwandan data protection law, you have the right to:

- Request access to the personal data we hold about you.
- Request correction of inaccurate data.
- Request deletion of your account and associated personal data, subject to our legitimate need to retain audit records for predictions already generated.
- Object to certain kinds of processing.
- Lodge a complaint with the National Cyber Security Authority (NCSA) if you believe your data has been mishandled.

To exercise any of these rights, contact us at [INSERT CONTACT EMAIL].

## 1.10 Children's privacy

MBERE ML is a business-to-business decision-support tool intended for use by adult professionals at insurers and fleet operators. It is not directed at, and we do not knowingly collect data from, children.

## 1.11 Changes to this policy

We may update this Privacy Policy as the Platform evolves for example, if we move from a prototype to a production deployment, or begin processing real institutional data. We will post the updated policy with a new "Last updated" date, and where changes are material, we will make reasonable efforts to notify registered users directly.

## 1.12 Contact us

Questions about this Privacy Policy or your data can be directed to:

[INSERT CONTACT NAME / ROLE]
[INSERT CONTACT EMAIL]
[INSERT ORGANISATION / INSTITUTIONAL AFFILIATION, e.g. African Leadership University capstone project]

---

# 2. Terms of Use Agreement

## 2.1 Acceptance of these terms

By creating an account or otherwise accessing MBERE ML, you agree to be bound by these Terms of Use, our Privacy Policy (Part 1), and our Disclaimer (Part 3). If you do not agree, do not use the Platform. If you are agreeing on behalf of an organisation (an insurer or fleet operator), you confirm you have authority to bind that organisation to these terms.

## 2.2 What MBERE ML is and is not

This is the single most important section of these terms, and we want it stated plainly rather than buried in fine print.

**MBERE ML estimates driver-context crash-severity risk among recorded crashes.** Given a driver, vehicle, and environmental context, it estimates how severe a crash outcome tends to be in similar contexts, based on patterns learned from historical crash records. It expresses this as a risk band (Low, Medium, or High), a risk score, and class probabilities, together with an explanation of which factors most influenced that specific prediction.

**MBERE ML does not predict whether a specific individual driver will crash in the future.** It is not a prospective per-driver risk model, it does not use telematics, trip, or exposure data, and it makes no claim about any named individual's likelihood of being involved in a crash. The distinction matters: the underlying data describes crashes that occurred, with contextual attributes attached it does not describe a population of drivers with and without crashes, and cannot support that kind of prediction. Any output from this Platform should be read as a _contextual severity-risk signal_, not as a statement about a specific person's future behaviour.

## 2.3 Eligibility and account roles

The Platform supports three account roles:

- **Insurer** for portfolio risk monitoring and as an input to risk-based decision processes (subject to §2.7 below).
- **Fleet or moto-taxi operator** for targeting driver safety interventions, training, and check-ins.
- **System Administrator** for platform, model, and user-account operations.

You must provide accurate registration information and are responsible for maintaining the confidentiality of your account credentials. You are responsible for all activity that occurs under your account.

## 2.4 Permitted use

You may use MBERE ML to:

- Request driver-context severity-risk assessments for legitimate portfolio-monitoring or safety-intervention purposes.
- Review risk assessments, explanations, and risk history within your organisation's account.
- Use the platform's analytics and dashboard views to inform human decision-making within your organisation.

## 2.5 Prohibited use

You may not:

- Use the Platform to make, or as the sole basis for, an automated decision about an individual's insurance premium, coverage eligibility, or employment status.
- Attempt to reverse-engineer, extract, or misuse the underlying model, training data, or feature contract beyond ordinary use of the Platform's published API.
- Use the Platform to profile, discriminate against, or take adverse action against an individual on the basis of a protected characteristic (including but not limited to sex, ethnicity, or disability), whether directly or through a feature that acts as a proxy for one.
- Submit data you do not have a lawful basis to collect and process.
- Interfere with, disrupt, or attempt unauthorised access to the Platform, its API, or its underlying infrastructure.
- Represent the Platform's outputs as certified, regulator-approved, or actuarially validated risk assessments, unless and until they are.

## 2.6 Accuracy of data you provide

Driver-context records are entered by your organisation. MBERE ML is not responsible for, and disclaims liability arising from, inaccurate, incomplete, or misleading data entered by you or your organisation. The quality of any risk assessment depends directly on the quality of the input data.

## 2.7 No automated decision-making human review is required

**MBERE ML must not be used to automatically set insurance premiums, approve or deny coverage, or make employment decisions.** Every output is decision support for a human reviewer, not a final decision in itself. This is a condition of use, not merely a recommendation: our own research explicitly identifies uncalibrated risk scores and near-zero recall on the rarest, most severe outcome class as reasons this system is unsuited to fully automated, high-stakes decisions. Any use of MBERE ML outputs as an input to pricing must be accompanied by independent actuarial validation, calibration, and regulatory review by your organisation obligations that rest with you, not with MBERE ML.

## 2.8 Model limitations and no warranty

The Platform, its predictions, risk scores, and explanations are provided **"as is" and "as available,"** without warranty of any kind, express or implied, including without limitation any warranty of accuracy, reliability, merchantability, or fitness for a particular purpose. Specific, known limitations including modest overall performance relative to a transparent baseline, near-zero recall on the rare Fatal-severity class, and domain shift between the Ethiopian training data and the Rwandan operating context are disclosed in full in our Disclaimer (Part 3), which forms part of these Terms.

## 2.9 Intellectual property

The Platform's software, model architecture, documentation, and branding are the property of [TERRY MANZI / LEGAL ENTITY, PENDING] and, where applicable, African Leadership University. Your driver-context data and any records you create remain your property; by using the Platform you grant us a licence to process that data solely to provide the Service, as described in the Privacy Policy.

## 2.10 Fees

[As of this writing MBERE ML is operated as a non-commercial academic prototype and no fees are charged. If you introduce pricing, add a fees/billing section here before publishing.]

## 2.11 Suspension and termination

We may suspend or terminate your account if you violate these Terms, in particular the prohibited uses in §2.5. You may close your account at any time; §1.8 describes how your data is handled afterward.

## 2.12 Limitation of liability

To the maximum extent permitted by applicable law, MBERE ML and its developer(s) shall not be liable for any indirect, incidental, special, consequential, or punitive damages, or any loss of profits, revenue, data, or business opportunity, arising from or related to your use of the Platform, including any decision made or action taken in reliance on a risk assessment it produced. **[Terry: this clause, and the indemnification clause below, are exactly the kind of provisions that need a qualified lawyer's review before publication courts vary widely in how much of a liability limitation they'll actually enforce, especially where an insurance-adjacent decision is involved, and getting this wrong could leave you personally exposed rather than protected.]**

## 2.13 Indemnification

You agree to indemnify and hold harmless MBERE ML and its developer(s) from any claim, loss, or damage arising from your misuse of the Platform, your violation of these Terms, or your violation of any applicable law, including any decision your organisation makes about an individual using MBERE ML's output as a factor.

## 2.14 Governing law

These Terms are governed by the laws of the Republic of Rwanda. [Terry: confirm this is actually where you want disputes resolved and whether you want to specify a particular court or arbitration mechanism a lawyer should finalise this clause.]

## 2.15 Changes to these terms

We may update these Terms as the Platform evolves. Continued use of the Platform after an update constitutes acceptance of the revised Terms.

## 2.16 Contact

[INSERT CONTACT EMAIL]

---

# 3. Disclaimer

This Disclaimer forms part of, and should be read together with, the Terms of Use (Part 2) and Privacy Policy (Part 1).

## 3.1 Academic and prototype status

MBERE ML was developed as a Bachelor of Software Engineering capstone project at the African Leadership University, supervised by Emmanuel Adjei. It is a research prototype, not a certified commercial insurance, actuarial, or risk-management product. It has not been reviewed or approved by Rwanda's National Bank (BNR) or any insurance regulator, and no output from this Platform should be treated as regulator-approved.

## 3.2 Not insurance, actuarial, legal, or financial advice

Nothing produced by MBERE ML constitutes insurance, actuarial, legal, or financial advice. Risk scores, bands, and explanations are decision-support signals only. Any pricing, coverage, or employment decision must be made by a qualified human professional, informed by but not dictated by this Platform's output, and, where relevant, validated through proper actuarial and regulatory processes.

## 3.3 What the risk score actually means

The risk score MBERE ML produces is a **probability-weighted expected-severity index** specifically, it is calculated as (P(Serious) + 2 × P(Fatal)) ÷ 2, giving a value between 0 and 1, which is then banded into Low, Medium, or High using fixed thresholds (0.34 and 0.67). This is a transparent business rule, not a value learned from data.

**The risk score is not a calibrated probability**, and should not be read as one. No probability calibration (such as Platt scaling or isotonic regression) has been applied, and our own research shows that the resampling techniques used to handle class imbalance can degrade calibration. The score should be interpreted as a **relative ranking signal** for triage and monitoring useful for comparing contexts against each other not as a statistically precise probability of any specific outcome.

**The risk score does not predict whether a specific driver will crash.** It estimates the severity a crash tends to have, given a context, drawing on patterns in historical crash records. It says nothing about the likelihood that a crash occurs in the first place.

## 3.4 Known model performance limitations

We disclose these limitations because we believe an honest accounting of what this system can and cannot do is essential to using it responsibly:

- On held-out test data, the best-performing model achieves a macro-F1 score of 0.347, against a transparent rule-based baseline of 0.336 a real but modest improvement.
- **Recall on the rare, most severe (Fatal) outcome class is near zero.** In our held-out evaluation, the selected model correctly identified none of the 31 true Fatal-severity cases present. This is the most consequential limitation of the system: it is least reliable precisely where the stakes of an outcome are highest.
- Individual features carry weak predictive signal, a limitation of the underlying crash-record data rather than of any particular algorithm our research systematically tested this and concluded that additional data, not further model tuning, is the more promising path to improvement.

## 3.5 Trained on Ethiopian data, not yet validated on Rwandan data

The model underlying MBERE ML was trained and evaluated exclusively on the Addis Ababa Road Traffic Accident dataset (Bedane, 2020) real crash records from Ethiopia. **Reported performance figures are Addis-Ababa-only.** Applicability to the Rwandan context has not been demonstrated on real Rwandan data and remains a validation requirement, not an established fact. A separate synthetic Rwandan-context sample has been used only to confirm the system behaves sensibly on Rwanda-shaped inputs never to report a performance metric and this check itself has a limited scope (see §3.6).

## 3.6 Synthetic data disclosure

Where MBERE ML's documentation or interface references a "synthetic Rwandan-context" validation, that data was artificially generated using Tonic Fabricate. It does not describe real individuals, vehicles, or crashes, and was never used to calculate or report any performance metric. It exists solely to confirm the pipeline accepts and behaves sensibly on Rwanda-shaped inputs.

## 3.7 No automated pricing, coverage, or employment decisions

MBERE ML explicitly recommends against using driver attributes for automatic insurance pricing on the basis of this model. Any pricing-adjacent use would require independent actuarial and claims validation, probability calibration, and regulatory review beyond the scope of this Platform as currently built. The system contains no capability to automatically set a premium, approve or deny coverage, or make an employment decision this is a deliberate design choice, not merely a policy statement.

## 3.8 Fairness and non-discrimination

Because severity-risk scores can influence decisions that affect people's livelihoods insurance costs, employment, access to work MBERE ML's design includes specific fairness safeguards: certain candidate features (including driver sex) were excluded from the model on the basis of weak predictive signal, which had the additional effect of removing a direct protected attribute; and the system is designed to support a fairness audit of outcomes across age, sex, vehicle type, and vehicle category before any operational recommendation is acted on. We nonetheless acknowledge the well-documented risk of proxy discrimination that other, retained features may correlate with protected characteristics even after direct ones are removed and recommend that any organisation using this Platform's output conduct its own disparate-impact review appropriate to its use case.

## 3.9 Human review requirement

Every output from MBERE ML is intended for review by a qualified human decision-maker. It should not be treated as a final, self-executing decision under any circumstances. This requirement is reflected structurally in the Platform every prediction is delivered with an explanation, precisely so that a human reviewer can assess it and contractually in §2.7 of the Terms of Use.

## 3.10 No liability for reliance on outputs

To the fullest extent permitted by law, MBERE ML and its developer(s) accept no liability for decisions made, actions taken, or outcomes arising from reliance on any risk score, band, explanation, or other output of this Platform. Use of MBERE ML's output is at your own risk and subject to the Limitation of Liability in §2.12 of the Terms of Use.

---

_End of document set. Questions about any section: [INSERT CONTACT EMAIL]._
