#!/bin/bash
# check_service.sh - Verify The 55 service is running correctly

set -e

echo "=== The 55 Service Health Check ==="
echo ""

# Check systemd status
echo "1. Systemd Status:"
systemctl is-active the55 && echo "   Service: ACTIVE" || echo "   Service: INACTIVE"

# Check process
echo ""
echo "2. Process Check:"
pgrep -f "gunicorn.*the55" > /dev/null && echo "   Gunicorn: RUNNING" || echo "   Gunicorn: NOT FOUND"

# Check port binding
echo ""
echo "3. Port Check:"
ss -tlnp | grep :8055 > /dev/null && echo "   Port 8055: LISTENING" || echo "   Port 8055: NOT LISTENING"

# Check health endpoint
echo ""
echo "4. Health Endpoint:"
curl -s http://127.0.0.1:8055/health | grep -q "ok" && echo "   /health: OK" || echo "   /health: FAILED"

echo ""
echo "=== Check Complete ==="
