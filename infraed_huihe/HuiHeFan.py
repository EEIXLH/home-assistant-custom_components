from .base import InfraedDevice

class HuiHeFanDevice(InfraedDevice):


    def state(self):
        state = self.state
        if state is None:
            return "on"
        return state


    def speed(self):
        return "high"


    def speed_list(self):
        speed_list = ["off","low","medium""high"]
        return speed_list


    def oscillating(self):
        return "forward"


    def set_speed(self, speed):
        sendResponse = self.api.device_control(self.obj_id, 9367)
        if sendResponse == True:
            self.state = "on"

        return


    def oscillate(self, oscillating):

        sendResponse = self.api.device_control(self.obj_id, 9362)
        if sendResponse == True:
            self.state = "on"


    def turn_on(self):
        sendResponse = self.api.device_control(self.obj_id, 1)
        if sendResponse == True:
            self.state = "on"

        return


    def turn_off(self):
        sendResponse = self.api.device_control(self.obj_id, 1)
        if sendResponse == True:
            self.state = "off"

        return


    def support_oscillate(self):
        return True


    def support_direction(self):
        return True