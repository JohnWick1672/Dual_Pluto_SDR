import struct
import time
import random


def generate_telemetry():


    #Generating timestamp
    timestamp = int(time.time())

    #generating some random measurements
    temperature = random.uniform(20.0,30.0)
    battery = random.randint(80,100)
    voltage = random.uniform(7.0,8.4)
    current = random.uniform(0.5,1.2)
    #storing telemetry in dictionary
    telemetry = {'temperature': temperature,
                 'battery': battery,
                 'voltage': voltage,
                 'current': current,
                 'timestamp': timestamp
                 }

    packed_data = struct.pack('>IfBff',telemetry['timestamp'],telemetry['temperature'],telemetry['battery'],telemetry['voltage'],telemetry['current'] )

    return packed_data



