from.condition import ConditionOre
from datetime import datetime


class Trigger(object):
    """
    {
      "method":"match",
      "target":1,
      "enabled":true,
    }
    """
    @staticmethod
    def type():
        return "match"

    def __init__(self, target, point=None):
        self.target = target
        self.prev = None
        self.value = None
        self.point = point
        self.action = None
        self.condition = None
        self.sensor = None
        self.enabled = True

    def get_sensor_update(self):
        if self.point is None:
            self.value = self.sensor.get_value()
        else:
            self.value = self.sensor.get_point(self.point)

    def update(self):
        self.prev = self.value

    def attach_sensor(self, sensor):
        self.sensor = sensor

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def check(self):
        if not self.action:
            return False

        self.get_sensor_update()

        if self.prev is None:
            self.update()

        if self.enabled and self.logic():
            if self.condition is None or self.condition():
                self.action.execute()

        self.update()

        return True

    def assign_action(self, action):
        self.action = action

    def get_action(self):
        return self.action

    def add_condition(self, condition):
        if not isinstance(condition, ConditionOre):
            raise ValueError("Need to an condition or a logic gate")
        self.condition = condition

    def condition_dict(self):
        if self.condition:
            return self.condition.to_dict()
        else:
            return None

    def is_validated(self):
        if not self.sensor.is_triggerable():
            return False
        if not self.action:
            return False
        return True

    def to_dict(self):
        res = dict()
        res["method"] = self.type()
        res["target"] = self.target
        return res

    def logic(self):
        return self.value == self.target and self.prev != self.target

    def __str__(self):
        res = "When sensor {0} matches {1}, {2}".format(self.sensor.sensor_id, self.target, self.action)
        if self.condition:
            res += ", if ( {0} )".format(self.condition)
        return res


class RisingEdge(Trigger):
    @staticmethod
    def type():
        return "rise"

    def logic(self):
        return self.value > self.target >= self.prev

    def __str__(self):
        return "When sensor {0} rises above {1}, {2}".format(self.sensor.sensor_id, self.target, self.action)


class FallingEdge(Trigger):
    @staticmethod
    def type():
        return "fall"

    def logic(self):
        return self.value < self.target <= self.prev

    def __str__(self):
        return "When sensor {0} falls below {1}, {2}".format(self.sensor.sensor_id, self.target, self.action)


class TimeReach(Trigger):
    @staticmethod
    def type():
        return "time"

    def logic(self):
        now = datetime.fromtimestamp(self.value)
        target = datetime.fromtimestamp(self.target)
        prev = datetime.fromtimestamp(self.prev)

        hour = target.hour
        minute = target.minute
        second = target.second

        target = now.replace(hour=hour, minute=minute, second=second)

        if now >= target > prev:
            return True
        else:
            return False

    def __str__(self):
        return "When time pass {0}, {1}".format(self.target, self.action)


class Changed(Trigger):
    @staticmethod
    def type():
        return "changed"

    def logic(self):
        return self.value != self.prev

    def __str__(self):
        return "When sensor {0} changes, {1}".format(self.sensor.sensor_id, self.action)


trigger_table = {
    "match": Trigger,
    "rise": RisingEdge,
    "fall": FallingEdge,
    "time": TimeReach,
    "change": Changed
}
