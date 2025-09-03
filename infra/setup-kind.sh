#!/bin/bash
set -e

echo "🚀 Starting local Docker registry..."
docker run -d --restart=always -p "127.0.0.1:5500:5000" --name kind-registry registry:2 || true

echo "🚀 Creating Kind cluster (ms-cluster)..."
cat <<'YAML' | kind create cluster --name ms-cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
containerdConfigPatches:
- |-
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."localhost:5500"]
    endpoint = ["http://kind-registry:5000"]
nodes:
- role: control-plane
- role: worker
YAML

echo "🚀 Connecting registry to Kind network..."
docker network connect "kind" kind-registry || true

echo "✅ Kind cluster and registry ready!"
