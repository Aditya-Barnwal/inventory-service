#!/usr/bin/env bash
set -euo pipefail
NS=inventory
TAG="dev-$(date +%s)"

echo "🔧 Building & pushing backend..."
docker build -t localhost:5500/inventory-service:$TAG ./backend
docker push localhost:5500/inventory-service:$TAG

echo "🎨 Building & pushing frontend..."
# .env should point to http://inventory.local/api/v1
docker build -t localhost:5500/inventory-frontend:dev ./frontend
docker push localhost:5500/inventory-frontend:dev

echo "🚀 Helm upgrade backend (and MySQL)..."
helm upgrade --install inventory ./infra/helm/inventory-service \
  -n $NS --create-namespace \
  --set image.repository=localhost:5500/inventory-service \
  --set image.tag=$TAG

echo "🖥️  Helm upgrade frontend..."
helm upgrade --install inventory-ui ./infra/helm/frontend -n $NS

echo "⏳ Waiting for rollouts..."
kubectl -n $NS rollout status deploy/inventory-inventory-service --timeout=180s
kubectl -n $NS rollout status deploy/inventory-ui-inventory-frontend --timeout=180s

echo "✅ Done. Open: http://inventory.local"
