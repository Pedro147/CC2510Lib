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

from cclib import CCDebugger, CCHEXFile
import sys
import time

def printHelp():
	"""
	Show help screen
	"""
	print "Usage: cc_write_flash.py <hex file> " #[[[<license key>] <bt address>] <hw version>]"
	print ""

# Wait for filename
if len(sys.argv) < 2:
	print "ERROR: Please specify a source hex filename!"
	printHelp()
	sys.exit(1)

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

# Parse the HEX file
hexFile = CCHEXFile( sys.argv[1] )
hexFile.load()

# Display sections & calculate max memory usage
maxMem = 0
#build flash image
flash_data = [0xFF] * dbg.flashSize 

print "Sections in %s:\n" % sys.argv[1]
print " Addr.    Size"
print "-------- -------------"
for mb in hexFile.memBlocks:
	
	# Calculate top position
	memTop = mb.addr + mb.size
	if memTop > maxMem:
		maxMem = memTop
	
	#add to flash image:
	for i in range(mb.size):
		dest = mb.addr + i
		data = mb.bytes[i]
		#make sure we have no overlapping writes:
		if (flash_data[dest] != 0xFF):
			print "ERROR: sections in hex file overlap ?!"
			sys.exit(4)
		else:
			#fine, store this byte
			flash_data[dest] = data
	
	# Print portion
	print " 0x%04x   %6i B " % (mb.addr, mb.size)
print ""

print "flash usage: %3.1f%% (%d bytes of %d)\n" % ((maxMem*100.0/dbg.flashSize),maxMem, dbg.flashSize)

# Check for oversize data
if maxMem > (dbg.flashSize):
	print "ERROR: Data too bit to fit in chip's memory!"
	sys.exit(4)

# Confirm
print "This is going to ERASE and REPROGRAM the chip. Are you sure? <y/N>: ", 
ans = sys.stdin.readline()[0:-1]
if (ans != "y") and (ans != "Y"):
	print "Aborted"
	sys.exit(2)


print "\nFlashing:"

try:
	print " - Chip erase..."
	dbg.chipErase()
	time.sleep(5)
	
	data = []
	for i in range(dbg.flashPageSize):
		data.append(i & 0xFF)

	print " - Flashing..."
	dbg.writeFlashPage(0x0000, data, True)
	
	print " - Reading..."
	for i in range(dbg.flashSize/dbg.flashPageSize):
		print "page[%d]" % (i),
		read = dbg.readFlashPage(i*dbg.flashPageSize)
		for x in read:
			print "%04X" % x,
		print "."
	
	
except Exception as e:
 	print "ERROR: %s" % str(e)
 	sys.exit(3)



## Flash memory
#dbg.pauseDMA(False)
#print " - Flashing %i memory blocks..." % len(hexFile.memBlocks)
#for mb in hexFile.memBlocks:

	## Flash memory block
	#print " -> 0x%04x : %i bytes " % (mb.addr, mb.size),
	#try:
		#dbg.writeCODE( mb.addr, mb.bytes, verify=True, showProgress=True )
	#except Exception as e:
		#print "ERROR: %s" % str(e)
		#sys.exit(3)

# Done
print "\nCompleted"
print ""
