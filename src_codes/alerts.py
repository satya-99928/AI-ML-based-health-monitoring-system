from gpiozero import RGBLED
from gpiozero import Buzzer

from config import RED_LED
from config import GREEN_LED
from config import BLUE_LED
from config import BUZZER
from config import NORMAL
from config import ABNORMAL
from config import CRITICAL


class AlertSystem:

    def __init__(self):

        self.led = RGBLED(
            RED_LED,
            GREEN_LED,
            BLUE_LED
        )

        self.buzzer = Buzzer(BUZZER)

    def update(self, status):

        self.buzzer.off()

        if status == NORMAL:
            self.led.color = (0, 1, 0)

        elif status == ABNORMAL:
            self.led.color = (1, 1, 0)

        elif status == CRITICAL:
            self.led.color = (1, 0, 0)
            self.buzzer.on()

        else:
            self.led.off()

    def off(self):

        self.led.off()
        self.buzzer.off()