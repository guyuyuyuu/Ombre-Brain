#!/bin/bash
echo "[START] launching gateway.py..."
python gateway.py >> /proc/1/fd/1 2>> /proc/1/fd/2 &
GPID=$!
echo "[START] gateway pid=$GPID"
sleep 1
if kill -0 $GPID 2>/dev/null; then
    echo "[START] gateway still running ok"
else
    echo "[START] gateway exited early!"
fi
echo "[START] launching server.py..."
exec python server.py
