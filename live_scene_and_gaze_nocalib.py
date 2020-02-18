# live_scene_and_gaze.py : A demo for video streaming and synchronized gaze
#
# Copyright (C) 2018  Davide De Tommaso
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import cv2
import numpy as np

if hasattr(__builtins__, 'raw_input'):
      input=raw_input

from tobiiglassesctrl import TobiiGlassesController

ipv4_address = "192.168.71.50"

tobiiglasses = TobiiGlassesController(ipv4_address, video_scene=True)
tobiiglasses.start_streaming()
video_freq = tobiiglasses.get_video_freq()

frame_duration = 1000.0/float(video_freq) #frame duration in ms

input("Press ENTER to start the video scene")

cap = cv2.VideoCapture("rtsp://%s:8554/live/scene" % ipv4_address)

# Check if camera opened successfully
if (cap.isOpened()== False):
  print("Error opening video stream or file")

# Read until video is completed
while(cap.isOpened()):
  # Capture frame-by-frame
  ret, frame = cap.read()
  if ret == True:

    height, width = frame.shape[:2]
    data_gp  = tobiiglasses.get_data()['gp']
    data_pts = tobiiglasses.get_data()['pts']
    print(data_gp, data_pts)
    offset = data_gp['ts']/1000000.0 - data_pts['ts']/1000000.0
    if offset > 0.0 and offset <= frame_duration:
        cv2.circle(frame,(int(data_gp['gp'][0]*width),int(data_gp['gp'][1]*height)), 60, (0,0,255), 6)
    # Display the resulting frame
    cv2.imshow('Tobii Pro Glasses 2 - Live Scene',frame)

    # Press Q on keyboard to  exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  # Break the loop
  else:
    break

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
tobiiglasses.stop_streaming()
tobiiglasses.close()
