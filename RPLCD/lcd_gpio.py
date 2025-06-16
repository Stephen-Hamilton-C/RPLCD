"""
Copyright (C) 2013-2023 Danilo Bargen

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

from collections import namedtuple

from . import common as c
from .lcd import BaseCharLCD

from time import perf_counter as now

# Duration to rate-limit calls to _send
COMPAT_MODE_WAIT_TIME = 0.001

PinConfig = namedtuple('PinConfig', 'rs rw e d0 d1 d2 d3 d4 d5 d6 d7 backlight')


class BaseGPIOCharLCD(BaseCharLCD):
    def __init__(
        self,
        pin_rs=None,
        pin_rw=None,
        pin_e=None,
        pins_data=None,
        pin_backlight=None,
        backlight_mode='active_low',
        backlight_enabled=True,
        cols=20,
        rows=4,
        dotsize=8,
        charmap='A02',
        auto_linebreaks=True,
        compat_mode=False,
    ):
        """
        Character LCD controller. Base class only, you should use a subclass.
        """

        # Configure compatibility mode
        self.compat_mode = compat_mode
        if compat_mode:
            self.last_send_event = now()

        # Set attributes
        if pin_rs is None:
            raise ValueError('pin_rs is not defined.')
        if pin_e is None:
            raise ValueError('pin_e is not defined.')

        if len(pins_data) == 4:  # 4 bit mode
            self.data_bus_mode = c.LCD_4BITMODE
            block1 = [None] * 4
        elif len(pins_data) == 8:  # 8 bit mode
            self.data_bus_mode = c.LCD_8BITMODE
            block1 = pins_data[:4]
        else:
            raise ValueError('There should be exactly 4 or 8 data pins.')
        block2 = pins_data[-4:]
        self.pins = PinConfig(
            rs=pin_rs,
            rw=pin_rw,
            e=pin_e,
            d0=block1[0],
            d1=block1[1],
            d2=block1[2],
            d3=block1[3],
            d4=block2[0],
            d5=block2[1],
            d6=block2[2],
            d7=block2[3],
            backlight=pin_backlight,
        )
        self.backlight_mode = backlight_mode

        # Call superclass
        super(BaseGPIOCharLCD, self).__init__(
            cols, rows, dotsize, charmap=charmap, auto_linebreaks=auto_linebreaks
        )

        # Set backlight status
        if pin_backlight is not None:
            self.backlight_enabled = backlight_enabled

    def _init_connection(self):
        # Setup GPIO
        self._start_gpio()
        for pin in list(filter(None, self.pins)):
            self._claim_output_pin(pin)
        if self.pins.backlight is not None:
            self._claim_output_pin(self.pins.backlight)

        # Initialization
        c.msleep(50)
        self._write_pin(self.pins.rs, 0)
        self._write_pin(self.pins.e, 0)
        if self.pins.rw is not None:
            self._write_pin(self.pins.rw, 0)

    def _close_connection(self):
        active_pins = [pin for pin in self.pins if pin is not None]
        self._free_pins(active_pins)

    # Properties

    def _get_backlight_enabled(self):
        # We could probably read the current GPIO output state via sysfs, but
        # for now let's just store the state in the class
        if self.pins.backlight is None:
            raise ValueError('You did not configure a GPIO pin for backlight control!')
        return bool(self._backlight_enabled)

    def _set_backlight_enabled(self, value):
        if self.pins.backlight is None:
            raise ValueError('You did not configure a GPIO pin for backlight control!')
        if not isinstance(value, bool):
            raise ValueError('backlight_enabled must be set to ``True`` or ``False``.')
        self._backlight_enabled = value
        self._write_pin(self.pins.backlight, value ^ (self.backlight_mode == 'active_low'))

    backlight_enabled = property(
        _get_backlight_enabled,
        _set_backlight_enabled,
        doc='Whether or not to turn on the backlight.',
    )

    # Low level commands

    def _send(self, value, mode):
        """Send the specified value to the display with automatic 4bit / 8bit
        selection. The rs_mode is either ``RS_DATA`` or ``RS_INSTRUCTION``."""
        # Wait, if compatibility mode is enabled
        if self.compat_mode:
            self._wait()

        # Choose instruction or data mode
        self._write_pin(self.pins.rs, mode)

        # If the RW pin is used, set it to low in order to write.
        if self.pins.rw is not None:
            self._write_pin(self.pins.rw, 0)

        # Write data out in chunks of 4 or 8 bit
        if self.data_bus_mode == c.LCD_8BITMODE:
            self._write8bits(value)
        else:
            self._write4bits(value >> 4)
            self._write4bits(value)

        # Record the time for the tail-end of the last send event
        if self.compat_mode:
            self.last_send_event = now()

    def _send_data(self, value):
        """Send data to the display."""
        self._send(value, c.RS_DATA)

    def _send_instruction(self, value):
        """Send instruction to the display."""
        self._send(value, c.RS_INSTRUCTION)

    def _write4bits(self, value):
        """Write 4 bits of data into the data bus."""
        for i in range(4):
            bit = (value >> i) & 0x01
            self._write_pin(self.pins[i + 7], bit)
        self._pulse_enable()

    def _write8bits(self, value):
        """Write 8 bits of data into the data bus."""
        for i in range(8):
            bit = (value >> i) & 0x01
            self._write_pin(self.pins[i + 3], bit)
        self._pulse_enable()

    def _pulse_enable(self):
        """Pulse the `enable` flag to process data."""
        self._write_pin(self.pins.e, 0)
        c.usleep(1)
        self._write_pin(self.pins.e, 1)
        c.usleep(1)
        self._write_pin(self.pins.e, 0)
        c.usleep(100)  # commands need > 37us to settle

    def _wait(self):
        """Rate limit the number of send events."""
        end = self.last_send_event + COMPAT_MODE_WAIT_TIME
        while now() < end:
            pass

    def _start_gpio(self):
        raise NotImplementedError('Inheriting class does not override required method')

    def _free_pins(self, pins):
        raise NotImplementedError('Inheriting class does not override required method')
    
    def _write_pin(self, pin, value):
        raise NotImplementedError('Inheriting class does not override required method')

    def _claim_output_pin(self, pin):
        raise NotImplementedError('Inheriting class does not override required method')
