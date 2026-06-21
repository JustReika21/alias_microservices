#!/bin/sh
set -e

APISIX_ADMIN="http://apisix:9180/apisix/admin"
ADMIN_KEY="$APISIX_ADMIN_KEY"

echo "Waiting etcd..."
until curl -s http://etcd:2379/health | grep -q "true"; do
  sleep 2
done

echo "Waiting APISIX admin..."
until curl -s -H "X-API-KEY: $ADMIN_KEY" \
  "$APISIX_ADMIN/routes" >/dev/null; do
  sleep 2
done

echo "Loading routes..."

routes_json=$(yq eval -o=json /routes.yaml)

echo "$routes_json" | jq -c '.routes[]' | while read route; do
  id=$(echo "$route" | jq -r '.id')

  echo "Upserting route $id"

  curl -s -X PUT \
    "$APISIX_ADMIN/routes/$id" \
    -H "X-API-KEY: $ADMIN_KEY" \
    -H "Content-Type: application/json" \
    -d "$route"

done

echo "Done"