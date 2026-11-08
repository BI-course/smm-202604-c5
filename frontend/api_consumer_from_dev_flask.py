"""
api_consumer_from_dev_flask.py

A frontend-style client that calls each of the four prediction endpoints
exposed by api.py, running on the local Flask development server. Start
api.py first (python api.py), then run this script separately.

This mirrors api.py's four artifacts one-to-one:

    1. Regression        -- /api/v1/models/sme-revenue-regressor/predictions
    2. Classification     -- /api/v1/models/corporate-distress-classifier/predictions
    3. Clustering         -- /api/v1/models/mall-customer-segmenter/predictions
    4. Association Rule   -- /api/v1/models/ecommerce-recommender/predictions
       Mining (ARM)

Each call uses the same requests.post(..., json=payload, headers=headers)
pattern, the same header set, and the same try/except structure as the
single-endpoint version this file replaces -- only the URL, payload, and the
key read back out of the JSON response differ per endpoint, because each
endpoint returns a different shape (a regression figure, a class + class
probabilities, a cluster id, or a list of recommendations).
"""

import requests

BASE_URL = "http://127.0.0.1:5000"

HEADERS = {
    'Content-Type': 'application/json',  # This header tells the server that the payload is in JSON format
    'Accept': 'application/json',        # This header tells the server that the client expects a JSON response
    'User-Agent': 'ServingMLModels-Client/1.0',  # Identifies the client application (useful for backend logging/debugging)
    # 'Authorization': 'Bearer <token>',  # This can be used for token-based authentication if the API requires it
}


def call_endpoint(path, payload):
    """Send one POST request to the given API path and return the parsed
    JSON response, or None if the request failed. Centralizing the
    try/except here means each of the four calls below gets identical
    error handling without repeating it four times."""
    url = f"{BASE_URL}{path}"
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()  # Raises an HTTPError if the status code is 4xx or 5xx
        return response.json()

    except requests.exceptions.HTTPError as e:
        print("HTTP error:", e)
        if e.response is not None:
            print("Response body:", e.response.text)

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

    return None


# 1. REGRESSION -- predict monthly revenue (KES) for an SME

regression_payload = {
    "promotions_active": 1,
    "footfall_count": 250,
    "avg_basket_size_kes": 1500,
    "store_format": "Supermarket",
    "location_type": "Residential",
    "store_size_category": "Medium"
}

result = call_endpoint("/api/v1/models/retail-sales-regressor/predictions", regression_payload)
if result is not None:
    print("Predicted daily sales revenue (KES) =", result["predicted_daily_sales_revenue_kes"])
print("-" * 60)



# 2. CLASSIFICATION -- predict SME credit risk category (Low/Medium/High)

classification_payload = {
    "industry_sector": "Manufacturing",
    "listing_status": "Private",
    "credit_rating_band": "High Risk",
    "audit_going_concern_flag": None,
    "years_in_operation": 4.0,
    "num_employees": 40,
    "debt_to_equity_ratio": 3.8,
    "current_ratio": 0.7,
    "interest_coverage_ratio": 0.9,
    "revenue_growth_pct": -6.5,
    "net_profit_margin_pct": -3.2,
    "working_capital_to_assets_ratio": -0.12,
    "macroeconomic_interest_rate_pct": 14.5
}

result = call_endpoint("/api/v1/models/corporate-distress-classifier/predictions", classification_payload)
if result is not None:
    print("Predicted credit risk category =", result["predicted_credit_risk_category"])
    print("Class probabilities =", result["class_probabilities"])

print("-" * 60)



# 3. CLUSTERING -- assign a new mall customer to an existing segment

clustering_payload = {
    "Age": 27,
    "Annual Income (k$)": 45,
    "Spending Score (1-100)": 72,
}

result = call_endpoint("/api/v1/models/mall-customer-segmenter/predictions", clustering_payload)
if result is not None:
    print("Assigned cluster =", result["assigned_cluster"])

print("-" * 60)



# 4. ASSOCIATION RULE MINING -- recommend products for a shopping cart

recommendation_payload = {
    "cart": ["P04", "P01"],
    "top_n": 3,
}

result = call_endpoint("/api/v1/models/ecommerce-recommender/predictions", recommendation_payload)
if result is not None:
    print("Cart =", result["cart"])
    print("Recommendations =", result["recommendations"])