import requests as r

from datetime import datetime
from datetime import timezone

from . import lumix_parameters

import logging

logger = logging.getLogger(__name__)

class CameraControl:

    def __init__(self, cam_ip):
        self.cam_ip = cam_ip
        self.baseurl = "http://{ip}/cam.cgi".format(ip=self.cam_ip)
        self.start_camera_control()

    def start_camera_control(self):
        resp = r.get(self.baseurl, params = {"mode": "camcmd", "value": "recmode"})
        if self.check_response(resp):
            logger.debug('Connected to camera {}'.format(self.cam_ip))

    def start_stream(self, upd_port):
        resp = r.get(self.baseurl, params = {"mode": "startstream", "value": str(upd_port)})
        if self.check_response(resp):
            return True

    def stop_stream(self):
        resp = r.get(self.baseurl, params = {"mode": "stopstream"})
        if self.check_response(resp):
            return True

    def get_info(self, setting):
        params = {"mode": "getinfo", "type": setting}
        resp = r.get(self.baseurl, params = params )
        return resp

    def current_menu_info(self):
        resp = self.get_info("curmenu")
        return resp

    def all_menu_info(self):
        resp = self.get_info("allmenu")
        return resp

    def get_lens_info(self):
        # ?, max_fstop, min_fstop, max_shutter, min_shutter, ?, ?, max_zoom, min_zoom, ?, ?, ?
        resp = self.get_info("lens")
        return resp

    def get_setting(self, setting):
        params = {"mode": "getsetting", "type": setting}
        resp = r.get(self.baseurl, params = params )
        return resp

    def get_focus_mode(self):
        resp = self.get_setting("focusmode")
        return resp

    def get_focus_mag(self):
        resp = self.get_setting("mf_asst_mag")
        return resp

    def get_mf_asst_setting(self):
        resp = self.get_setting("mf_asst")
        return resp

    def set_setting(self, settings):
        params = {"mode": "setsetting"}
        params.update(settings)
        resp = r.get(self.baseurl, params = params )
        return resp

    def set_iso(self, ISO):
        if ISO == "auto":
            ISO = "50"
        resp = self.set_setting({"type": "iso", "value": ISO})
        if self.check_response(resp):
            logger.debug ('ISO set to {}'.format(ISO))

    def set_focal(self, focal):
        resp = self.set_setting({"type": "focal", "value": lumix_parameters.fstop[focal] })
        if self.check_response(resp):
            logger.debug('f stop set to {}'.format(focal))

    def set_shutter(self, shutter):
        resp = self.set_setting({"type": "shtrspeed", "value": lumix_parameter.shutter_speed[shutter] })
        if self.check_response(resp):
            logger.debug('shutter set to {}'.format(shutter))

    def set_video_quality(self, quality="mp4ed_30p_100mbps_4k"):
        # mp4_24p_100mbps_4k / mp4_30p_100mbps_4k
        resp = self.set_setting({"type": "videoquality", "value": quality})
        if self.check_response(resp):
            logger.debug('video quality set to {]'.format(quality))
        return resp

    def focus_control(self, direction="tele", speed="normal"):
        #tele or wide for direction, normal or fast for speed
        params = {"mode": "camctrl", "type": "focus", "value": "{0}-{1}".format(direction, speed)}
        resp = r.get(self.baseurl, params = params )
        return resp

    def rack_focus(self, start_point="current", end_point="0", speed="normal"):
        #tele or wide for direction, normal or fast for speed
        
        #Check where we are with a fine step
        resp = self.focus_control("tele", "normal").text
        current_position = int(resp.split(',')[1])
        
        if end_point == "current":
            end_point = current_position + 13

        # First get to the starting point if necessary
        if start_point == "current":
            start_point = current_position + 13
        elif int(start_point) < current_position:
            while current_position - int(start_point) > 13:
                resp = self.focus_control("tele", "fast").text
                current_position = int(resp.split(',')[1])
        else:
            while int(start_point) - current_position > 13:
                resp = self.focus_control("wide", "fast").text
                current_position = int(resp.split(',')[1])

        #At the start, now let's get to the end point
        start_point = int(start_point)

        threshold = 13
        if speed == "fast":
            threshold = 70

        if start_point > int(end_point):
            while current_position - int(end_point) > threshold:
                resp = self.focus_control("tele", speed).text
                current_position = int(resp.split(',')[1])
                if current_position - int(end_point) <= threshold:
                    #Fine focus for the last bit
                    threshold = 13
                    speed = "normal"
        else:
            while int(end_point) - current_position > threshold:
                resp = self.focus_control("wide", speed).text
                current_position = int(resp.split(',')[1])
                if int(end_point) - current_position <= threshold:
                    threshold = 13
                    speed = "normal"

    def capture_photo(self):
        params = {"mode": "camcmd", "value": "capture"}
        resp = r.get(self.baseurl, params = params)
        return resp

    def video_record_start(self):
        params = {"mode": "camcmd", "value": "video_recstart"}
        resp = r.get(self.baseurl, params = params)
        return resp

    def video_record_stop(self):
        params = {"mode": "camcmd", "value": "video_recstop"}
        resp = r.get(self.baseurl, params = params)
        return resp

    def check_response(self, resp):
        # Get a 200 response even on error. Have to check <result>
        if "<result>ok</result>" in resp.text:
            return True
        else:
            logger.error('Response is {}'.format(resp.text))
            return False

    def set_date(self, new_date=None):
        if new_date is None:
            new_date = datetime.now(tz=timezone.utc).astimezone()
        value = new_date.strftime('%Y%m%d%H%M%S%z')
        params = {"mode": "setsetting", "type": "clock", "value": value}
        resp = r.get(self.baseurl, params = params)
        return resp

    def get_state(self):
        params = {"mode": "getstate"}
        resp = r.get(self.baseurl, params = params)
        return resp


if __name__ == "__main__":
    IP = "10.0.1.105"
    control = CameraControl(IP) #IP of camera
