from pydantic import BaseModel, Field


class RegressionTrainRequest(BaseModel):
    target_column: str = Field(..., min_length=1)


class RegressionTrainResponse(BaseModel):
    best_model_name: str
    mae: float
    mse: float
    r2_score: float


class ClusteringTrainResponse(BaseModel):
    best_model_name: str
    silhouette_score: float
    clusters_count: int
    cluster_labels: list[int]


class SaveModelResponse(BaseModel):
    saved_file_name: str
