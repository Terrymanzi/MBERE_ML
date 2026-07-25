import disclaimerMarkdown from "../content/disclaimer.md?raw";
import { LegalPageLayout } from "../components/LegalPageLayout";

export function DisclaimerPage() {
  return (
    <LegalPageLayout
      title="Disclaimer"
      description="Important limitations and disclosures about MBERE ML's risk model and outputs."
      markdown={disclaimerMarkdown}
    />
  );
}
