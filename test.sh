#!/bin/bash      


v4l2-ctl --device=1 --set-ctrl=auto_exposure=1
v4l2-ctl --device=1 --set-ctrl=exposure=10
v4l2-ctl --device=1 --set-ctrl=white_balance_automatic=0
v4l2-ctl --device=1 --set-ctrl=sharpness=63
v4l2-ctl --device=1 --set-ctrl=gain_automatic=0
v4l2-ctl --device=1 --set-ctrl=gain=10
v4l2-ctl --device=0 --set-ctrl=auto_exposure=1
v4l2-ctl --device=0 --set-ctrl=exposure=10
v4l2-ctl --device=0 --set-ctrl=white_balance_automatic=0
v4l2-ctl --device=0 --set-ctrl=sharpness=63
v4l2-ctl --device=0 --set-ctrl=gain_automatic=0
v4l2-ctl --device=0 --set-ctrl=gain=10 
python3 -u Main.py >> log

