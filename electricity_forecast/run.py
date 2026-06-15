from pathlib import Path
from your_module.models import train_models, save_models, load_models, forecast_dataframe
from your_module.types import ForecastRequest

MODEL_PATH = Path("trained_models.pkl")

def get_models(feature_table, force_retrain=False):
    """Load model từ file nếu có, không thì train mới và lưu lại."""
    
    if MODEL_PATH.exists() and not force_retrain:
        print(" Tìm thấy model đã train, đang load...")
        models = load_models(MODEL_PATH)
        print(f"   Loaded {len(models)} meters: {list(models.keys())}")
        return models
    
    print("🔄 Chưa có model, bắt đầu train...")
    models, metrics_df = train_models(feature_table)
    
    save_models(models, MODEL_PATH)
    print(f"   Đã lưu model vào: {MODEL_PATH}")
    print(f"   Trained {len(models)} meters")
    print(metrics_df[["meter", "model_name", "mae", "rmse", "r2"]].to_string())
    
    return models


# ---- Sử dụng ----
# Lần đầu: tự động train và lưu
models = get_models(your_feature_table)

# Lần sau: chỉ load, không train lại
models = get_models(your_feature_table)  # dùng y chang, tự detect

# Muốn force train lại (khi có data mới):
models = get_models(your_feature_table, force_retrain=True)

# Forecast bình thường
request = ForecastRequest(horizon_hours=24)
forecast_df = forecast_dataframe(models, your_feature_table, request)
