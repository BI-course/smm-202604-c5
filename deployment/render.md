# Public deployment: Render

This covers the Render part of the lab: the API in `../api.py`, with our four saved models, served publicly so it can be tested with curl or Postman.

**Live URL:** https://smm-202604-c5-lab.onrender.com

## How the request travels

```
curl / Postman --HTTPS--> Render (TLS, public URL) --> Gunicorn (4 workers, $PORT) --> api.py --> model/*.joblib
```
## Settings used

| Setting | Value |
|---|---|
| Service type | Web Service |
| Service name | `smm-202604-c5-lab` |
| Repository / branch | `BI-course/smm-202604-c5`, branch `deploy/lab-smm/render-bakhita` |
| Runtime | Python 3.12.10 (read from `.python-version`) |
| Build command | `pip install -r requirements/base.txt -r requirements/prod.txt -c requirements/constraints.txt` |
| Start command | `gunicorn -w 4 -b 0.0.0.0:$PORT api:app` (same as `Procfile`) |
| Plan | Free |


## Steps

1. Checked that `../model` on `main` has our four `.joblib` files and that `Procfile` says `web: gunicorn -w 4 -b 0.0.0.0:$PORT api:app`:
   - `20261104_133324_ridge_regressor_for_retail_sales.joblib` (regression)
   - `corporate_distress_classifier.joblib` (classification)
   - `kmeans_ecommerce_customer_segmentation.joblib` (clustering)
   - `streaming_arm_rules.joblib` (association rules)
2. On dashboard.render.com: **+ New → Web Service**, connected the repository, chose branch `main`, and entered the settings above.
3. Waited for the deploy. The log showed `All the four artifacts have been loaded. The API is ready.`
4. Tested each endpoint with a POST request (curl and Postman).


## Test results

All requests returned `200 OK`. Base URL: `https://smm-202604-c5-lab.onrender.com`

| Endpoint (POST `/api/v1/models/...`) | Request | Response |
|---|---|---|
| `retail-sales-regressor/predictions` | promotions 1, footfall 250, basket 1,500 KES, Supermarket, Residential, Medium | `predicted_daily_sales_revenue_kes: 191850.29` (Ridge Regression) |
| `corporate-distress-classifier/predictions` | Manufacturing, Private, High Risk, D/E 3.8, current ratio 0.7, interest cover 0.9, growth -6.5%, margin -3.2% | `Distressed`, probability `{"Distressed": 0.756,"Healthy": 0.112,"Watch": 0.132}` (Random Forest + SMOTE)|
| `ecommerce-customer-segmenter/predictions` | recency 11 days, 2 orders/year, 4,000 KES, 2 categories | `assigned_cluster: 4` (K-Means, k = 5) |
| `streaming-recommender/predictions` | cart S02 + S03, top 3 | `S01`, confidence `0.833`, lift `3.7` |
| `streaming-recommender/predictions` | cart S99 (no matching rule) | empty `recommendations` list, not an error |


## Problems I hit

- **"Not Found" at the main URL.** Opening `https://smm-202604-c5-lab.onrender.com` in the browser returns 404. This is by design: `../api.py` has no route for `/`, only the four prediction routes.
- **"Method Not Allowed" in the browser.** Opening an endpoint address in Safari returns 405, because the browser sends GET and the endpoints only accept POST. Testing with curl in Terminal or with Postman fixed this.