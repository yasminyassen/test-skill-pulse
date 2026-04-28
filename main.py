from __future__ import annotations

from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.ml import train_clustering, train_regression
from app.schemas import (
    ClusteringTrainResponse,
    RegressionTrainRequest,
    RegressionTrainResponse,
    SaveModelResponse,
)
from app.state import STATE


BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="AutoML Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_uploaded_file(file: UploadFile) -> pd.DataFrame:
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()

    try:
        if suffix == ".csv":
            return pd.read_csv(file.file)
        if suffix == ".xlsx":
            return pd.read_excel(file.file)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {exc}") from exc

    raise HTTPException(status_code=400, detail="Only .csv and .xlsx files are supported.")


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload")
def upload_dataset(file: UploadFile = File(...)) -> dict:
    df = _load_uploaded_file(file)

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded dataset is empty.")

    STATE.uploaded_df = df.copy()
    STATE.uploaded_filename = file.filename

    preview_rows = df.head(5).where(pd.notnull(df.head(5)), None).to_dict(orient="records")

    return {
        "message": "Dataset uploaded successfully.",
        "columns": df.columns.tolist(),
        "preview_rows": preview_rows,
        "rows_count": int(df.shape[0]),
    }


@app.post("/train/regression", response_model=RegressionTrainResponse)
def train_regression_endpoint(payload: RegressionTrainRequest) -> RegressionTrainResponse:
    if STATE.uploaded_df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded. Use /upload first.")

    try:
        result = train_regression(STATE.uploaded_df, payload.target_column)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Regression training failed: {exc}") from exc

    STATE.trained_bundle = {
        "task": "regression",
        "best_model_name": result.best_model_name,
        "pipeline": result.best_pipeline,
        "metrics": {
            "mae": result.mae,
            "mse": result.mse,
            "r2_score": result.r2_score,
        },
    }
    STATE.trained_task = "regression"

    return RegressionTrainResponse(
        best_model_name=result.best_model_name,
        mae=result.mae,
        mse=result.mse,
        r2_score=result.r2_score,
    )


@app.post("/train/clustering", response_model=ClusteringTrainResponse)
def train_clustering_endpoint() -> ClusteringTrainResponse:
    if STATE.uploaded_df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded. Use /upload first.")

    try:
        result = train_clustering(STATE.uploaded_df)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Clustering training failed: {exc}") from exc

    STATE.trained_bundle = {
        "task": "clustering",
        "best_model_name": result.best_model_name,
        "pipeline": result.best_pipeline,
        "metrics": {
            "silhouette_score": result.silhouette_score,
            "clusters_count": result.clusters_count,
        },
    }
    STATE.trained_task = "clustering"

    return ClusteringTrainResponse(
        best_model_name=result.best_model_name,
        silhouette_score=result.silhouette_score,
        clusters_count=result.clusters_count,
        cluster_labels=result.cluster_labels,
    )


@app.post("/save-model", response_model=SaveModelResponse)
def save_model() -> SaveModelResponse:
    if STATE.trained_bundle is None or STATE.trained_task is None:
        raise HTTPException(status_code=400, detail="No trained model found. Train first.")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"{STATE.trained_task}_model_{timestamp}.joblib"
    output_path = ARTIFACTS_DIR / file_name

    try:
        joblib.dump(STATE.trained_bundle, output_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save model: {exc}") from exc

    STATE.last_saved_model_path = output_path
    return SaveModelResponse(saved_file_name=file_name)


@app.get("/download-model")
def download_model() -> FileResponse:
    if STATE.last_saved_model_path is None or not STATE.last_saved_model_path.exists():
        raise HTTPException(status_code=404, detail="No saved model found. Use /save-model first.")

    return FileResponse(
        path=STATE.last_saved_model_path,
        filename=STATE.last_saved_model_path.name,
        media_type="application/octet-stream",
    )
