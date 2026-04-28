#!/bin/sh
export PORT=${PORT:-8080}
echo "Starting WhatAPlant on port $PORT"
exec python -c "
import os
port = int(os.environ.get('PORT', 8080))
import subprocess
subprocess.run(['gunicorn', 'app:app', '--bind', f'0.0.0.0:{port}', '--workers', '2', '--timeout', '120'])
"
