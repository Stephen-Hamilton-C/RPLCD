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

import lgpio

from .lcd_gpio import BaseGPIOCharLCD


class CharLCD(BaseGPIOCharLCD): 
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
        Character LCD controller.

        All provided pin numbers must be in the BCM numbering scheme.

        You can save 1 pin by not using RW. Set ``pin_rw`` to ``None`` if you
        want this.

        :param pin_rs: Pin for register select (RS).
        :type pin_rs: int
        :param pin_rw: Pin for selecting read or write mode (R/W). Set this to
            ``None`` for read only mode.
        :type pin_rw: int
        :param pin_e: Pin to start data read or write (E).
        :type pin_e: int
        :param pins_data: List of data bus pins in 8 bit mode (DB0-DB7) or in 4
            bit mode (DB4-DB7) in ascending order.
        :type pins_data: list of int
        :param pin_backlight: Pin for controlling backlight on/off. Set this to
            ``None`` for no backlight control. Default: ``None``.
        :type pin_backlight: int
        :param backlight_mode: Set this to either ``active_high`` or ``active_low``
            to configure the operating control for the backlight. Has no effect if
            pin_backlight is ``None``. Default: ``active_low``
        :type backlight_mode: str
        :param backlight_enabled: Whether the backlight is enabled initially.
            Default: ``True``. Has no effect if pin_backlight is ``None``
        :type backlight_enabled: bool
        :param rows: Number of display rows (usually 1, 2 or 4). Default: ``4``.
        :type rows: int
        :param cols: Number of columns per row (usually 16 or 20). Default ``20``.
        :type cols: int
        :param dotsize: Some 1 line displays allow a font height of 10px.
            Allowed: ``8`` or ``10``. Default: ``8``.
        :type dotsize: int
        :param charmap: The character map used. Depends on your LCD. This must
            be either ``A00`` or ``A02`` or ``ST0B``. Default: ``A02``.
        :type charmap: str
        :param auto_linebreaks: Whether or not to automatically insert line
            breaks. Default: ``True``.
        :type auto_linebreaks: bool
        :param compat_mode: Whether to run additional checks to support older LCDs
            that may not run at the reference clock (or keep up with it).
        :type compat_mode: bool

        """
        super().__init__(
            pin_rs,
            pin_rw,
            pin_e,
            pins_data,
            pin_backlight,
            backlight_mode,
            backlight_enabled,
            cols,
            rows,
            dotsize,
            charmap,
            auto_linebreaks,
            compat_mode,
        )

    def _start_gpio(self):
        self.chip = lgpio.gpiochip_open(0)

    def _claim_output_pin(self, pin):
        lgpio.gpio_claim_output(self.chip, pin)

    def _write_pin(self, pin, value):
        lgpio.gpio_write(self.chip, pin, value)

    def _free_pins(self, pins):
        lgpio.gpio_free(self.chip, pins)