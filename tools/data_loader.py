import pandas as pd
import io
from core.logger import logger


def load_data(file):

    try:
        # reset pointer
        if hasattr(file, "seek"):
            file.seek(0)

        file_name = getattr(file, "name", "")

        # -----------------------------
        # 📂 CSV
        # -----------------------------
        if file_name.endswith(".csv") or isinstance(file, io.StringIO):
            df = pd.read_csv(file)

        # -----------------------------
        # 📂 EXCEL
        # -----------------------------
        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(file)

        else:
            # fallback
            df = pd.read_csv(file)

        logger.info(f"Data loaded successfully: shape={df.shape}")
        return df

    except Exception as e:
        logger.error(f"Data loading failed: {e}")
        raise ValueError("❌ Failed to load file. Unsupported or corrupted format.")