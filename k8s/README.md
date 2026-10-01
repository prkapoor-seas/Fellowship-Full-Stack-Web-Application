# Deploying LabsAtYale on Minikube

Two services (`web`, `analytics`) run as separate Deployments. The NGINX Ingress
controller routes `labsatyale.local` to the stable web release and diverts a
configurable share of requests to a canary release.

```
                  ┌──────────────── Ingress (nginx) ────────────────┐
labsatyale.local ─┤  web         → Service web-stable → v1 pods (2) │
                  │  web-canary  → Service web-canary → v2 pod  (1) │  canary-weight %
                  └─────────────────────────┬───────────────────────┘
                                            │ http://analytics:8000
                                  Service analytics → analytics pod
```

| File | Contents |
| ---- | -------- |
| `analytics.yaml` | analytics PVC, Deployment, Service |
| `web-stable.yaml` | shared SQLite PVC, stable Deployment (seeds the DB on first boot), Service |
| `ingress.yaml` | primary Ingress → `web-stable` |
| `canary/web-canary.yaml` | canary Deployment, Service, and weighted canary Ingress |

Every web response carries an `X-App-Version` header (`v1`, `v2`, …) so you can
see which release served it.

## 1. One-time setup

```bash
brew install minikube
minikube start --driver=docker
minikube addons enable ingress
```

## 2. Build the images inside Minikube

Run these from the repo root. Building inside Minikube means no registry is
needed, which is why the manifests use `imagePullPolicy: Never`.

```bash
minikube image build -t labsatyale-web:v1 web/
minikube image build -t labsatyale-analytics:v1 analytics/
```

## 3. Create the secret from `.env`

```bash
kubectl create secret generic labsatyale-secrets --from-env-file=.env
```

## 4. Deploy the stable release

```bash
kubectl apply -f k8s/
kubectl get pods -w        # wait until every pod is 1/1 Running, then Ctrl-C
```

On first boot the `seed-db` init container creates `labsatyale.sqlite` from
`schema.sql` and `mock.sql`. To use the repo's real `labsatyale.sqlite` instead,
copy it into the shared volume once:

```bash
POD=$(kubectl get pod -l app=web,track=stable -o jsonpath='{.items[0].metadata.name}')
kubectl cp labsatyale.sqlite "$POD":/data/labsatyale.sqlite
```

## 5. Open the site

With the docker driver on macOS, the ingress is reachable only through a tunnel.
Leave this running in its own terminal; it may ask for your password:

```bash
minikube tunnel
```

Map the hostname to localhost once:

```bash
echo "127.0.0.1 labsatyale.local" | sudo tee -a /etc/hosts
```

Then browse to http://labsatyale.local. To see the analytics dashboard:

```bash
kubectl port-forward svc/analytics 8000:8000     # http://localhost:8000
```

## 6. Release a canary

Make your code change, then build it as a new version and deploy it beside v1:

```bash
minikube image build -t labsatyale-web:v2 web/
kubectl apply -f k8s/canary/
```

About 10% of requests now go to v2. Check the split:

```bash
for i in $(seq 100); do curl -s -o /dev/null -D - http://labsatyale.local/labs | grep -i x-app-version; done | sort | uniq -c
```

Change the share at any time (0–100):

```bash
kubectl annotate ingress web-canary --overwrite nginx.ingress.kubernetes.io/canary-weight=50
```

Both releases share the same database and `APP_SECRET_KEY`, so users stay logged
in and see the same data whichever version serves them.

## 7. Promote or roll back

**Roll back.** Remove the canary; all traffic returns to v1:

```bash
kubectl delete -f k8s/canary/
```

**Promote.** Move stable to v2, then remove the canary:

```bash
kubectl set image deployment/web-stable web=labsatyale-web:v2 seed-db=labsatyale-web:v2
kubectl set env deployment/web-stable -c web APP_VERSION=v2
kubectl rollout status deployment/web-stable
kubectl delete -f k8s/canary/
```

Then update `web-stable.yaml` to `v2` (and the canary file to `v3`) so the files
match what's running for the next cycle.

## Useful commands

```bash
kubectl get pods,svc,ingress
kubectl logs -l app=web,track=canary
minikube dashboard            # web UI for the cluster
minikube stop                 # pause; data on the volumes is kept
minikube delete               # wipe the cluster, including both databases
```

## Why SQLite is OK here

Minikube runs a single node, so every web pod, stable and canary, mounts the same
`ReadWriteOnce` volume and opens the same file, and SQLite's file locks work. A
multi-node cluster would break this: pods on other nodes couldn't share the file,
and the fix would be moving to a database server such as Postgres.
