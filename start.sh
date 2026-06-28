#!/bin/bash
python gateway.py &
exec python server.py
