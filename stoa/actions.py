import time
from .condition import ConditionOre
from .constants import sensorDef


ActionRefreshTime = {
    "default": 10
}


class ActionOre(object):
    @staticmethod
    def type():
        raise NotImplementedError("Need an action type")

    def __init__(self, *args):
        self._enabled = True
        self._last_execute_time = 0
        self._executed = False

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def _refresh(self):
        cur_time = time.time()
        if self.type() in ActionRefreshTime:
            action_type = self.type()
        else:
            action_type = "default"
        if cur_time - self._last_execute_time > ActionRefreshTime[action_type]:
            self._executed = False

    def _update(self):
        self._last_execute_time = time.time()
        self._executed = True

    def execute(self):
        self._refresh()
        if not self._enabled:
            return False

        if self._executed:
            return False

        self._action()
        self._update()
        return True

    def _action(self):
        print "Nothing to do"

    def to_dict(self):
        res = dict()
        res["method"] = self.type()
        return res

    def with_sensor(self):
        return None

    def has_sensor(self, sensor_id):
        return False


class SensorSet(ActionOre):
    @staticmethod
    def type():
        return "zwave_set"

    def __init__(self, value=None, sensor=None, point=None, delay=None, tmo=None):
        super(SensorSet, self).__init__()

        self.value = value
        self.sensor_id = int(sensor)
        self.point_id = int(point) if point else None
        self.delay = int(delay) if delay else 0
        self.tmo = int(tmo) if tmo else None
        # TODO: delay and tmo is not in used

    @classmethod
    def from_dict(cls, data):
        if data["method"] == cls.type():
            value = data.get("value")
            sensor = data.get("sensor")
            point = data.get("point")
            delay = data.get("delay")
            tmo = data.get("tmo")
            return cls(value, sensor, point, delay, tmo)
        else:
            raise RuntimeError("method in metadata does not match {}")

    def _action(self):
        if self.sensor_id is None:
            raise RuntimeError("SensorSet action is incomplete")
        if self.point_id is None:
            print "Setting sensor id:{0} to value:{1}".format(self.sensor_id, self.value)
        else:
            print "Setting sensor id:{0}, point:{1} to value:{2}".format(self.sensor_id, self.point_id, self.value)

    def active_once(self, value):
        if self.sensor_id is None:
            raise RuntimeError("SensorSet action is incomplete")
        if self.point_id is None:
            print "Setting sensor id:{0} to value:{1}".format(self.sensor_id, value)
        else:
            print "Setting sensor id:{0}, point:{1} to value:{2}".format(self.sensor_id, self.point_id, value)

    def __str__(self):
        if self.sensor_id is None:
            raise RuntimeError("SensorSet action is incomplete")
        if self.point_id is None:
            res = "set sensor id:{0} to value:{1}".format(self.sensor_id, self.value)
        else:
            res = "set sensor id:{0}, point:{1} to value:{2}".format(self.sensor_id, self.point_id, self.value)
        return res

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        res = dict()
        res["method"] = self.type()
        res["value"] = self.value
        res["sensor"] = self.sensor_id
        if self.point_id:
            res["point"] = self.point_id
        if self.delay:
            res["delay"] = self.delay
        if self.tmo:
            res["tmo"] = self.tmo
        return res

    def with_sensor(self):
        return int(self.sensor_id)

    def has_sensor(self, sensor_id):
        return sensor_id == self.sensor_id


class SecurityMode(ActionOre):
    @staticmethod
    def type():
        return "security_mode"

    def __init__(self, value=None):
        super(SecurityMode, self).__init__()
        self.value = value

    def _action(self):
        if self.value is None:
            raise RuntimeError("SecurityMode action is incomplete")
        print "Setting Security Mode to:{0}".format(self.value)

    def active_once(self, value):
        print "Setting Security Mode to:{0}".format(value)

    def to_dict(self):
        res = dict()
        res["value"] = self.value
        return res

    def __repr__(self):
        return self.__str__()


class Notification(ActionOre):
    @staticmethod
    def type():
        return "notify"

    def __init__(self, trigger):
        self.trigger_sensor = trigger.sensor.sensor_id
        self.trigger_type = trigger.type()
        self.trigger_target = trigger.target
        super(Notification, self).__init__()

    def _action(self):
        print "Notification: Sensor_{0} {1} {2}".format(
                                                 self.trigger_sensor,
                                                 self.trigger_type,
                                                 self.trigger_target)

    def __str__(self):
        return "Notify"

    def __repr__(self):
        return self.__str__()


class ActionGroup(ActionOre):
    @staticmethod
    def type():
        return "action_group"

    def __init__(self, *args):
        super(ActionGroup, self).__init__()

        self._list = list()
        for arg in args:
            self._list.append(arg)

    def add_action(self, action):
        if not isinstance(action, ActionOre):
            raise ValueError("Need a action object")

        self._list.append(action)

    def _action(self):
        if not self._list:
            print "Need at least one action"
        for action in self._list:
            action.execute()

    def __str__(self):
        if not self._list:
            return "Nothing to do"
        res = "[ {0} ]".format(", and ".join([str(x) for x in self._list]))
        return res

    def to_dict(self):
        res = list()
        for item in self._list:
            res.append(item.to_dict())
        return res

    def with_sensor(self):
        res = []
        for i in range(len((self._list))):
            s = self._list[i].with_sensor()
            if s:
                res.append(int(s))
        return res

    def has_sensor(self, sensor_id):
        return sensor_id in self.with_sensor()


action_table = {
    "zwave_set": SensorSet.from_dict,
    "notify": Notification,
    "security_mode": SecurityMode
}
