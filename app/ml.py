from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from imblearn.over_sampling import RandomOverSampler
from scipy import sparse
from sklearn.cluster import AgglomerativeClustering, KMeans, MiniBatchKMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor


@dataclass
class RegressionResult:
    best_model_name: str
    mae: float
    mse: float
    r2_score: float
    best_pipeline: Pipeline


@dataclass
class ClusteringResult:
    best_model_name: str
    silhouette_score: float
    clusters_count: int
    cluster_labels: list[int]
    best_pipeline: Pipeline


MAX_CLUSTERS = 8
MAX_EVAL_SAMPLES = 10000
MAX_SILHOUETTE_SAMPLES = 5000
AGGLOMERATIVE_MAX_SAMPLES = 12000

def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Force each column to a uniform type before preprocessing."""
    df = df.copy()
    for col in df.columns:
        # Try to convert to numeric first
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() / len(converted) > 0.5:
            # Majority are numeric, treat as numeric
            df[col] = converted
        else:
            # Treat as categorical, cast everything to string
            df[col] = df[col].astype(str)
    return df

def _build_feature_preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = [c for c in df.columns if c not in numeric_cols]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, categorical_cols),
        ],
        remainder="drop",
    )


def _maybe_resample_regression(X_train: pd.DataFrame, y_train: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    try:
        q = min(5, max(2, y_train.nunique()))
        y_binned = pd.qcut(y_train, q=q, duplicates="drop")
        if y_binned.nunique() < 2:
            return X_train, y_train

        distribution = y_binned.value_counts(normalize=True)
        imbalance_ratio = distribution.max() / distribution.min()
        if imbalance_ratio < 1.5:
            return X_train, y_train

        ros = RandomOverSampler(random_state=42)
        idx_df = pd.DataFrame({"idx": np.arange(len(y_train))})
        idx_resampled, _ = ros.fit_resample(idx_df, y_binned.astype(str))
        chosen_idx = idx_resampled["idx"].to_numpy()
        return X_train.iloc[chosen_idx], y_train.iloc[chosen_idx]
    except Exception:
        return X_train, y_train


def train_regression(df: pd.DataFrame, target_column: str) -> RegressionResult:
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' does not exist.")
    
    df = _clean_dataframe(df)

    X = df.drop(columns=[target_column])
    y = df[target_column]

    if not np.issubdtype(y.dtype, np.number):
        raise ValueError("Regression target column must be numeric.")

    preprocessor = _build_feature_preprocessor(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    X_train, y_train = _maybe_resample_regression(X_train, y_train)

    candidate_models: dict[str, Any] = {
        "LinearRegression": LinearRegression(),
        "DecisionTreeRegressor": DecisionTreeRegressor(random_state=42),
    }

    best_name = ""
    best_pipe: Pipeline | None = None
    best_mse = float("inf")
    best_metrics: tuple[float, float, float] | None = None

    for model_name, model in candidate_models.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model),
            ]
        )
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        if mse < best_mse:
            best_mse = mse
            best_name = model_name
            best_pipe = pipeline
            best_metrics = (mae, mse, r2)

    if best_pipe is None or best_metrics is None:
        raise RuntimeError("No regression model could be trained.")

    return RegressionResult(
        best_model_name=best_name,
        mae=float(best_metrics[0]),
        mse=float(best_metrics[1]),
        r2_score=float(best_metrics[2]),
        best_pipeline=best_pipe,
    )


# def _maybe_resample_clustering(X_prepared: np.ndarray) -> np.ndarray:
#     if X_prepared.shape[0] < 10:
#         return X_prepared

#     try:
#         initial_k = min(3, max(2, X_prepared.shape[0] // 10))
#         initial_kmeans = KMeans(n_clusters=initial_k, random_state=42, n_init=10)
#         pseudo_labels = initial_kmeans.fit_predict(X_prepared)

#         counts = pd.Series(pseudo_labels).value_counts(normalize=True)
#         imbalance_ratio = counts.max() / counts.min()
#         if imbalance_ratio < 1.5:
#             return X_prepared

#         ros = RandomOverSampler(random_state=42)
#         X_resampled, _ = ros.fit_resample(X_prepared, pseudo_labels)
#         return X_resampled
#     except Exception:
#         return X_prepared

def _prepare_clustering_features(df: pd.DataFrame, preprocessor: ColumnTransformer) -> tuple[Any, str, Any]:
    """Prepare a clustering-ready matrix and optional reducer step for the saved pipeline."""
    X_transformed = preprocessor.fit_transform(df)

    if sparse.issparse(X_transformed):
        n_features = X_transformed.shape[1]
        n_components = min(50, n_features - 1) if n_features > 1 else 1
        reducer = TruncatedSVD(n_components=n_components, random_state=42)
        X_cluster = reducer.fit_transform(X_transformed)
        return X_cluster.astype(np.float32), "svd", reducer

    return np.asarray(X_transformed, dtype=np.float32), "reducer", "passthrough"


def _sample_for_evaluation(X: np.ndarray) -> tuple[np.ndarray, np.ndarray | None]:
    if X.shape[0] <= MAX_EVAL_SAMPLES:
        return X, None

    rng = np.random.default_rng(42)
    indices = rng.choice(X.shape[0], size=MAX_EVAL_SAMPLES, replace=False)
    indices.sort()
    return X[indices], indices


def _safe_silhouette(X: np.ndarray, labels: np.ndarray) -> float:
    sample_size = min(MAX_SILHOUETTE_SAMPLES, X.shape[0])
    return float(silhouette_score(X, labels, sample_size=sample_size, random_state=42))


def train_clustering(df: pd.DataFrame) -> ClusteringResult:
    df = _clean_dataframe(df)
    preprocessor = _build_feature_preprocessor(df)
    X_cluster, reducer_step_name, reducer_step = _prepare_clustering_features(df, preprocessor)

    if X_cluster.shape[0] < 2:
        raise ValueError("Not enough rows for clustering.")

    X_eval, _ = _sample_for_evaluation(X_cluster)

    best_name = ""
    best_score = -1.0
    best_cluster_count = 0

    max_clusters = min(MAX_CLUSTERS, X_eval.shape[0] - 1)
    if max_clusters < 2:
        raise ValueError("Not enough rows for clustering.")

    use_agglomerative = X_cluster.shape[0] <= AGGLOMERATIVE_MAX_SAMPLES

    for n_clusters in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans_labels = kmeans.fit_predict(X_eval)
        kmeans_score = _safe_silhouette(X_eval, kmeans_labels)
        if kmeans_score > best_score:
            best_name = "KMeans"
            best_score = float(kmeans_score)
            best_cluster_count = n_clusters

        if use_agglomerative:
            agglomerative = AgglomerativeClustering(n_clusters=n_clusters)
            agg_labels = agglomerative.fit_predict(X_eval)
            agg_score = _safe_silhouette(X_eval, agg_labels)
            if agg_score > best_score:
                best_name = "AgglomerativeClustering"
                best_score = float(agg_score)
                best_cluster_count = n_clusters
        else:
            minibatch = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, n_init=10, batch_size=2048)
            mb_labels = minibatch.fit_predict(X_eval)
            mb_score = _safe_silhouette(X_eval, mb_labels)
            if mb_score > best_score:
                best_name = "MiniBatchKMeans"
                best_score = float(mb_score)
                best_cluster_count = n_clusters

    if not best_name or best_cluster_count == 0:
        raise RuntimeError("No clustering model could be trained.")

    if best_name == "KMeans":
        final_model = KMeans(n_clusters=best_cluster_count, random_state=42, n_init=10)
        best_labels = final_model.fit_predict(X_cluster)
    elif best_name == "MiniBatchKMeans":
        final_model = MiniBatchKMeans(n_clusters=best_cluster_count, random_state=42, n_init=10, batch_size=2048)
        best_labels = final_model.fit_predict(X_cluster)
    else:
        final_model = AgglomerativeClustering(n_clusters=best_cluster_count)
        best_labels = final_model.fit_predict(X_cluster)

    final_score = _safe_silhouette(X_cluster, best_labels)

    best_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (reducer_step_name, reducer_step),
            ("model", final_model),
        ]
    )

    # Refit pipeline on original data for saving both preprocessing and model together.
    best_pipeline.fit(df)

    return ClusteringResult(
        best_model_name=best_name,
        silhouette_score=float(final_score),
        clusters_count=int(best_cluster_count),
        cluster_labels=[int(x) for x in best_labels.tolist()],
        best_pipeline=best_pipeline,
    )
