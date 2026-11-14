import struct
import time
import random
from .packet import REGULAR_TELEMETRY,EMERGENCY_TELEMETRY


def generate_telemetry():

    """"
    Generate simulated spacecraft telemetry measurements and serialize them into a binary payload.

    Parameters:
     None

    Returns:
     bytes: A 17-byte serialized telemetry payload.

    """

    #Generating timestamp
    timestamp = int(time.time())

    #generating some random measurements
    temperature = random.uniform(15.0,30.0)
    battery = random.randint(40,100)
    voltage = random.uniform(5.0,8.4)
    current = random.uniform(0.5,1.5)
    #storing telemetry in dictionary
    telemetry = {'temperature': temperature,
                 'battery': battery,
                 'voltage': voltage,
                 'current': current,
                 'timestamp': timestamp
                 }

    packed_data = struct.pack('>IfBff',telemetry['timestamp'],telemetry['temperature'],telemetry['battery'],telemetry['voltage'],telemetry['current'] )

    return packed_data

def determine_packet_type(payload):
    """
    Takes in a dictionary of telemetry measurements and determines whether emergency type packet is needed

    Parameters:
        payload(bytes): Serialized telemetry measurements
    
    Returns: 
        int: regular or emergency
    """
    # unpack the serialized data
    telemetry = decode_telemetry(payload)
    # list of things to look out for: temp > 29 C, battery < 42%, voltage > 8.3V, current > 1.4A
    thresholds = {
        'temperature': 29,
        'battery': 42,
        'voltage': 8.3,
        'current': 1.4
    }
    for key,value in telemetry.items():
        if key == 'timestamp':
            continue
        if key == 'battery':
            if value < thresholds[key]:
                return EMERGENCY_TELEMETRY
            
        elif value > thresholds[key]:
            return EMERGENCY_TELEMETRY
    return REGULAR_TELEMETRY
             
        


    


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




#TEST

test_telemetry = {'timestamp': 12984, 'temperature': 27, 'battery': 60, 'voltage': 7, 'current': 0.9}

test_telemetry = struct.pack('>IfBff',test_telemetry['timestamp'],test_telemetry['temperature'], test_telemetry['battery'], test_telemetry['voltage'], test_telemetry['current'])

packet_type = determine_packet_type(test_telemetry)

print(packet_type)
