#!/usr/bin/python
#
# CCLib_proxy Utilities
# Copyright (c) 2014 Ioannis Charalampidis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from cclib import CCDebugger, hexdump
import sys

# Open debugger
try:
	dbg = CCDebugger("/dev/ttyACM0")
except Exception as e:
	print "ERROR: %s" % str(e)
	sys.exit(1)

# Get info
print "\nChip information:"
print "      Chip ID : 0x%04x" % dbg.chipID
print "   Flash size : %i Kb" % dbg.chipInfo['flash']
print "    SRAM size : %i Kb" % dbg.chipInfo['sram']
if dbg.chipInfo['usb']:
	print "          USB : Yes"
else:
	print "          USB : No"
print ""
dbg.enter()
dbg.setPC(0x0000)
dbg.resume()

# Done
print ""
