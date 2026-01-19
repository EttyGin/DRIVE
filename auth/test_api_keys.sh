#!/usr/bin/env bash

BASE_URL="http://localhost:8000"

echo "=============================="
echo "1. Who am I? (regular user)"
echo "=============================="
curl -s $BASE_URL/me \
  -H "Authorization: Api-Key REGULAR_SERVICE_KEY_abcdef"
echo
echo

echo "=============================="
echo "2. Change my API key"
echo "=============================="
curl -s -X POST $BASE_URL/me/change-api-key \
  -H "Authorization: Api-Key REGULAR_SERVICE_KEY_abcdef" \
  -H "Content-Type: application/json" \
  -d '{"new_api_key":"MY_NEW_PERSONAL_KEY_999999"}'
echo
echo

echo "=============================="
echo "3. Try old API key (should fail)"
echo "=============================="
curl -s $BASE_URL/me \
  -H "Authorization: Api-Key REGULAR_SERVICE_KEY_abcdef"
echo
echo

echo "=============================="
echo "4. Try new API key (should succeed)"
echo "=============================="
curl -s $BASE_URL/me \
  -H "Authorization: Api-Key MY_NEW_PERSONAL_KEY_999999"
echo
echo

echo "=============================="
echo "5. Try changing API key with Bearer token (should fail)"
echo "=============================="
curl -s -X POST $BASE_URL/me/change-api-key \
  -H "Authorization: Bearer valid-oidc-token" \
  -H "Content-Type: application/json" \
  -d '{"new_api_key":"SHOULD_NOT_WORK_KEY_123"}'
echo
echo

echo "=============================="
echo "6. Admin API key (should be unchanged)"
echo "=============================="
curl -s $BASE_URL/me \
  -H "Authorization: Api-Key ADMIN_SUPER_SECRET_KEY_123456"
echo
echo
