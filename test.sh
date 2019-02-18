#!/bin/bash      


v4l2-ctl --device=1 --set-ctrl=auto_exposure=1
v4l2-ctl --device=1 --set-ctrl=exposure=10
v4l2-ctl --device=1 --set-ctrl=white_balance_automatic=0
v4l2-ctl --device=1 --set-ctrl=sharpness=63
v4l2-ctl --device=1 --set-ctrl=gain_automatic=0
v4l2-ctl --device=1 --set-ctrl=gain=10
v4l2-ctl --device=2 --set-ctrl=auto_exposure=1
v4l2-ctl --device=2 --set-ctrl=exposure=10
v4l2-ctl --device=2 --set-ctrl=white_balance_automatic=0
v4l2-ctl --device=2 --set-ctrl=sharpness=63
v4l2-ctl --device=2 --set-ctrl=gain_automatic=0
v4l2-ctl --device=2 --set-ctrl=gain=10
python3 Main.py 
# python3 camera_calibration.py -oconstants 1.png 2.png 3.png 4.png 5.png 6.png 7.png 8.png 9.png 10.png 11.png 12.png 13.png 14.png 15.png 16.png 17.png 18.png 19.png 20.png 21.png 22.png 23.png 24.png 25.png 26.png 27.png 28.png 29.png 30.png 31.png 32.png 

