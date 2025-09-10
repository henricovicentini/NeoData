import io
import json
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.ensemble import IsolationForest


def validate_dataframe(df: pd.DataFrame) -> dict:
    """Valida se o DataFrame atende critérios básicos de qualidade."""
    results = {}

    if df is None or df.empty:
        return {"valid": False, "reason": "DataFrame vazio ou nulo", "row_count": 0}

    try:
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        results["no_nulls_numeric"] = (
            all(df[c].notna().all() for c in num_cols) if num_cols else True
        )
        results["numeric_positive"] = all(
            (df[c] >= 0).all() for c in num_cols if c in df.columns
        )
        results["row_count"] = len(df)
        results["valid"] = (
            results["no_nulls_numeric"]
            and results["numeric_positive"]
            and results["row_count"] > 0
        )

    except Exception as e:
        results = {"valid": False, "error": str(e), "row_count": len(df)}

    return results


def analyze_dataframe(df: pd.DataFrame) -> dict:
    """Gera estatísticas básicas do DataFrame."""
    if df is None or df.empty:
        return {
            "shape": (0, 0),
            "dtypes": {},
            "missing_by_col": {},
            "duplicates": 0,
        }

    try:
        return {
            "shape": df.shape,
            "dtypes": {c: str(t) for c, t in df.dtypes.items()},
            "missing_by_col": df.isna().sum().to_dict(),
            "duplicates": int(df.duplicated().sum()),
        }
    except Exception as e:
        return {"error": f"Erro ao analisar DataFrame: {str(e)}"}


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicados, imputa valores ausentes e trata outliers."""
    if df is None or df.empty:
        return pd.DataFrame()

    try:
        # Remove duplicados
        df = df.drop_duplicates()

        # Seleciona apenas colunas numéricas
        num_cols = df.select_dtypes(include=[np.number]).columns

        if len(num_cols) > 0:
            # Imputação de valores ausentes
            imputer = KNNImputer(n_neighbors=3)
            df[num_cols] = imputer.fit_transform(df[num_cols])

            # Detecção e remoção de outliers
            iso = IsolationForest(contamination=0.05, random_state=42)
            mask = iso.fit_predict(df[num_cols])
            df = df[mask == 1]

        return df.reset_index(drop=True)

    except Exception as e:
        print(f"[clean_dataframe] Erro durante limpeza: {e}")
        return df.reset_index(drop=True)


def compare_reports(before: dict, after: dict) -> dict:
    """Compara estatísticas antes e depois da limpeza."""
    try:
        return {
            "rows_before": before.get("shape", [0, 0])[0],
            "rows_after": after.get("shape", [0, 0])[0],
            "missing_before": before.get("missing_by_col", {}),
            "missing_after": after.get("missing_by_col", {}),
            "duplicates_before": before.get("duplicates", 0),
            "duplicates_after": after.get("duplicates", 0),
        }
    except Exception as e:
        return {"error": f"Erro ao comparar relatórios: {str(e)}"}
