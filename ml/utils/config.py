"""Typed loader for dataset YAML configs (config-driven, per project principles).

The schema is dataset-agnostic so a Porto Seguro config can be added later by
writing another YAML; no code changes required.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .paths import resolve_path


@dataclass
class PathsConfig:
    raw: Path
    processed_dir: Path
    artifacts_dir: Path


@dataclass
class TargetConfig:
    column: str
    classes: list[str]
    label_map: dict[str, str] = field(default_factory=dict)


@dataclass
class CleanConfig:
    leakage_columns: list[str] = field(default_factory=list)
    time_column: str | None = None
    time_derived: str | None = None
    missing_tokens: list[str] = field(default_factory=lambda: ["", "na", "nan", "unknown"])
    categorical_fill_value: str = "Unknown"


@dataclass
class TimeOfDayConfig:
    source: str
    derived: str
    buckets: dict[str, list[int]]  # name -> [start_hour, end_hour] inclusive


@dataclass
class VehicleRule:
    keyword: str
    group: str


@dataclass
class VehicleGroupConfig:
    source: str
    derived: str
    default_group: str = "Other"
    rules: list[VehicleRule] = field(default_factory=list)


@dataclass
class FeatureEngineeringConfig:
    renames: dict[str, str] = field(default_factory=dict)  # engineered_name -> source_column
    time_of_day: TimeOfDayConfig | None = None
    vehicle_type: VehicleGroupConfig | None = None


@dataclass
class FeaturesConfig:
    ordinal: dict[str, list[str]] = field(default_factory=dict)  # name -> ordered categories
    onehot: list[str] = field(default_factory=list)
    numeric: list[str] = field(default_factory=list)

    @property
    def categorical(self) -> list[str]:
        return list(self.ordinal.keys()) + list(self.onehot)

    @property
    def all(self) -> list[str]:
        return self.categorical + list(self.numeric)


@dataclass
class EncodingConfig:
    scale_numeric: bool = False


@dataclass
class BaselineConfig:
    kind: str = "rule_based"  # "rule_based" (Addis) | "logistic" (generic/binary)


@dataclass
class SplitConfig:
    test_size: float = 0.2
    random_state: int = 42
    stratify: bool = True
    k_folds: int = 5


@dataclass
class FeatureSelectionConfig:
    enabled: bool = True
    method: str = "mutual_info"  # "mutual_info" | "model_importance"
    threshold: float = 0.0       # keep features with score >= threshold


@dataclass
class DatasetConfig:
    name: str
    kind: str  # "multiclass" | "binary"
    paths: PathsConfig
    target: TargetConfig
    clean: CleanConfig
    feature_engineering: FeatureEngineeringConfig
    features: FeaturesConfig
    encoding: EncodingConfig = field(default_factory=EncodingConfig)
    split: SplitConfig = field(default_factory=SplitConfig)
    feature_selection: FeatureSelectionConfig = field(default_factory=FeatureSelectionConfig)
    baseline: BaselineConfig = field(default_factory=BaselineConfig)
    random_state: int = 42
    description: str = ""

    @property
    def n_classes(self) -> int:
        return len(self.target.classes)


def _parse_feature_engineering(raw: dict) -> FeatureEngineeringConfig:
    tod_raw = raw.get("time_of_day")
    veh_raw = raw.get("vehicle_type")
    time_of_day = TimeOfDayConfig(**tod_raw) if tod_raw else None
    vehicle_type = None
    if veh_raw:
        rules = [VehicleRule(**r) for r in veh_raw.get("rules", [])]
        vehicle_type = VehicleGroupConfig(
            source=veh_raw["source"],
            derived=veh_raw["derived"],
            default_group=veh_raw.get("default_group", "Other"),
            rules=rules,
        )
    return FeatureEngineeringConfig(
        renames=dict(raw.get("renames", {})),
        time_of_day=time_of_day,
        vehicle_type=vehicle_type,
    )


def load_config(path: str | Path) -> DatasetConfig:
    """Load and validate a dataset config from a YAML file."""
    path = Path(path)
    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    paths_raw = raw["paths"]
    paths = PathsConfig(
        raw=resolve_path(paths_raw["raw"]),
        processed_dir=resolve_path(paths_raw["processed_dir"]),
        artifacts_dir=resolve_path(paths_raw["artifacts_dir"]),
    )

    return DatasetConfig(
        name=raw["name"],
        kind=raw["kind"],
        paths=paths,
        target=TargetConfig(**raw["target"]),
        clean=CleanConfig(**raw.get("clean", {})),
        feature_engineering=_parse_feature_engineering(raw.get("feature_engineering", {})),
        features=FeaturesConfig(**raw.get("features", {})),
        encoding=EncodingConfig(**raw.get("encoding", {})),
        split=SplitConfig(**raw.get("split", {})),
        feature_selection=FeatureSelectionConfig(**raw.get("feature_selection", {})),
        baseline=BaselineConfig(**raw.get("baseline", {})),
        random_state=int(raw.get("random_state", 42)),
        description=raw.get("description", "") or "",
    )
