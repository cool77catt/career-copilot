#!/usr/bin/env bash
set -euo pipefail

if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
fi

if [ ! -f frontend/.env.local ]; then
  cp frontend/.env.local.example frontend/.env.local
fi

echo "Environment files ready."
