import { Link } from "react-router-dom";
import type { PredictResponse } from "@/services";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatDateTime } from "@/lib/format";
import { RiskBandMeter } from "./RiskBandMeter";
import { ProbabilityBars } from "./ProbabilityBars";
import { ShapContributions } from "./ShapContributions";

export function PredictionResult({ result }: { result: PredictResponse }) {
  return (
    <div className="space-y-6">
      <Card>
        <CardBody>
          <RiskBandMeter score={result.risk_score} band={result.risk_band} />
          <div className="mt-5 flex flex-wrap items-center gap-2 border-t border-slate-100 pt-5">
            <Badge tone="brand">Predicted: {result.predicted_class}</Badge>
            <Badge tone="neutral">
              {result.model.name} v{result.model.version}
            </Badge>
            <Badge tone="neutral">{result.model.dataset}</Badge>
            {result.driver_id != null && (
              <Link to={`/app/drivers/${result.driver_id}`}>
                <Badge tone="green">Saved to driver #{result.driver_id}</Badge>
              </Link>
            )}
          </div>
          <p className="mt-3 text-xs text-slate-400">
            Assessment #{result.risk_assessment_id} · {formatDateTime(result.created_at)}
          </p>
        </CardBody>
      </Card>

      <Card>
        <CardHeader
          title="Class probabilities"
          description="Model-estimated probability per outcome."
        />
        <CardBody>
          <ProbabilityBars
            probabilities={result.probabilities}
            predictedClass={result.predicted_class}
          />
        </CardBody>
      </Card>

      <Card>
        <CardHeader
          title="Why this prediction"
          description={`Top contributing features (${result.explanation.method.toUpperCase()}).`}
        />
        <CardBody>
          <ShapContributions
            features={result.explanation.top_features}
            method={result.explanation.method}
          />
          <p className="mt-2 text-xs text-slate-400">
            Red increases the predicted-class score; blue decreases it.
          </p>
        </CardBody>
      </Card>
    </div>
  );
}
