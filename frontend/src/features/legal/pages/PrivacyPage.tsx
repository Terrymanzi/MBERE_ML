import privacyMarkdown from "../content/privacy.md?raw";
import { LegalPageLayout } from "../components/LegalPageLayout";

export function PrivacyPage() {
  return (
    <LegalPageLayout
      title="Privacy Policy"
      description="How MBERE ML collects, uses, stores, and protects your information."
      markdown={privacyMarkdown}
    />
  );
}
