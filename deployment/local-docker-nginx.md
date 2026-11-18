# Local deployment: Docker + Gunicorn + Nginx (issue #7)

Mark Kinuthia (kinuthia-mark), branch `deploy/docker-nginx`. Done and tested on 18 Nov 2026.

This covers marking guide rows 5 (API Dockerized and served with Gunicorn) and 6 (Nginx reverse proxy forwards requests to the containerized API). No changes to `api.py` or `model/` were needed: the containers are built from the same files that are on `main` after PR #18.

## How the request travels

```
curl / browser --HTTPS 443--> Nginx (TLS, reverse proxy) --/api/--> flask-gunicorn-app x2 (Gunicorn, 5 workers each, port 8000) --> api.py --> model/*.joblib
```

Port 8000 is only exposed inside the Docker network, so the API can only be reached through Nginx.

## Steps (Git Bash, from the repo root)

1. Start Docker Desktop. Stop anything else using ports 80 and 443 first. On my laptop XAMPP's Apache runs as a Windows service and takes both ports, so in an administrator PowerShell:

   ```powershell
   Stop-Service Apache2.4
   ```

2. Create the volume folders and the `.env` file (copy `env.example` and set your own passwords; `.env` is gitignored):

   ```shell
   ./lab_setup.sh
   ```

3. Start the Ubuntu container and make the self-signed certificate inside it (config from `app_server_reverse_proxy_server_setup.md`, CN = localhost, SAN = localhost, customized-ubuntu-server-smm, 127.0.0.1, valid 90 days):

   ```shell
   docker compose -f docker-compose-dev.yaml up -d ubuntu-server
   docker exec -it --user student customized-ubuntu-server-smm bash
   # inside the container: write /home/student/openssl.cnf as in the setup guide, then
   mkdir -p /home/student/certs
   openssl req -x509 -nodes -days 90 -newkey rsa:2048 \
     -keyout /home/student/certs/selfsigned.key \
     -out /home/student/certs/selfsigned.crt \
     -config /home/student/openssl.cnf
   ```

4. Copy the two files to the Nginx folder (both folders are gitignored, so the key is never committed):

   ```shell
   cp container-volumes/ubuntu/home-student/certs/selfsigned.* container-volumes/nginx/certs/
   ```

5. Build and start everything with two app replicas, then restart Nginx once so it sees both replicas:

   ```shell
   docker compose -f docker-compose.yaml -f docker-compose-dev.yaml up -d --build --scale flask-gunicorn-app=2
   docker compose -f docker-compose.yaml -f docker-compose-dev.yaml restart nginx
   ```

## Test results (18 Nov 2026)

`http://localhost/` returns 301 to `https://localhost/`, and the responses come from `nginx/1.28.1` using our certificate.

| Endpoint (POST `https://localhost/api/v1/models/...`) | Request | Response |
|---|---|---|
| `retail-sales-regressor/predictions` | promotions 1, footfall 850, basket 1,200 KES, Supermarket, Mall, Medium | `predicted_daily_sales_revenue_kes: 411591.55` (Ridge) |
| `corporate-distress-classifier/predictions` | Speculative rating, D/E 2.8, current ratio 0.9, interest cover 1.2, growth -6.5%, margin -2.1% | `Distressed`, probability 0.788 (Random Forest + SMOTE) |
| `ecommerce-customer-segmenter/predictions` | recency 11 days, 2 orders/year, 4,000 KES, 2 categories | `assigned_cluster: 4` (K-Means, k = 5) |
| `streaming-recommender/predictions` | cart S02 + S03, top 3 | S01, confidence 0.833, lift 3.7 |

Example (`-k` because the certificate is self-signed):

```shell
curl -k -X POST https://localhost/api/v1/models/ecommerce-customer-segmenter/predictions \
  -H "Content-Type: application/json" \
  -d '{"recency_days": 11, "frequency_per_year": 2, "avg_order_value_kes": 4000, "num_categories_purchased": 2}'
```

## Problems I hit

- **Apache answered instead of Nginx.** XAMPP's Apache was holding ports 80 and 443, so the first tests returned Apache 404 pages. Stopping the `Apache2.4` service fixed it.
- **Old Docker volumes.** I had an older clone of this repo from class with the same folder name, so Docker reused its volumes (pointing at the old folder). Running `docker compose ... down` and `docker volume rm smm-202604-c5_home-student smm-202604-c5_nginx-certs smm-202604-c5_nginx-frontend` made Compose recreate them for the current folder. For these bind volumes, removing the volume only removes Docker's link, not the files.

## What I learned

Gunicorn runs several worker processes, so the API can answer more than one request at a time, unlike the Flask development server. Nginx sits in front: it handles HTTPS, sends `/api/` traffic to the app containers and spreads it across the two replicas, and keeps the app server off the public ports. Because the models are loaded from the saved `.joblib` files when Gunicorn starts, the containers serve the exact same pipelines the notebooks saved, with no retraining.
