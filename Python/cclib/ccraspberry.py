import wiringpi
from wiringpi import GPIO


# Command constants
CMD_ENTER    =(0x01)
CMD_EXIT     =(0x02)
CMD_CHIP_ID  =(0x03)
CMD_STATUS   =(0x04)
CMD_PC       =(0x05)
CMD_STEP     =(0x06)
CMD_EXEC_1   =(0x07)
CMD_EXEC_2   =(0x08)
CMD_EXEC_3   =(0x09)
CMD_BRUSTWR  =(0x0A)
CMD_RD_CFG   =(0x0B)
CMD_WR_CFG   =(0x0C)
CMD_CHPERASE =(0x0D)
CMD_RESUME   =(0x0E)
CMD_HALT     =(0x0F)
CMD_PING     =(0xF0)

# Response constants
ANS_OK       =(0x01)
ANS_ERROR    =(0x02)
ANS_READY    =(0x03)

class CCDbg:
    pinDC = 7
    pinDD = 0
    pinRST = 2
    pinSEND = 3

    delay_time_us = 1
    def __init__(self):
        print "Hello from ccraspberry"
        wiringpi.wiringPiSetup()
	wiringpi.pinMode(self.pinDC,       GPIO.OUTPUT)
	wiringpi.pinMode(self.pinDD,       GPIO.OUTPUT)
	wiringpi.pinMode(self.pinRST,      GPIO.OUTPUT)
	wiringpi.pinMode(self.pinSEND,      GPIO.OUTPUT)
        wiringpi.digitalWrite(self.pinDC,  GPIO.LOW);
        wiringpi.digitalWrite(self.pinDD,  GPIO.LOW);
        wiringpi.digitalWrite(self.pinRST, GPIO.LOW);
        wiringpi.digitalWrite(self.pinSEND, GPIO.HIGH);

        self.enter()

    def enter(self):
        wiringpi.digitalWrite(self.pinRST, GPIO.LOW)
        wiringpi.delay(200)
        wiringpi.digitalWrite(self.pinDC,  GPIO.HIGH)
        wiringpi.delay(3)
        wiringpi.digitalWrite(self.pinDC,  GPIO.LOW)
        wiringpi.delay(3)
        wiringpi.digitalWrite(self.pinDC,  GPIO.HIGH)
        wiringpi.delay(3)
        wiringpi.digitalWrite(self.pinDC,  GPIO.LOW)
        wiringpi.delay(200)
        wiringpi.digitalWrite(self.pinRST, GPIO.HIGH)
        wiringpi.delay(200);

    def exit(self):
        self.write( 0x4C ) #0x48 ); // RESUME
        self.switchRead()
        bAns = self.read() # debug status
        self.switchWrite()
        return 0

    def getChipID(self):
        self.write( 0x68 ) # GET_CHIP_ID
        self.switchRead()
        bRes = self.read() # High order
        bAns = bRes << 8
        bRes = self.read() # Low order
        bAns |= bRes
        self.switchWrite()
        return bAns

    def getStatus(self):
        self.write( 0x34) # 0x30 ); // READ_STATUS
        self.switchRead()
        bAns = self.read() # debug status
        self.switchWrite()

        return bAns;

    def getConfig(self):
        self.write( 0x24) # 0x20 ); // RD_CONFIG
        self.switchRead()
        bAns = self.read() # Config
        self.switchWrite()
        return bAns

    def setConfig(self, config):
        self.write( 0x1D) #0x18 ); // WR_CONFIG
        self.write( config )
        self.switchRead()
        bAns = self.read() # Config
        self.switchWrite()
        return bAns

    def chipErase(self):
        self.write( 0x14) # //0x10 ); // CHIP_ERASE
        self.switchRead()
        bAns = self.read() # Debug status
        self.switchWrite()
        return bAns;

    def exec1(self, oc0):
        self.write( 0x55) #0x51 ); // DEBUG_INSTR + 3b
        self.write( oc0 )
        self.switchRead()
        bAns = self.read() # Accumulator
        self.switchWrite()
        return bAns

    def exec2(self, oc0, oc1):
        self.write( 0x56) #0x52 ); // DEBUG_INSTR + 3b
        self.write( oc0 )
        self.write( oc1 )
        self.switchRead()
        bAns = self.read() # Accumulator
        self.switchWrite()
        return bAns

    def exec3(self, oc0, oc1, oc2):
        self.write( 0x57) #0x53 ); // DEBUG_INSTR + 3b
        self.write( oc0 )
        self.write( oc1 )
        self.write( oc2 )
        self.switchRead()
        bAns = self.read() # Accumulator
        self.switchWrite()
        return bAns

    def getPC(self):
        self.write( 0x28) # 0x28 ); // GET_PC
        self.switchRead()
        bRes = self.read() # High order
        bAns = bRes << 8
        bRes = self.read() # Low order
        bAns |= bRes
        self.switchWrite()
        return bAns

    def resume(self):
        self.write( 0x4C) #RESUME
        self.switchRead()
        bAns = self.read() # Accumulator
        self.switchWrite()
        return bAns;

    def halt(self):
        self.write( 0x44) #HALT
        self.switchRead()
        bAns = self.read() # Accumulator
        self.switchWrite()
        return bAns

    def write(self, data):
        # Make sure DD is on output
	wiringpi.pinMode(self.pinDD, GPIO.OUTPUT)

        # Sent bytes
        for cnt in range(8):

            # First put data bit on bus
            if data & 0x80:
                wiringpi.digitalWrite(self.pinDD, GPIO.HIGH)
            else:
                wiringpi.digitalWrite(self.pinDD, GPIO.LOW)

            # Place clock on high (other end reads data)
            wiringpi.digitalWrite(self.pinDC, GPIO.HIGH)

            # Shift & Delay
            data = data << 1
            wiringpi.delayMicroseconds(self.delay_time_us)

            # Place clock down
            wiringpi.digitalWrite(self.pinDC, GPIO.LOW)
            wiringpi.delayMicroseconds(self.delay_time_us)
        return 0

    def switchWrite(self):
        wiringpi.digitalWrite(self.pinSEND, GPIO.HIGH)
	wiringpi.pinMode(self.pinDD, GPIO.OUTPUT)

    def switchRead(self):
        didWait = False

        # Switch to input
	wiringpi.pinMode(self.pinDD, GPIO.INPUT)
        wiringpi.digitalWrite(self.pinSEND, GPIO.LOW)

        # Wait at least 83 ns before checking state t(dir_change)
        # switchRead is always done after a rewrite, that already have a delay.
        #wiringpi.delay(2)

        # Wait for DD to go LOW (Chip is READY)
        while wiringpi.digitalRead(self.pinDD) == GPIO.HIGH:

            # Do 8 clock cycles
            for cnt in range(8):
              wiringpi.digitalWrite(self.pinDC, GPIO.HIGH)
              wiringpi.delayMicroseconds(self.delay_time_us)
              wiringpi.digitalWrite(self.pinDC, GPIO.LOW)
              wiringpi.delayMicroseconds(self.delay_time_us)

            # Let next function know that we did wait
            didWait = True

        # Wait t(sample_wait)
        if didWait:
            wiringpi.delayMicroseconds(self.delay_time_us)

        return 0

    def read(self):
        data = 0

        # Switch to input
	wiringpi.pinMode(self.pinDD, GPIO.INPUT)

        # Send 8 clock pulses if we are HIGH
        for cnt in range(8):
            wiringpi.digitalWrite(self.pinDC, GPIO.HIGH)
            wiringpi.delayMicroseconds(self.delay_time_us)

            # Shift and read
            data = data << 1;
            if wiringpi.digitalRead(self.pinDD) == GPIO.HIGH:
                data = data | 0x01
            wiringpi.digitalWrite(self.pinDC, GPIO.LOW)
            wiringpi.delayMicroseconds(self.delay_time_us)

        return data


