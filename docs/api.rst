API
###

CharLCD (I²C)
=============

The main class for controlling I²C connected LCDs.

.. autoclass:: RPLCD.i2c.CharLCD

CharLCD (GPIO)
==============

The main class for controlling GPIO (parallel) connected LCDs.

.. autoclass:: RPLCD.gpio.CharLCD

CharLCD (lgpio)
===============

The main class for controlling GPIO (parallel) connected LCDs on Raspberry Pi 5
using the lgpio_ backend.

.. autoclass:: RPLCD.lgpio.CharLCD

CharLCD (pigpio)
================

The main class for controlling LCDs through pigpio_.

.. autoclass:: RPLCD.pigpio.CharLCD

.. _pigpio: http://abyz.me.uk/rpi/pigpio/
.. _lgpio: https://abyz.me.uk/lg/py_lgpio.html
