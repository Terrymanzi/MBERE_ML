## 1.1 Who this policy covers

This Privacy Policy explains how MBERE ML ("we," "us," "the Platform") collects, uses, stores, and protects information when you use our driver-context crash-severity risk profiling service. It applies to:

- **Registered operators** — insurers, fleet or moto-taxi operators, and system administrators who create accounts to use the Platform.
- **Visitors** to our public pages who have not created an account.

MBERE ML is a research-originated decision-support tool developed as a Bachelor of Software Engineering capstone project at the African Leadership University (ALU), under the supervision of Emmanuel Adjei. It is currently operated as a prototype. This policy describes how it handles data in that capacity, and will be updated if and when the Platform moves beyond a prototype/pilot stage.

**Data controller.** Terry Manzi — African Leadership University capstone project, pending formal business registration — is the data controller for personal data processed through the Platform, for purposes of Rwanda's Law N° 058/2021 Relating to the Protection of Personal Data and Privacy.

## 1.2 What we collect

**Account information.** When you register, we collect your name, email address, organisation, and role (Insurer, Fleet Manager, or System Administrator). Your password is never stored in plain text — it is hashed using bcrypt before storage, and we cannot recover or view your original password.

**Driver and vehicle records you enter.** Operators may create driver-context records for the purpose of requesting a severity-risk assessment. These records may include: driver age band, driving experience, vehicle type, vehicle service year, road surface, weather and light conditions, time of day, and related contextual attributes. **We do not require and do not request full names, national ID numbers, phone numbers, or other direct identifiers of the individual driver as part of the model's feature set** — the underlying model was trained on, and expects, contextual attributes rather than identity fields. If your organisation chooses to store a driver's name or other identifying information alongside a record for your own internal reference, that information is your responsibility to collect lawfully and disclose to the driver in question; MBERE ML does not use it in any prediction.

**Prediction and audit records.** Every risk assessment we generate is persisted together with: the feature record used to produce it, the resulting risk score, band, and class probabilities, the SHAP explanation returned with it, the model version that produced it, and the account that requested it. This audit trail exists so that every prediction is traceable, reviewable, and auditable — it is not optional and cannot be disabled, because it is a structural safeguard against unexplained or unaccountable predictions.

**Technical and log data.** Like most web platforms, we automatically log standard technical data needed to operate and secure the Service — for example authentication timestamps, session tokens (JWT), and basic request metadata.

## 1.3 What the model was and was not trained on

We believe in being specific here rather than vague, because it materially affects what the Platform can and can't tell you about any individual.

- The underlying machine-learning model was trained and evaluated on the **Addis Ababa Road Traffic Accident dataset** (Bedane, 2020; Mendeley Data), a publicly available dataset of 12,316 real crash records from Ethiopia. This dataset **contains no personal identifiers** — no names, no contact details, no identifiers traceable to any individual driver.
- A separate **synthetic Rwandan-context sample**, generated using Tonic Fabricate, was used only to check that the system behaves sensibly on Rwanda-shaped inputs. This sample is **entirely artificial** — it was not derived from, and does not describe, any real person. It was never used to calculate or report any performance metric.
- No real Rwandan institutional crash, insurance, or driver data has been used to train this model as of this writing. Should real institutional data (for example from Rwanda National Police or Rwanda Biomedical Centre) be obtained in future, it would be subject to a separate data-sharing agreement, ethics review, and update to this policy before any use.

## 1.4 How we use your data

We use the information described above to:

- Generate a driver-context severity-risk assessment (a risk band, a risk score, and class probabilities) and an accompanying SHAP explanation for every prediction requested.
- Maintain the audit trail described in §1.2, so that any prediction can be traced back to the model version, inputs, and account that produced it.
- Authenticate accounts and enforce role-based access control between operator and administrator functions.
- Operate, secure, and improve the Platform.

**We do not use your data to make automated pricing, employment, or coverage decisions.** The Platform is designed as human-reviewed decision support. No component of MBERE ML sets a premium, approves or denies coverage, or makes an employment decision automatically. See the Disclaimer and §2.7 of the Terms of Use for more on this.

## 1.5 Legal basis and compliance

MBERE ML processes personal data in accordance with **Law N° 058/2021 of 13/10/2021 Relating to the Protection of Personal Data and Privacy**, Rwanda's data protection statute, which is supervised by the **National Cyber Security Authority (NCSA)**. Where we process personal data, we do so on the basis of your consent (given at account registration), our legitimate interest in operating and securing the Platform, or as necessary to perform our obligations to you as a registered user.

## 1.6 Data storage and security

Account and prediction data is stored in a relational database — SQLite in our development environment, PostgreSQL in production. Authentication uses JSON Web Tokens (JWT), and passwords are hashed with bcrypt before storage. Administrative functions (model training, deployment, user management) are access-controlled separately from operator functions.

We are transparent that, as an academic prototype, MBERE ML's security posture has not undergone an independent third-party security audit or penetration test. We apply standard practices — hashed credentials, token-based authentication, role separation, an immutable audit trail — but we do not claim enterprise-grade or certified security, and you should not submit data you are not comfortable being handled by a system at this maturity level.

## 1.7 Data sharing with third parties

We do not sell your data. We do not share driver-context records, predictions, or account information with third parties for marketing or advertising purposes. We do not currently share data with any external insurer, government body, or commercial partner beyond your own organisation's account.

If MBERE ML enters into a data-sharing arrangement with an institutional partner (for example, Rwanda National Police or Rwanda Biomedical Centre, as contemplated in our research design), any such arrangement would be governed by a separate data-sharing agreement, would require appropriate data-protection and ethics approvals, and this policy would be updated before that sharing began.

## 1.8 Data retention

We retain account information for as long as your account remains active, and prediction/audit records for as long as necessary to preserve the integrity of the audit trail described in §1.2.

## 1.9 Your rights

Subject to Rwandan data protection law, you have the right to:

- Request access to the personal data we hold about you.
- Request correction of inaccurate data.
- Request deletion of your account and associated personal data, subject to our legitimate need to retain audit records for predictions already generated.
- Object to certain kinds of processing.
- Lodge a complaint with the National Cyber Security Authority (NCSA) if you believe your data has been mishandled.

To exercise any of these rights, contact us at terrymanzi@outlook.com.

## 1.10 Children's privacy

MBERE ML is a business-to-business decision-support tool intended for use by adult professionals at insurers and fleet operators. It is not directed at, and we do not knowingly collect data from, children.

## 1.11 Changes to this policy

We may update this Privacy Policy as the Platform evolves — for example, if we move from a prototype to a production deployment, or begin processing real institutional data. We will post the updated policy with a new "Last updated" date, and where changes are material, we will make reasonable efforts to notify registered users directly.

## 1.12 Contact us

Questions about this Privacy Policy or your data can be directed to:

Terry Manzi — Founder & Developer, MBERE ML
terrymanzi@outlook.com
African Leadership University — Bachelor of Software Engineering capstone project
