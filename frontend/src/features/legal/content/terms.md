## 2.1 Acceptance of these terms

By creating an account or otherwise accessing MBERE ML, you agree to be bound by these Terms of Use, our Privacy Policy, and our Disclaimer. If you do not agree, do not use the Platform. If you are agreeing on behalf of an organisation (an insurer or fleet operator), you confirm you have authority to bind that organisation to these terms.

## 2.2 What MBERE ML is and is not

This is the single most important section of these terms, and we want it stated plainly rather than buried in fine print.

**MBERE ML estimates driver-context crash-severity risk among recorded crashes.** Given a driver, vehicle, and environmental context, it estimates how severe a crash outcome tends to be in similar contexts, based on patterns learned from historical crash records. It expresses this as a risk band (Low, Medium, or High), a risk score, and class probabilities, together with an explanation of which factors most influenced that specific prediction.

**MBERE ML does not predict whether a specific individual driver will crash in the future.** It is not a prospective per-driver risk model, it does not use telematics, trip, or exposure data, and it makes no claim about any named individual's likelihood of being involved in a crash. The distinction matters: the underlying data describes crashes that occurred, with contextual attributes attached — it does not describe a population of drivers with and without crashes, and cannot support that kind of prediction. Any output from this Platform should be read as a _contextual severity-risk signal_, not as a statement about a specific person's future behaviour.

## 2.3 Eligibility and account roles

The Platform supports three account roles:

- **Insurer** — for portfolio risk monitoring and as an input to risk-based decision processes (subject to §2.7 below).
- **Fleet or moto-taxi operator** — for targeting driver safety interventions, training, and check-ins.
- **System Administrator** — for platform, model, and user-account operations.

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

## 2.7 No automated decision-making — human review is required

**MBERE ML must not be used to automatically set insurance premiums, approve or deny coverage, or make employment decisions.** Every output is decision support for a human reviewer, not a final decision in itself. This is a condition of use, not merely a recommendation: our own research explicitly identifies uncalibrated risk scores and near-zero recall on the rarest, most severe outcome class as reasons this system is unsuited to fully automated, high-stakes decisions. Any use of MBERE ML outputs as an input to pricing must be accompanied by independent actuarial validation, calibration, and regulatory review by your organisation — obligations that rest with you, not with MBERE ML.

## 2.8 Model limitations and no warranty

The Platform, its predictions, risk scores, and explanations are provided **"as is" and "as available,"** without warranty of any kind, express or implied, including without limitation any warranty of accuracy, reliability, merchantability, or fitness for a particular purpose. Specific, known limitations — including modest overall performance relative to a transparent baseline, near-zero recall on the rare Fatal-severity class, and domain shift between the Ethiopian training data and the Rwandan operating context — are disclosed in full in our Disclaimer, which forms part of these Terms.

## 2.9 Intellectual property

The Platform's software, model architecture, documentation, and branding are the property of Terry Manzi and, where applicable, African Leadership University. Your driver-context data and any records you create remain your property; by using the Platform you grant us a licence to process that data solely to provide the Service, as described in the Privacy Policy.

## 2.10 Fees

As of this writing, MBERE ML is operated as a non-commercial academic prototype and no fees are charged. This section will be updated if pricing is introduced.

## 2.11 Suspension and termination

We may suspend or terminate your account if you violate these Terms, in particular the prohibited uses in §2.5. You may close your account at any time; §1.8 of the Privacy Policy describes how your data is handled afterward.

## 2.12 Limitation of liability

To the maximum extent permitted by applicable law, MBERE ML and its developer(s) shall not be liable for any indirect, incidental, special, consequential, or punitive damages, or any loss of profits, revenue, data, or business opportunity, arising from or related to your use of the Platform, including any decision made or action taken in reliance on a risk assessment it produced.

## 2.13 Indemnification

You agree to indemnify and hold harmless MBERE ML and its developer(s) from any claim, loss, or damage arising from your misuse of the Platform, your violation of these Terms, or your violation of any applicable law, including any decision your organisation makes about an individual using MBERE ML's output as a factor.

## 2.14 Governing law

These Terms are governed by the laws of the Republic of Rwanda.

## 2.15 Changes to these terms

We may update these Terms as the Platform evolves. Continued use of the Platform after an update constitutes acceptance of the revised Terms.

## 2.16 Contact

terrymanzi@outlook.com
