from stoa.sensors import Sensor


class Trigger(object):
    def __init__(self, target, point=None):
        self.target = target
        self.prev = None
        self.value = None
        self.point = point
        self.action = None
        self.sensor = None

    def get_sensor(self):
        if self.point is None:
            self.value = self.sensor.get_value()
        else:
            self.value = self.sensor.get_point(self.point)

    def update(self):
        self.prev = self.value

    def attach_sensor(self, sensor):
        self.sensor = sensor

    def check(self):
        if not self.action:
            return False

        self.get_sensor()

        if self.prev is None:
            self.update()

        if self.logic():
            self.action.execute()

        self.update()

        return True

    def assign(self, action):
        self.action = action

    def get_action(self):
        return self.action

    def logic(self):
        return self.value == self.target and self.prev != self.target

    def __str__(self):
        return "When sensor {0} matches {1}, {2}".format(self.sensor.sensor_id, self.target, self.action)


class RisingEdge(Trigger):
    def logic(self):
        return self.value > self.target >= self.prev

    def __str__(self):
        return "When sensor {0} rises above {1}, {2}".format(self.sensor.sensor_id, self.target, self.action)


class FallingEdge(Trigger):
    def logic(self):
        return self.value < self.target <= self.prev

    def __str__(self):
        return "When sensor {0} falls below {1}, {2}".format(self.sensor.sensor_id, self.target, self.action)


trigger_table = {
    "match": Trigger,
    "rise": RisingEdge,
    "fall": FallingEdge
}
