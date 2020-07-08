# streaming_into_lsl.py : A demo for data streaming into LabStreamingLayer
#
# Tested on Windows 10 and Python 3.7.7
# Requires: pylsl library - https://github.com/chkothe/pylsl
#
# Copyright (C) 2020  Juan Antonio Barragan N
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>

import time
from tobiiglassesctrl import TobiiGlassesController
from pylsl import StreamInfo, StreamOutlet
import traceback


class StreamsObj:

    """
    The following class contains all the information of the streams that are going to be created in LSL.

    Stream List:
    1) gaze_position
    2) gaze_position_3d
    3) left_eye_data
    4) right_eye_data
    5) mems

    """
    sf = 0 # Irregular stream of data
    stream_channels = {'gaze_position': ['gidx', 's', 'gpx', 'gpy'],
                       'gaze_position_3d': ['gidx', 's', 'gp3dx', 'gp3dy', 'gp3dz'],
                       'left_eye_data': ['gidx', 's', 'pcx', 'pcy', 'pcz', 'pd', 'gdx', 'gdy', 'gdz'],
                       'right_eye_data': ['gidx', 's', 'pcx', 'pcy', 'pcz', 'pd', 'gdx', 'gdy', 'gdz'],
                       'mems': ['acx', 'acy', 'acz', 'gyx', 'gyy', 'gyz']
                       }

    stream_descriptions = {'gaze_position': ['gaze_position', 'eye_tracker', 4, sf, 'float32', 'gaze_position_lsl_id'],
                           'gaze_position_3d': ['gaze_position_3d', 'eye_tracker', 5, sf, 'float32',
                                                'gaze_position__3d_lsl_id'],
                           'left_eye_data': ['left_eye_data', 'eye_tracker', 9, sf, 'float32', 'left_eye_data_lsl_id'],
                           'right_eye_data': ['right_eye_data', 'eye_tracker', 9, sf, 'float32',
                                              'right_eye_data_lsl_id'],
                           'mems': ['accelerometer_gyro_tobii', 'eye_tracker', 6, sf, 'float32',
                                    'accelerometer_gyro__lsl_id']
                           }

    def __init__(self):

        """
        Initialize LSL outlets
        """
        self.outlets_dict = {}

        # Iterate over all the stream names
        for key in self.stream_channels.keys():
            outlet = self.create_stream(key)
            self.outlets_dict[key] = outlet

    def create_stream(self, stream_name):
        # Configure LSL streams
        info = StreamInfo(*self.stream_descriptions[stream_name])

        # append channels meta-data
        channels = info.desc().append_child("channels")
        for c in self.stream_channels[stream_name]:
            if c == 'gidx':
                channels.append_child("channel") \
                    .append_child_value("name", c) \
                    .append_child_value("unit", "na") \
                    .append_child_value("type", "marker")
            elif c == 's':
                channels.append_child("channel") \
                    .append_child_value("name", c) \
                    .append_child_value("unit", "na") \
                    .append_child_value("type", "marker")
            else:
                channels.append_child("channel") \
                    .append_child_value("name", c) \
                    .append_child_value("unit", "mm") \
                    .append_child_value("type", "coordinate")

        outlet = StreamOutlet(info)

        return outlet

    def sendData(self, name, data):
        """
        Send data to the different streams

        :param name: Str used to indicate which stream to use to send the data.
        :param data: Data that is going to be send.

        :return:
        """
        if name == 'left_eye':
            # 'left_eye_data': ['gidx','s','pcx','pcy','pcz','pd','gdx','gdy','gdz']
            d1 = data['pc']
            d2 = data['pd']
            d3 = data['gd']

            dataToSend = [d1['gidx'], d1['s']] + d1['pc'] + [d2['pd']] + d3['gd']
            self.outlets_dict['left_eye_data'].push_sample(dataToSend)

        elif name == 'right_eye':
            # 'right_eye_data': ['gidx','s','pcx','pcy','pcz','pd','gdx','gdy','gdz'],
            d1 = data['pc']
            d2 = data['pd']
            d3 = data['gd']

            dataToSend = [d1['gidx'], d1['s']] + d1['pc'] + [d2['pd']] + d3['gd']
            self.outlets_dict['right_eye_data'].push_sample(dataToSend)

        elif name == 'gp':
            # 'gaze_position -- > ['gidx','s','gpx','gpy']
            dataToSend = [data['gidx'], data['s']] + data['gp']
            self.outlets_dict['gaze_position'].push_sample(dataToSend)

        elif name == 'gp3':
            # 'gaze_position_3d':['gidx','s','gp3dx','gp3dy','gp3dz']
            dataToSend = [data['gidx'], data['s']] + data['gp3']
            self.outlets_dict['gaze_position_3d'].push_sample(dataToSend)

        elif name == 'mems':
            ac_data = data['ac']
            gy_data = data['gy']
            dataToSend = [] + ac_data['ac'] + gy_data['gy']
            self.outlets_dict['mems'].push_sample(dataToSend)



def main():
    # Configure LSL streams
    lsl_streams = StreamsObj()

    # Create Tobii glasses Controller
    tobiiglasses = TobiiGlassesController("192.168.71.50")

    # Start Streaming
    tobiiglasses.start_streaming()

    print("Please wait ...")
    time.sleep(1.0)

    input("Press any key to start streaming")

    old_time = time.time()
    try:
        while True:

            data = tobiiglasses.get_data()

            if time.time() - old_time > 0.020:  # Send data every 20ms/50Hz
                lsl_streams.sendData('mems', data['mems'])
                lsl_streams.sendData('left_eye', data['left_eye'])
                lsl_streams.sendData('right_eye', data['right_eye'])
                lsl_streams.sendData('gp', data['gp'])
                lsl_streams.sendData('gp3', data['gp3'])

                old_time = time.time()

    except Exception:
        trace = traceback.format_exc()
        print(trace)

    finally:
        tobiiglasses.stop_streaming()
        tobiiglasses.close()


if __name__ == '__main__':
    main()
