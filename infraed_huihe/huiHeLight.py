from .base import InfraedDevice


class HuiHeLight(InfraedDevice):


    def state(self):
        state = self.state
        if state is None:
            return "on"
        return state


    def brightness(self):
        #brightness = self.data.get('brightness')
        return 50
        return brightness


    def set_brightness(self, brightness):
            pass
        #self.data['brightness'] = brightness


    def support_color(self):
        return True

        # if self.data.get('color') is None:
        #     return False
        # else:
        #     return True


    def support_color_temp(self):

        return True
        # if self.dev_type=="0001-0201-0001":
        #     return False
        # else:
        #     if self.data.get('color_temp') is None:
        #
        #         return False
        #     else:
        #         return True


    def hs_color(self):
        pass
        # if self.data.get('color') is None:
        #     return None
        # else:
        #     work_mode = self.data.get('color_mode')
        #     if work_mode == 'colour':
        #         color = self.data.get('color')
        #         return color.get('hue'), color.get('saturation')
        #     else:
        #         return 0.0, 0.0


    def color_temp(self):
        pass
        # if self.data.get('color_temp') is None:
        #     return None
        # else:
        #     return self.data.get('color_temp')


    def min_color_temp(self):
        return 5500


    def max_color_temp(self):
        return 2800


    def turn_on(self):

        self.api.device_control(self.obj_id,1)
        self.state = "on"
        return


    def turn_off(self):
        self.api.device_control(self.obj_id,1)
        self.state = "off"
        return



    def set_brightness(self, brightness):
        """Set the brightness(0-255) of light."""

        pass
        #value = int(brightness * 100 / 255)
        #self.api.device_control(self.obj_id, 'brightness', value)


    def set_color(self, color):
        """Set the color of light."""
        pass

        # hsv_color = {}
        # hsv_color['hue'] = color[0]
        # hsv_color['saturation'] = color[1]/100
        # if (len(color) < 3):
        #     hsv_color['brightness'] = int(self.brightness()) / 255.0
        # else:
        #     hsv_color['brightness'] = color[2]
        # # color white
        # if hsv_color['saturation'] == 0:
        #     hsv_color['hue'] = 0
        # self.api.device_control(self.obj_id, 'colorSet', {'color': hsv_color})


    def set_color_temp(self, color_temp):
        pass
        # self.api.device_control(self.obj_id, 'CCT', color_temp)
