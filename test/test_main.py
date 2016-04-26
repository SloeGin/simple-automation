from stoa.sensors import Sensor, SensorFactory
from stoa.constants import sensorDef
from stoa.actions import Action, ActionGroup
from stoa.observers import Logic, Observer
from stoa.triggers import Trigger

if __name__ == "__main__":

    s1 = Sensor(1, sensorDef.SENSOR_BINARY_SENSOR, "door")
    s2 = Sensor(2, sensorDef.SENSOR_BINARY_SWITCH, "lamp 1")
    s3 = Sensor(3, sensorDef.SENSOR_MOTION, "motion")
    s4 = Sensor(4, sensorDef.SENSOR_MULTILEVEL_SWITCH, "lamp 2")
    s5 = Sensor(5, sensorDef.SENSOR_TEMPERATURE, "temp")
    s6 = Sensor(6, sensorDef.SENSOR_MULTILEVEL_SWITCH, "lamp 3")

    sf = SensorFactory()
    sf.add_sensor(s1)
    sf.add_sensor(s2)
    sf.add_sensor(s3)
    sf.add_sensor(s4)
    sf.add_sensor(s5)
    sf.add_sensor(s6)

    t1 = Trigger(1, s1)
    t2 = Trigger(1, s3)

    tl = list()
    tl.append(t1)
    tl.append(t2)

    a1 = Action(1, 2)
    a2 = Action(50, 4)
    a3 = Action(61, 6)
    ag1 = ActionGroup(a2, a3)

    t1.assign(a1)
    t2.assign(ag1)

    o1 = Observer("=wd=", None, sf.get_sensor(0))
    o2 = Observer("=g=", 26, sf.get_sensor(5))
    o3 = Observer("=we=", None, sf.get_sensor(0))
    l1 = Logic(o2, "and", o3)

    a1.add_observer(o1)
    ag1.add_observer(l1)

    print(t1)
    print(t2)
    print()

    s1.update_value(0)
    s3.update_value(0)
    print(sf)
    for t in tl:
        t.check()

    s1.update_value(1)
    s3.update_value(1)
    s5.update_value(27)
    print(sf)
    for t in tl:
        t.check()

    s1.update_value(0)
    s3.update_value(0)
    print(sf)
    for t in tl:
        t.check()

    s1.update_value(1)
    s3.update_value(1)
    s5.update_value(27)
    print(sf)
    for t in tl:
        t.check()