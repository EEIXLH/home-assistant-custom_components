from .base import InfraedDevice

class HuiHeSwitch(InfraedDevice):


    def state(self):
        state = self.state
        if state is None:
            return "on"
        # return "on"
        return state


    def turn_on(self):
        self.api.device_control(self.obj_id,1)


    def turn_off(self):
        self.api.device_control(self.obj_id,1)


