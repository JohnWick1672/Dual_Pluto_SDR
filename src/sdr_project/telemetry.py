import struct
import time
import random


def generate_telemetry():

    """"
    Generate simulated spacecraft telemetry measurements and serialize them    into a binary payload.

    Parameters:
     None

    Returns:
     bytes: A 17-byte serialized telemetry payload.

    """

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



def decode_telemetry(payload):

    """
    Deserialize a binary telemetry payload into readable measurements.

    Parameters:
        payload (bytes): The 17-byte serialized telemetry payload.

    Returns:
        dict: Dictionary where values can be accesed through the keys: timestamp, temperature, battery, voltage, and current.
    """
    #using known format of >'IfBff unpack the telemetry
    timestamp, temperature, battery,voltage, current = struct.unpack('>IfBff', payload)

    telemetry = {'timestamp': timestamp, 'temperature': temperature, 'battery': battery, 'voltage': voltage ,'current': current}

    return telemetry