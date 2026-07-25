import termsMarkdown from "../content/terms.md?raw";
import { LegalPageLayout } from "../components/LegalPageLayout";

export function TermsPage() {
  return (
    <LegalPageLayout
      title="Terms of Use"
      description="The terms governing use of the MBERE ML driver-context crash-severity risk platform."
      markdown={termsMarkdown}
    />
  );
}
