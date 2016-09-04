CC2510Lib
=====

this is a fork of the CC2510Lib (https://github.com/fishpepper/CC2510Lib)
that is a fork of the CCLib (https://github.com/wavesoft/CCLib)

STATUS: Flash read/write confirmed working on raspberry pi V2.

working:
- connecting
- cc_info.py
- erase chip
- write & verify flash using cc_write_flash.py (tested with hex from sdcc)

fishpepper ported it to support programming of a cc2510f16 chip. adding cc251x support is trivial, see ccdebugger.py and chip id code.
I then ported it from Arduino to raspbian/raspberry, as i did not manage to get the arduino code or the voltage dividers work correctly.
Using the raspberry the voltage levels are just right, and nothing other then the wires are needed.
Also this managed to increase flash speed a lot :)

Just also wanna thank fishpepper for his work, i'm surely admire your work!

Wiring
------

    3.3V VCC     = Pin 1
    DBG DATA     = Pin 11
    DBG CLOCK    = Pin 7
    GND          = Pin 6
    RESET        = Pin 13

Usage
-----

1. Install WiringPi-Python described at https://github.com/WiringPi/WiringPi-Python
2. Connect all 5 wires as described above.
3. Use the python scripts from the Python/ directory to read/flash your chip.


Disclaimer
----------

i sucessfully flashed a cc2510f16 chip with the scripts provided with this project, however I DO NOT GURANTEE THAT THIS WILL WORK IN YOUR CASE. **YOU ARE USING THIS CODE SOLELY AT YOUR OWN RISK!**

License
-------

Copyright (c) 2016 Jimmy Wennlund - github.com/jimmyw
Copyright (c) 2015 Simon Schulz - github.com/fishpepper

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

