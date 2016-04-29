import time

from stoa.observers import Node


ActionRefreshTime = {
    "default": 10
}


class ActionOre(object):
    @staticmethod
    def type():
        return "default"

    def __init__(self):
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
        if cur_time - self._last_execute_time > ActionRefreshTime[self.type()]:
            self._executed = False

    def _update(self):
        self._last_execute_time = time.time()
        self._executed = True

    def add_observer(self, observer):
        if not isinstance(observer, Node):
            raise ValueError("Need to an observer or a logic")
        self._observer = observer

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


class Action(ActionOre):
    def __init__(self, value, sensor, point=None, delay=None, tmo=None):
        super(Action, self).__init__()

        self.value = value
        self.sensor_id = sensor
        self.point_id = point
        self.delay = delay if delay else 0
        self.tmo = tmo

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


class ActionGroup(ActionOre):
    def __init__(self, *args):
        super(ActionGroup, self).__init__()

        self._list = list()
        for arg in args:
            self._list.append(arg)

    def add_action(self, action):
        if not isinstance(action, Action):
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


action_table = {
    "default": Action
}
