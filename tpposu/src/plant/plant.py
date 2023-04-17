from os import getcwd
from ctypes import CDLL, POINTER, c_double, c_int


class Plant:
    def __init__(self, dll_path=None):
        if dll_path is None:
            dll_path = 'src\plant\PlantDLL.dll'
        self.dll = CDLL(dll_path)
        self.dll.plant_init.argstype = [POINTER(c_double)]

        self.dll.plant_measure.argstype = [c_int, POINTER(c_double)]
        self.dll.plant_measure.restype = c_double

        self.dll.plant_control.argstype = [c_int, c_double, POINTER(c_double)]

        self.plant = (POINTER(c_double) * 53)()
        self.init()

    def init(self):
        return self.dll.plant_init(self.plant)

    def measure(self, kanal):
        return self.dll.plant_measure(kanal, self.plant)

    def control(self, kanal, urp):
        return self.dll.plant_control(kanal, urp, self.plant)

    def get_measures_from_channel(self, channel, steps=1):
        measures = []
        for i in range(0, steps):
            measure = self.dll.plant_measure(channel, self.plant)
            measures.append(measure)
        return measures