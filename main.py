from math import cos, sqrt, radians, floor
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


class HomeScreen(Screen):
    pass


GUI = Builder.load_file("main.kv")


class MainApp(App):
    def build(self):
        return GUI

    def enable_button(self):
        alt_airport = self.root.ids['home_screen'].ids['alt_airport'].text
        wind_direction = self.root.ids['home_screen'].ids['wind_direction'].text
        windspeed = self.root.ids['home_screen'].ids['windspeed'].text
        holding_mins = self.root.ids['home_screen'].ids['holding_mins'].text
        fuel_onboard = self.root.ids['home_screen'].ids['fuel_onboard'].text
        dist_from_syd = self.root.ids['home_screen'].ids['dist_from_syd']

        go_button = self.root.ids['home_screen'].ids['go_button']
        if alt_airport and wind_direction and windspeed and holding_mins and fuel_onboard and dist_from_syd:
            go_button.disabled = False
        else:
            go_button.disabled = True

    def calculate(self):
        try:
            alt_airport = self.root.ids['home_screen'].ids['alt_airport'].text

            # WIND SPEED AND DIRECTION
            wind_direction = self.root.ids['home_screen'].ids['wind_direction'].text
            wind_direction = int(wind_direction)
            windspeed = self.root.ids['home_screen'].ids['windspeed'].text
            windspeed = int(windspeed)

            # WIND COMPONENT TO CONTINUE TO LHI
            track_to_continue = 61  # 061 actual track sydney to lhi
            continue_offset = abs(wind_direction - track_to_continue)
            continue_rads = radians(continue_offset)
            wind_to_continue = round(-(cos(continue_rads) * windspeed))

            # TRACKS FROM LHI TO RESPECTIVE ALTERNATE AIRPORT
            if alt_airport == 'CFS' or alt_airport == 'YCFS':
                track_to_divert = 268
                dist_to_alt = 239
                track_diff = 47
                tas = 212
                fuel_flow = 1086
            elif alt_airport == 'PMQ' or alt_airport == 'YPMQ':
                track_to_divert = 256
                dist_to_alt = 173
                track_diff = 42
                tas = 212
                fuel_flow = 1086
            elif alt_airport == 'NTL' or alt_airport == 'WLM' or alt_airport == 'YWLM':
                track_to_divert = 244
                dist_to_alt = 76
                track_diff = 46
                tas = 212
                fuel_flow = 1086
            elif alt_airport == 'TMW' or alt_airport == 'YSTW':
                track_to_divert = 258
                dist_to_alt = 173
                track_diff = 77  ######### Written as an 83 degree variation in FCOM but it should be 77
                tas = 212
                fuel_flow = 1086
            elif alt_airport == 'BNE' or alt_airport == 'YBBN':
                track_to_divert = 293
                dist_to_alt = 407
                track_diff = 56
                tas = 212
                fuel_flow = 1086
            elif alt_airport == 'BNK' or alt_airport == 'BNA' or alt_airport == 'YBNA':
                track_to_divert = 284
                dist_to_alt = 330
                track_diff = 50
                tas = 211
                fuel_flow = 1025
            elif alt_airport == 'SYD' or alt_airport == 'YSSY':  # trialling sydney for a PSD as it's been discussed in flight many times
                track_to_divert = 360
                dist_to_alt = 0
                track_diff = 0
                tas = 211
                fuel_flow = 1025
            else:  # if its YBCG
                track_to_divert = 289
                dist_to_alt = 366
                track_diff = 52
                tas = 211
                fuel_flow = 1025
            # WIND COMPONENT TO DIVERT TO ALTERNATE
            divert_offset = abs(wind_direction - track_to_divert)
            divert_rads = radians(divert_offset)
            wind_to_divert = round(-(cos(divert_rads) * windspeed))

            wind_divert = int(wind_to_divert)
            wind_cont = int(wind_to_continue)

            holding_mins = self.root.ids['home_screen'].ids['holding_mins'].text
            fuel_onboard = self.root.ids['home_screen'].ids['fuel_onboard'].text
            dist_from_syd = self.root.ids['home_screen'].ids['dist_from_syd'].text

            fuel_adj = ((float(dist_from_syd) / (212 + wind_cont)) * 1086) - 190
            fixed_res = 500
            holding_fuel = round(int(holding_mins) * 14.1666667)
            safe_fuel = int(fuel_onboard) - fixed_res - holding_fuel
            ref_fuel = round(((safe_fuel + fuel_adj) / 1000), 2)

            if wind_divert == wind_cont:
                psd = ((ref_fuel * 1000) ** 2 - dist_to_alt ** 2 * (fuel_flow / (tas + wind_divert)) ** 2) / (
                        2 * (ref_fuel * 1000 * (fuel_flow / (tas + wind_cont)) - dist_to_alt * (
                            fuel_flow / (tas + wind_divert)
                            ) ** 2 * cos(track_diff / 57.3)))
            else:
                psd = (sqrt(
                    (2 * (ref_fuel * 1000 * (fuel_flow / (tas + wind_cont)) - dist_to_alt * (fuel_flow / (tas + wind_divert)
                                                                                             ) ** 2 * cos(track_diff / 57.3)
                          )) ** 2 - 4 * ((fuel_flow / (tas + wind_divert)) ** 2 - (fuel_flow / (tas + wind_cont)) ** 2) * (
                            dist_to_alt ** 2 * (fuel_flow / (tas + wind_divert)) ** 2 - (ref_fuel * 1000) ** 2)) - 2 * (
                               ref_fuel * 1000 * (fuel_flow / (tas + wind_cont)) - dist_to_alt * (fuel_flow /
                                                                                                  (
                                                                                                              tas + wind_divert)) ** 2 * cos(
                           track_diff / 57.3))) / 2 / (
                                  (fuel_flow / (tas + wind_divert)) ** 2 - (fuel_flow / (tas + wind_cont)
                                                                            ) ** 2)
            result = self.root.ids['home_screen'].ids['result']
            result.text = 'The point of safe diversion is ' + str(round(psd)) + 'nm from SYD'
        except:
            result = self.root.ids['home_screen'].ids['result']
            result.text = 'INCORRECT ENTRY'


MainApp().run()
