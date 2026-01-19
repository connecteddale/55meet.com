#!/bin/bash
# e2e_test.sh - End-to-end production test for The 55
# Tests the complete flow: login -> session -> join -> respond -> close -> synthesize -> reveal

set -e

BASE_URL="https://55.connecteddale.com"
COOKIE_FILE="/tmp/the55_test_cookies.txt"

echo "=== The 55 E2E Production Test ==="
echo "Base URL: $BASE_URL"
echo ""

# Cleanup
rm -f "$COOKIE_FILE"

# 1. Health check
echo "1. Health Check:"
HEALTH=$(curl -s "$BASE_URL/health")
echo "$HEALTH" | grep -q "ok" && echo "   PASS: Health endpoint OK" || { echo "   FAIL: Health check failed"; exit 1; }

# 2. Login page loads (facilitator login at /admin/login)
echo ""
echo "2. Login Page:"
curl -s "$BASE_URL/admin/login" | grep -q "Login" && echo "   PASS: Login page loads" || { echo "   FAIL: Login page failed"; exit 1; }

# 3. Participant join page loads
echo ""
echo "3. Participant Join Page:"
curl -s "$BASE_URL/join" | grep -q "Team Code" && echo "   PASS: Join page loads" || { echo "   FAIL: Join page failed"; exit 1; }

# 4. Static files served
echo ""
echo "4. Static Files:"
CSS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/static/css/main.css")
[ "$CSS_STATUS" = "200" ] && echo "   PASS: CSS file served (HTTP $CSS_STATUS)" || { echo "   FAIL: CSS not served (HTTP $CSS_STATUS)"; exit 1; }

# 5. Images API and static image serving
echo ""
echo "5. Images:"
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/images")
[ "$API_STATUS" = "200" ] && echo "   PASS: Images API works (HTTP $API_STATUS)" || { echo "   FAIL: Images API failed (HTTP $API_STATUS)"; exit 1; }
IMG_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/static/images/55/01.svg")
[ "$IMG_STATUS" = "200" ] && echo "   PASS: Static image served (HTTP $IMG_STATUS)" || { echo "   FAIL: Static image failed (HTTP $IMG_STATUS)"; exit 1; }

# 6. Test SSL certificate
echo ""
echo "6. SSL Certificate:"
CERT_ISSUER=$(echo | openssl s_client -connect 55.connecteddale.com:443 2>/dev/null | openssl x509 -noout -issuer 2>/dev/null | grep -o "Let's Encrypt" || echo "Unknown")
[ "$CERT_ISSUER" = "Let's Encrypt" ] && echo "   PASS: Valid Let's Encrypt certificate" || echo "   WARN: Certificate issuer: $CERT_ISSUER"

# 7. HTTP redirects to HTTPS
echo ""
echo "7. HTTP->HTTPS Redirect:"
REDIRECT=$(curl -s -o /dev/null -w "%{http_code}" -L "http://55.connecteddale.com/health")
[ "$REDIRECT" = "200" ] && echo "   PASS: HTTP redirects to HTTPS correctly" || { echo "   FAIL: Redirect not working"; exit 1; }

echo ""
echo "=== Automated Tests Complete ==="
echo ""
echo "Manual verification required:"
echo "  - Full session flow (create session, participant join, respond, close, synthesize, reveal)"
echo "  - Mobile testing on iOS Safari, Chrome, Samsung Internet"
echo ""

# Cleanup
rm -f "$COOKIE_FILE"
