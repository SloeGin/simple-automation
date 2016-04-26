from stoa.constants import sensorDef
import time


class Sensor(object):
    _ID_list = list()

    def __init__(self, sensor_id, sensor_type, name=None):
        self._point = dict()
        self._enabled = True
        self.type = int(sensor_type)
        self.name = name
        self.value = None
        if sensor_id in self._ID_list:
            raise ValueError("Sensor ID exists!")
        self.__class__._ID_list.append(sensor_id)
        self.sensor_id = sensor_id

    def is_controllable(self):
        return self.type in sensorDef.controllable_sensor

    def update_point(self, point, type, value=None):
        self._point[point] = {"point_id": point, "type": type, "value": value}

    def update_value(self, value):
        self.value = value

    def disable(self):
        self._enabled = False

    def enable(self):
        self._enabled = True

    def get_value(self):
        if self._enabled:
            return self.value

    def get_point(self, point):
        if point in self._point and self._enabled:
            return self._point[point]
        else:
            return None

    def list_point(self):
        return self._point


class Clock(Sensor):
    def get_value(self):
        return time.time()


class SensorFactory(object):
    def __init__(self):
        self._dict = dict()
        self._dict[0] = Clock(0, 0, "clock")

    def list(self):
        return self._dict

    def __iter__(self):
        return iter(self._dict)

    def add_sensor(self, sensor):
        if isinstance(sensor, Sensor):
            if sensor.sensor_id == 0:
                raise ValueError("Fatal error: cannot overwrite system clock")
            if sensor.sensor_id in self._dict:
                raise ValueError("Sensor ID exists!")
            self._dict[sensor.sensor_id] = sensor
        else:
            try:
                if sensor["id"] == 0:
                    raise ValueError("Fatal error: cannot overwrite system clock")
                if sensor["id"] in self._dict:
                    raise ValueError("Sensor ID exists!")
                new_sensor = Sensor(sensor["id"], sensor["type"], sensor["name"])
                if "points" in sensor:
                    for point in sensor["points"]:
                        new_sensor.update_point(point["point_id"], point["type"])
                self._dict[sensor["id"]] = new_sensor
            except:
                print("Wrong sensor format")

        return True

    def __str__(self):
        res = "Sensors:\n"
        for key, item in self._dict.items():
            res += "\t<{0}>: type={1}, name={2}, value = {3}\n".format(
                key, item.type, item.name, item.value
            )
        return res

    def get_sensor(self, sensor_id):
        return self._dict[sensor_id]

    def sensors(self):
        yield self._dict
