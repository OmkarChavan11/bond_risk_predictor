import psycopg2
import pandas as pd
import xgboost as xgb
import numpy as np

DB_CONFIG = {
    "host": "ep-sparkling-unit-adoazjll-pooler.c-2.us-east-1.aws.neon.tech",
    "database": "neondb",
    "user": "neondb_owner",
    "password": "npg_u2RvzLXweK9l"
}

def fetch_latest_metrics(issuer_id):
    conn = psycopg2.connect(**DB_CONFIG)
    # Pull the latest 4 metrics for the issuer
    query = """
        SELECT parameter_name, raw_value, covenant_limit 
        FROM financial_metrics 
        WHERE issuer_id = %s 
        ORDER BY metric_id DESC LIMIT 4;
    """
    df = pd.read_sql(query, conn, params=(issuer_id,))
    conn.close()
    return df

def calculate_risk_score(issuer_id):
    df = fetch_latest_metrics(issuer_id)
    
    # Data Cleaning
    def clean(val):
        try:
            return float(str(val).replace('%', '').replace('x', '').strip())
        except: return 0.0

    # Map both Actuals and Limits from the Neon DB
    metrics = {row['parameter_name']: clean(row['raw_value']) for _, row in df.iterrows()}
    limits = {row['parameter_name']: clean(row['covenant_limit']) for _, row in df.iterrows()}

    # 1. Fetch Dynamic Limits (with safe industry fallbacks to prevent crashes)
    car_limit = limits.get('Capital Adequacy', 15.0)
    lev_limit = limits.get('Leverage', 4.0)
    
    # Safety Check: Prevent Division by Zero if the DB returns 0
    car_limit = car_limit if car_limit > 0 else 15.0
    lev_limit = lev_limit if lev_limit > 0 else 4.0

    # 2. Calculate Dynamic Headroom
    features = {
        'car_headroom': (metrics.get('Capital Adequacy', 0) - car_limit) / car_limit,
        'lev_headroom': (lev_limit - metrics.get('Leverage', lev_limit)) / lev_limit,
        'asset_quality': metrics.get('Asset Quality', 0)
    }

    # 3. Inference Engine
    try:
        bst = xgb.Booster()
        bst.load_model('bond_risk_model.json')
        dmatrix = xgb.DMatrix([list(features.values())])
        probability = bst.predict(dmatrix)[0]
    except:
        # Fallback: Weighted heuristic
        probability = (1 - features['car_headroom']) * 0.4 + (1 - features['lev_headroom']) * 0.6
    
    # Cap probability between 0 and 100 just in case headroom goes wildly negative
    final_score = max(0, min(100, probability * 100))
    return round(final_score, 2)


# --- EXECUTION ---
score = calculate_risk_score(1)
print(f"🔥 Varthana Breach Probability: {score}%")