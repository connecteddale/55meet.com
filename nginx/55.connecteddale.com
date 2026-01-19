# /etc/nginx/sites-available/55.connecteddale.com
# The 55 - Leadership Alignment Diagnostics

upstream the55_backend {
    server 127.0.0.1:8055;
}

server {
    server_name 55.connecteddale.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging
    access_log /var/www/the55/logs/nginx_access.log;
    error_log /var/www/the55/logs/nginx_error.log;

    # Static files - served directly by nginx
    location /static/ {
        alias /var/www/the55/app/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # Health check - direct to backend
    location = /health {
        proxy_pass http://the55_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # All other routes - proxy to FastAPI
    location / {
        proxy_pass http://the55_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings for synthesis (Claude API can take 10-30s)
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # ACME challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/the55;
    }

    # HTTP only initially - certbot will add SSL
    listen 80;
}