class ccraspberry:
    buf = []
    name = "ccraspberry"
    dbg = CCDbg()
    iRead = 0

    def burst_write(self, inp):

        # When we have data, forward them to the debugger
        while self.iRead > 0 and len(inp) >= 1:
            inByte = ord(inp[0])
            inp = inp[1:]
            self.dbg.write(inByte)
            self.iRead = self.iRead - 1

        if self.iRead == 0:
            # Read debug status
            self.dbg.switchRead()
            bAns = self.dbg.read()
            self.dbg.switchWrite()

            # Handle response
            self.sendFrame( ANS_OK, bAns );

    def write(self, inp):
        inByte = ord(inp[0])
        c1 = ord(inp[1])
        c2 = ord(inp[2])
        c3 = ord(inp[3])

        if self.iRead > 0:
            self.burst_write(inp)
            return

        if inByte == CMD_ENTER:
            self.dbg.enter()
            self.sendFrame( ANS_OK );
        elif inByte == CMD_EXIT:
            self.dbg.exit()
            self.sendFrame( ANS_OK );
        elif inByte == CMD_CHIP_ID:
            s1 = self.dbg.getChipID()
            self.sendFrame( ANS_OK,
               s1 & 0xFF,       # LOW first
               (s1 >> 8) & 0xFF # HIGH second
              );
        elif inByte == CMD_STATUS:
            bAns = self.dbg.getStatus()
            self.sendFrame( ANS_OK, bAns )
        elif inByte == CMD_PC:
            s1 = self.dbg.getPC();
            self.sendFrame( ANS_OK,
                       s1 & 0xFF,       # LOW first
                       (s1 >> 8) & 0xFF # HIGH second
                      );
        elif inByte == CMD_STEP:
            bAns = self.dbg.step()
            self.sendFrame( ANS_OK, bAns )
        elif inByte == CMD_EXEC_1:
            bAns = self.dbg.exec1( c1 )
            self.sendFrame( ANS_OK, bAns )
        elif inByte == CMD_EXEC_2:
            bAns = self.dbg.exec2( c1, c2 )
            self.sendFrame( ANS_OK, bAns )
        elif inByte == CMD_EXEC_3:
            bAns = self.dbg.exec3( c1, c2, c3 )
            self.sendFrame( ANS_OK, bAns )
        elif inByte == CMD_BRUSTWR:
            # Calculate the size of the incoming brust
            iLen = (c1 << 8) | c2;

            # Validate length
            if iLen > 2048:
                self.sendFrame( ANS_ERROR, 3 )
                return

            # Confirm transfer
            self.sendFrame( ANS_READY );

            # Prepare for brust-write
            self.dbg.write( 0x80 | (c1 & 0x07) ) # High-order bits
            self.dbg.write( c2 ) # Low-order bits

            # Start serial loop
            self.iRead = iLen
        elif inByte == CMD_RD_CFG:
            bAns = self.dbg.getConfig()
            self.sendFrame( ANS_OK, bAns )
        elif inByte == CMD_WR_CFG:
            bAns = self.dbg.setConfig(c1)
            self.sendFrame( ANS_OK, bAns )
        elif inByte == CMD_CHPERASE:
            bAns = self.dbg.chipErase()
            self.sendFrame( ANS_OK, bAns )
        elif inByte == CMD_RESUME:
            bAns = self.dbg.resume();
            self.sendFrame( ANS_OK, bAns )
        elif inByte == CMD_HALT:
            bAns = self.dbg.halt()
            self.sendFrame( ANS_OK, bAns )
        elif inByte == CMD_PING:
            self.sendFrame(ANS_OK)
        else:
            self.sendFrame( ANS_ERROR, 0xFF )
        pass

    def flush(self):
        pass

    def read(self):
        b = self.buf[0]
        self.buf = self.buf[1:]
        return chr(b)

    def sendFrame(self, ans, b0=0, b1=0):
        self.buf = [ans, b1, b0]


