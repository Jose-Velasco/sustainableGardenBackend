import serial
from .models import Sensor, SensorReading
import json
import time
import random


class SensorReader:
    def __init__(self, sensor: Sensor):
        self.sensor_info = {
            "pin": sensor.pin,
            "sensor": sensor.sensor_type
        }
        self.usb = sensor.usb_port

    def read(self):
        sensor_json = json.dumps(self.sensor_info).encode('UTF-8')

        ser = serial.Serial(self.usb, 115200, timeout=1)
        time.sleep(2)
        ser.flush()

        ser.write(sensor_json)
        time.sleep(1.5)
        out = ""
        while True:
            time.sleep(0.1)
            data = ser.readline().decode('utf-8').rstrip()
            if data:
                out += data
            else:
                out_json = json.loads(out)
                return out_json

def generate_test_sensor_readings(reading_outputs_json):
    for reading_output in reading_outputs_json:
        if reading_output == "Rain":
            reading_outputs_json[reading_output] = random.choice([0,1])
        else:
            reading_outputs_json[reading_output] = round(random.uniform(15.5, 35), 2)
    return reading_outputs_json

# Generates dummy hardcoded Sensors and SensorReadings with reading Json that are the same
# as the test readings located in the garden.dump file
def initialize_test_dependencies():
    hAndTSensor = Sensor.objects.create(
        sensor_name="Humidity and Temp",
        sensor_type="DHT11 - Humidity/Temperature",
        pin=1,
        in_use=True
    )
    SensorReading.objects.create(sensor=hAndTSensor, reading = {
        "Humidity": None,
        "Temperature": None
    })
    rainSensor = Sensor.objects.create(
        sensor_name="Rain",
        sensor_type="Rain Sensor",
        pin=2,
        in_use=True
    )
    SensorReading.objects.create(sensor=rainSensor, reading = {
        "Rain": None
    })

