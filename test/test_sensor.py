from stoa.sensors import Sensor, SensorFactory
from stoa.constants import sensorDef

test_sensor_list = [

]


if __name__ == "__main__":
    s1 = Sensor(1, sensorDef.SENSOR_BINARY_SENSOR, "door")
    s2 = Sensor(2, sensorDef.SENSOR_BINARY_SWITCH, "lamp")

    sf = SensorFactory()
    sf.add_sensor(s1)
    sf.add_sensor(s2)

    print(sf)
