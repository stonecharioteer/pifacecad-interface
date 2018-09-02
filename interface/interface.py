"""
interface
"""
import logging
import datetime, time
import subprocess
import pifacecad
import sqlsoup
import expiringdict
from apscheduler.schedulers.background import BackgroundScheduler

class Interface:
    """Interface class definition

    This class defines the controller for the PiFaceCAD
    interface.

    It implements simple things, such as being able to turn pages,
    being able to change things in the currently shown page.
    """
    def __init__(self, *args, **kwargs):
        """Intitializer function"""
        logging.debug("Initializing the interface.")
        self.cad = pifacecad.PiFaceCAD()
        self.current_page = 1
        self.pages = {
                1: self.show_time,
                2: self.show_stats,
                3: self.show_ip
                }
        logging.debug("Polling for inputs!")
        self.last_page = self.current_page
        # five minute cache
        self.cached_dict = expiringdict.ExpiringDict(
                                    max_len=100,
                                    max_age_seconds=300)

        self.listener = pifacecad.SwitchEventListener(chip=self.cad)
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.scheduler.add_job(
                self.update,
                "interval",
                seconds=10,
                id="update_job")
        for i in range(6):
            self.listener.register(i,
                    pifacecad.IODIR_FALLING_EDGE,
                    logging.debug)

        self.listener.register(6,
                pifacecad.IODIR_FALLING_EDGE,
                self.page_left)
        self.listener.register(7,
                pifacecad.IODIR_FALLING_EDGE,
                self.page_right)
        self.update()
        logging.debug("Activating the listener.")
        self.listener.activate()

    def run_cmd(self, cmd):
        return subprocess.check_output(cmd, shell=True).decode("utf-8")

    def poll(self):
        """Constantly polls for input and shows
        the corresponding page
        """
        while True:
            time.sleep(0.15)
            switch_value = self.cad.switch_port.value
            logging.debug("Input: {}".format(switch_value))
            self.react(switch_value)

    def react(self, switch_value):
        """Reacts to the corresponding page."""
        if switch_value == 64:
            self.page_left()
        elif switch_value == 128:
            self.page_right()
        elif switch_value != 0:
            self.page_react(switch_value)
        else:
            self.show_page(self.current_page)

    def page_left(self, *args):
        logging.debug("Turning page left!")
        if self.current_page == 1:
            self.current_page = len(self.pages.keys())
        else:
            self.current_page -= 1
        self.show_page(self.current_page)

    def page_right(self, *args):
        logging.debug("Turning page right!")
        if self.current_page == len(self.pages.keys()):
            self.current_page = 1
        else:
            self.current_page += 1
        self.show_page(self.current_page)

    def show_page(self, page_number):
        logging.debug("Showing page number: {}".format(page_number))

        if self.last_page != page_number:
            self.cad.lcd.clear()
            self.last_page = self.current_page
        self.pages[page_number]()

    def show_time(self):
        logging.debug("Showing time")
        self.cad.lcd.write(datetime.datetime.now().strftime(
            "%a, %-d %b %Y\n%H:%M"))
        self.cad.lcd.home()

    def show_ip(self):
        logging.debug("Showing IP")
        ip = self.cached_dict.get("ip")
        if ip is None:
            ips = self.run_cmd("hostname --all-ip-addresses")
            self.cached_dict["ip"] = ips[:-1]
            self.cached_dict["ip_update_time"] = datetime.datetime.now()

        self.cad.lcd.write("IP: {}\n{}s ago.".format(
            self.cached_dict["ip"],
            (datetime.datetime.now() - self.cached_dict["ip_update_time"]
            ).seconds))
        self.cad.lcd.home()

    def show_stats(self):
        logging.debug("Showing stats")
        self.cad.lcd.write("Stats here")
        self.cad.lcd.home()

    def page_react(self, inp):
        logging.debug(
                "Reacting on page {} with input: {}".format(
                    self.current_page, inp))

    def update(self, *args):
        self.cad.lcd.blink_off()
        self.cad.lcd.cursor_off()
        self.cad.lcd.home()
        now = datetime.datetime.now()
        if 6 <= now.hour <= 23:
            self.cad.lcd.backlight_on()
        else:
            self.cad.lcd.backlight_off()
        self.show_page(self.current_page)

