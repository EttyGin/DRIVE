#!/usr/bin/env bash
set -euo pipefail

# === Debug option ===
if [ "${DEBUG:-0}" = "1" ]; then
  set -x
fi

# === קלאסטרים זמינים ===
CLUSTERS=("bm" "rawdemo")

# === טיפול בפרמטרים ===
if [ $# -eq 0 ]; then
  # אין פרמטרים – הכל אינטראקטיבי
  read -rp "Enter path to SealedSecret manifest: " SEALED_FILE
  echo "Select cluster:"
  select choice in "${CLUSTERS[@]}"; do
    CLUSTER="$choice"
    [ -n "$CLUSTER" ] && break
  done
elif [ $# -eq 1 ]; then
  # פרמטר אחד – זה הנתיב ל-SealedSecret
  SEALED_FILE="$1"
  echo "Select cluster:"
  select choice in "${CLUSTERS[@]}"; do
    CLUSTER="$choice"
    [ -n "$CLUSTER" ] && break
  done
else
  # שני פרמטרים – cluster + manifest
  CLUSTER="$1"
  SEALED_FILE="$2"
fi

# === מיפוי קלאסטרים ===
case "$CLUSTER" in
  bm)
    CONTROLLER_URL="bm_url"
    NAMESPACE_KEY="namespace-bm-dv"
    VALUES_FILE="values-bm-dev.yaml"
    MODE="json"
    ;;
  rawdemo)
    CONTROLLER_NAME="sealed-secrets-controller"
    CONTROLLER_NAMESPACE="kube-system"
    NAMESPACE_KEY="namespace-rawdemo"
    VALUES_FILE="values-rawdemo.yaml"
    MODE="raw"
    ;;
  *)
    echo "Unknown cluster: $CLUSTER"
    exit 1
    ;;
esac

echo "ℹ️  Selected cluster: $CLUSTER"
echo "ℹ️  Values file: $VALUES_FILE"
echo "ℹ️  Namespace key in config.json: $NAMESPACE_KEY"
echo "ℹ️  SealedSecret manifest: $SEALED_FILE"
echo "ℹ️  Mode: $MODE"

# === שליפת namespace מתוך config.json ===
NAMESPACE=$(jq -r ".\"$NAMESPACE_KEY\"" config.json)
echo "ℹ️  Namespace resolved: $NAMESPACE"

# === שליפת שם ה־Secret מתוך המניפסט ===
SECRET_NAME=$(yq e '.metadata.name' "$SEALED_FILE")
echo "ℹ️  Secret name: $SECRET_NAME"

# === לולאה על קובץ .secrets ===
while IFS=":" read -r KEY VALUE; do
  KEY=$(echo "$KEY" | xargs)
  VALUE=$(echo "$VALUE" | xargs)
  [ -z "$KEY" ] && continue

  echo "🔑 Processing key: $KEY"

  if [ "$MODE" = "json" ]; then
    ENCVAL=$(
      echo -n "$VALUE" | kubectl create secret generic "$SECRET_NAME" \
        --namespace "$NAMESPACE" \
        --from-literal="$KEY=/dev/stdin" \
        --dry-run=client -o json \
      | kubeseal --controller-url="$CONTROLLER_URL" --format=yaml \
      | yq e ".spec.encryptedData.$KEY" -
    )
  elif [ "$MODE" = "raw" ]; then
    ENCVAL=$(
      echo -n "$VALUE" | kubeseal \
        --raw \
        --name "$SECRET_NAME" \
        --namespace "$NAMESPACE" \
        --controller-name "$CONTROLLER_NAME" \
        --controller-namespace "$CONTROLLER_NAMESPACE"
    )
  else
    echo "Unsupported MODE=$MODE"
    exit 1
  fi

  # מציאת ההפניה ל־Values בתוך ה-template
  PATH_IN_VALUES=$(grep -o "{{ .Values\.[^ }]* }}" "$SEALED_FILE" | grep "$KEY" | sed -E 's/\{\{ .Values\.([^ }]+) \}\}/\1/')

  echo "🔍 Key=$KEY PATH_IN_VALUES=$PATH_IN_VALUES"
  # echo "🔍 Encrypted value (truncated): ${ENCVAL:0:20}..."

  if [ -n "$PATH_IN_VALUES" ]; then
    echo "📝 Updating $VALUES_FILE -> $PATH_IN_VALUES"
    yq e -i ".${PATH_IN_VALUES} = \"$ENCVAL\"" "$VALUES_FILE"
  else
    echo "⚠️  Key $KEY not found in SealedSecret template"
  fi

done < .secrets

echo "✅ Done. Updated $VALUES_FILE"
