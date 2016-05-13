import time

from stoa.observers import Node
#from stoa.dbus_sender import DBusSender


ActionRefreshTime = {
    "default": 10
}


class ActionOre(object):
    @staticmethod
    def type():
        return "default"

    def __init__(self, *args):
        self._enabled = True
        self._last_execute_time = 0
        self._executed = False
        self._observer = None

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

    def add_observer(self, observer):
        if not isinstance(observer, Node):
            raise ValueError("Need to an observer or a logic")
        self._observer = observer

    def observer_dict(self):
        if self._observer:
            return self._observer.to_dict()
        else:
            return None

    def execute(self):
        self._refresh()
        if not self._enabled:
            return False

        if self._executed:
            return False

        if self._observer is None or self._observer.check():
            self._action()
            self._update()
            return True
        return False

    def _action(self):
        print("Nothing to do")

    def to_dict(self):
        res = dict()
        res["method"] = self.type()
        return res


class Action(ActionOre):
    def __init__(self, value, sensor, point=None, delay=None, tmo=None):
        super(Action, self).__init__()

        self.value = value
        self.sensor_id = int(sensor)
        self.point_id = int(point) if point else None
        self.delay = int(delay) if delay else 0
        self.tmo = int(tmo) if tmo else None

    def _action(self):
        if self.point_id is None:
            print("Setting sensor id:{0} to value:{1}".format(self.sensor_id, self.value))
        else:
            print("Setting sensor id:{0}, point:{1} to value:{2}".format(self.sensor_id, self.point_id, self.value))

    def __str__(self):
        if self.point_id is None:
            res = "set sensor id:{0} to value:{1}".format(self.sensor_id, self.value)
        else:
            res = "set sensor id:{0}, point:{1} to value:{2}".format(self.sensor_id, self.point_id, self.value)
        if self._observer:
            res += ", if ( {0} )".format(self._observer)
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


class Notification(ActionOre):
    @staticmethod
    def type():
        return "notify"

    def __init__(self, trigger):
        self.trigger = trigger
        super(Notification, self).__init__()

    def _action(self):
        print("Notification: Sensor_{0} {1} {2}".format(
                                                 self.trigger.sensor.sensor_id,
                                                 self.trigger.type(),
                                                 self.trigger.target))

    def __str__(self):
        return "Notify"

    def __repr__(self):
        return self.__str__()


class ActionGroup(ActionOre):
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
            print("Need at least one action")
        for action in self._list:
            action.execute()

    def __str__(self):
        if not self._list:
            return "Nothing to do"
        res = "[ {0} ]".format(", and ".join([str(x) for x in self._list]))
        if self._observer:
            res += ", if ( {0} )".format(self._observer)
        return res

    def to_dict(self):
        res = list()
        for item in self._list:
            res.append(item.to_dict())
        return res

action_table = {
    "default": Action,
    "notify": Notification
}
