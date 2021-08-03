from django.http import Http404
from .sensor_in import SensorReader, generate_test_sensor_readings, initialize_test_dependencies
from .models import Sensor, SensorReading
from .serializers import SensorSerializer, SensorReadingSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from sustainableGardenBackend.settings import DEBUG
from datetime import datetime, timezone


class SensorList(generics.ListCreateAPIView):
    """
    List all sensors, or add a new sensor
    """
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


class SensorDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a sensor.
    """
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


class SensorRead(APIView):
    def get_object(self, pk):
        try:
            return Sensor.objects.get(pk=pk)
        except Sensor.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        sensor = self.get_object(pk)
        reader = SensorReader(sensor)
        data = reader.read()
        return Response(data)


class SensorReadAll(APIView):
    """
    View to read all current sensor values
    """

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # for testing purposes: creates two Sensors and adds them to the database in in order
        # to make random SensorReadings
        if DEBUG and len(SensorReading.objects.all()) == 0 and len(Sensor.objects.all()) == 0:
            initialize_test_dependencies()

    def get(self, request):
        sensors = [sensor for sensor in Sensor.objects.all()]
        readings = []
        for sensor in sensors:
            reader = SensorReader(sensor)
            # creates a SensorReading with random readings based on the amount of readings the Sensor object should have
            # from previously created SensorReading in the database
            if "is_endpoint_test" in request.query_params and request.query_params["is_endpoint_test"]:
                sensor_readings = SensorReading.objects.filter(sensor=sensor).first()
                reading = generate_test_sensor_readings(sensor_readings.reading)
                new_SensorReading = SensorReading(sensor=sensor, reading=reading, time_of_reading=datetime.now(timezone.utc))
                serializer = SensorReadingSerializer(new_SensorReading)
                readings.append(serializer.data)
            else:
                reading = reader.read()
                reading["sensor_pk"] = sensor.pk
                readings.append(reading)
        return Response(readings)
    
    # Creates and saves SenorReadings with random readings data
    @transaction.atomic
    def post(self, request):
        sensors = [sensor for sensor in Sensor.objects.all()]
        readings = []
        for sensor in sensors:
            sensor_readings = SensorReading.objects.filter(sensor=sensor).first()
            reading = generate_test_sensor_readings(sensor_readings.reading)
            new_sensor_reading = SensorReading.objects.create(sensor=sensor, reading=reading)
            serializer = SensorReadingSerializer(new_sensor_reading)
            readings.append(serializer.data)
        return Response(readings, 201)


class SensorReadingList(generics.ListAPIView):
    queryset = SensorReading.objects.order_by("time_of_reading")
    serializer_class = SensorReadingSerializer
