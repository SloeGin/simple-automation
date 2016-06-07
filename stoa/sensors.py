from stoa.constants import sensorDef
import time


class Sensor(object):
    _ID_list = list()

    def __init__(self, sensor_id, sensor_type, name=None):
        self._points = dict()
        self._enabled = True
        self.type = int(sensor_type)
        self.name = name
        self.value = None
        if sensor_id in self._ID_list:
            raise ValueError("Sensor ID exists!")
        self.__class__._ID_list.append(sensor_id)
        self.sensor_id = sensor_id
        self._triggers = list()

    def is_actable(self):
        return self.type in sensorDef.automatable_sensor_types

    def is_triggerable(self):
        if self.type == 0:
            return True
        else:
            return self.type in sensorDef.triggerable_sensor_types

    def load_point_list(self, points):
        for point in points:
            self.update_point(point)

    def update_point(self, point):
        self._points[point["point_id"]] = point

    def update_value(self, value, point=None):
        init = False
        if point is None:
            if self.value is None:
                init = True
            self.value = value
        else:
            if self._points[point] is None:
                init = True
            self._points[point] = value

        if not init:
            self.handle_data()

    def disable_trigger(self, index):
        self._triggers[index].disable()

    def enable_trigger(self, index):
        self._triggers[index].enable()

    def get_value(self):
        if self._enabled:
            return self.value
        else:
            return None

    def get_point(self, point):
        if point in self._points and self._enabled:
            return self._points[point]
        else:
            return None

    def list_point(self):
        return self._points

    def add_trigger(self, trigger):
        self._triggers.append(trigger)
        trigger.attach_sensor(self)
        return self._triggers.index(trigger)

    def handle_data(self):
        for trigger in self._triggers:
            trigger.check()

    def get_last_trigger(self):
        if self._triggers is not None:
            return self._triggers[-1]
        else:
            return None

    def has_trigger(self):
        if self._triggers:
            return True
        else:
            return False

    def get_trigger(self, index):
        try:
            return self._triggers[index]
        except:
            print("Index out of range")
            return None

    def remove_trigger(self, index):
        try:
            if index is None:
                self._triggers.pop()
            else:
                self._triggers.pop(index)
        except Exception as e:
            print("{0}".format(e))

    def __str__(self):
        res = "Sensor: id = {id}\n\tname = {name}\n\tvalue = {value}".format(
            id=self.sensor_id,
            name=self.name,
            value=self.value
        )
        for point, value in self._points.items():
            res += "\n\tpoint: {p}, type: {t}, value: {v}".format(
                p=str(point),
                t=str(value["point_type"]),
                v=str(value["point_value"])
            )
        for i in range(len(self._triggers)):
            res += "\n\ttrigger: {i} - {t}".format(
                i=i,
                t=str(self._triggers[i])
            )
        return res + "\n"

    def to_dict(self):
        res = list()
        for trigger in self._triggers:
            rule = dict()
            rule["sensor"] = trigger.sensor.sensor_id
            rule["enabled"] = trigger.enabled
            rule["trigger"] = trigger.to_dict()
            rule["action"] = trigger.action.to_dict()
            rule["observer"] = trigger.action.observer_dict()
            res.append(rule)
        return res if res else None


class Clock(Sensor):
    def get_value(self):
        return time.time()
