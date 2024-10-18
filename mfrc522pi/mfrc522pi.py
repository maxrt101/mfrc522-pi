##!/usr/bin/env python3

from dataclasses import dataclass
from  mfrc522pi.logger import logger
import RPi.GPIO as GPIO
import spi

class MFRC522:
    MAX_LEN = 16

    class PCD:
        IDLE       = 0x00
        AUTHENT    = 0x0E
        RECEIVE    = 0x08
        TRANSMIT   = 0x04
        TRANSCEIVE = 0x0C
        RESETPHASE = 0x0F
        CALCCRC    = 0x03

    class PICC:
        REQIDL    = 0x26
        REQALL    = 0x52
        ANTICOLL  = 0x93
        SElECTTAG = 0x93
        AUTHENT1A = 0x60
        AUTHENT1B = 0x61
        READ      = 0x30
        WRITE     = 0xA0
        DECREMENT = 0xC0
        INCREMENT = 0xC1
        RESTORE   = 0xC2
        TRANSFER  = 0xB0
        HALT      = 0x50

    class MI:
        OK       = 0
        NOTAGERR = 1
        ERR      = 2

    class REG:
        Reserved00     = 0x00
        Command        = 0x01
        CommIEn        = 0x02
        DivlEn         = 0x03
        CommIrq        = 0x04
        DivIrq         = 0x05
        Error          = 0x06
        Status1        = 0x07
        Status2        = 0x08
        FIFOData       = 0x09
        FIFOLevel      = 0x0A
        WaterLevel     = 0x0B
        Control        = 0x0C
        BitFraming     = 0x0D
        Coll           = 0x0E
        Reserved01     = 0x0F

        Reserved10     = 0x10
        Mode           = 0x11
        TxMode         = 0x12
        RxMode         = 0x13
        TxControl      = 0x14
        TxAuto         = 0x15
        TxSel          = 0x16
        RxSel          = 0x17
        RxThreshold    = 0x18
        Demod          = 0x19
        Reserved11     = 0x1A
        Reserved12     = 0x1B
        Mifare         = 0x1C
        Reserved13     = 0x1D
        Reserved14     = 0x1E
        SerialSpeed    = 0x1F

        Reserved20     = 0x20
        CRCResultM     = 0x21
        CRCResultL     = 0x22
        Reserved21     = 0x23
        ModWidth       = 0x24
        Reserved22     = 0x25
        RFCfg          = 0x26
        GsN            = 0x27
        CWGsP          = 0x28
        ModGsP         = 0x29
        TMode          = 0x2A
        TPrescaler     = 0x2B
        TReloadH       = 0x2C
        TReloadL       = 0x2D
        TCounterValueH = 0x2E
        TCounterValueL = 0x2F

        Reserved30     = 0x30
        TestSel1       = 0x31
        TestSel2       = 0x32
        TestPinEn      = 0x33
        TestPinValue   = 0x34
        TestBus        = 0x35
        AutoTest       = 0x36
        Version        = 0x37
        AnalogTest     = 0x38
        TestDAC1       = 0x39
        TestDAC2       = 0x3A
        TestADC        = 0x3B
        Reserved31     = 0x3C
        Reserved32     = 0x3D
        Reserved33     = 0x3E
        Reserved34     = 0x3F

    @dataclass
    class TransceiveResult:
        status: int
        data: list[int]
        size: int

    @dataclass
    class RequestResult:
        status: int
        size: int

    @dataclass
    class AntiCollisionResult:
        status: int
        uid: list[int]

    def __init__(self, dev: str = '/dev/spidev0.0', speed: int = 1000000, reset: int = 22):
        self.spi = spi.openSPI(device=dev, mode=0, speed=speed)
        self.reset_pin = reset

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.reset_pin, GPIO.OUT)
        GPIO.output(self.reset_pin, 1)

        self.init()

    def write(self, addr: int, value: int):
        spi.transfer(self.spi, ((addr << 1) & 0x7E, value))

    def read(self, addr: int) -> int:
        result = spi.transfer(self.spi, (((addr << 1) & 0x7E) | 0x80, 0))
        return result[1]

    def set_bit_mask(self, reg: int, mask: int):
        tmp = self.read(reg)
        self.write(reg, tmp | mask)

    def clear_bit_mask(self, reg: int, mask: int):
        tmp = self.read(reg)
        self.write(reg, tmp & (~mask))

    def antenna_on(self):
        tmp = self.read(self.REG.TxControl)
        if ~(tmp & 0x03):
            self.set_bit_mask(self.REG.TxControl, 0x03)

    def antenna_off(self):
        self.clear_bit_mask(self.REG.TxControl, 0x03)

    def version(self) -> int:
        return self.read(self.REG.Version)

    def reset(self):
        self.write(self.REG.Command, self.PCD.RESETPHASE)

    def init(self):
        GPIO.output(self.reset_pin, 1)

        self.reset()

        self.write(self.REG.TMode, 0x8D)
        self.write(self.REG.TPrescaler, 0x3E)
        self.write(self.REG.TReloadL, 30)
        self.write(self.REG.TReloadH, 0)

        self.write(self.REG.TxAuto, 0x40)
        self.write(self.REG.Mode, 0x3D)

        self.antenna_on()

    def cleanup(self):
        GPIO.cleanup()

    def transceive(self, command: int, data) -> TransceiveResult:
        buffer = []
        buffer_size = 0
        status = self.MI.ERR

        if command == self.PCD.AUTHENT:
            irq_enable = 0x12
            wait_irq = 0x10
        elif command == self.PCD.TRANSCEIVE:
            irq_enable = 0x77
            wait_irq = 0x30
        else:
            irq_enable = 0
            wait_irq = 0

        self.write(self.REG.CommIEn, irq_enable | 0x80)
        self.clear_bit_mask(self.REG.CommIrq, 0x80)
        self.set_bit_mask(self.REG.FIFOLevel, 0x80)

        self.write(self.REG.Command, self.PCD.IDLE)

        for b in data:
            self.write(self.REG.FIFOData, b)

        self.write(self.REG.Command, command)

        if command == self.PCD.TRANSCEIVE:
            self.set_bit_mask(self.REG.BitFraming, 0x80)

        i = 2000
        while True:
            n = self.read(self.REG.CommIrq)
            i -= 1
            if ~((i != 0) and ~(n & 1) and ~(n & wait_irq)):
                break

        self.clear_bit_mask(self.REG.BitFraming, 0x80)

        if i != 0:
            if (self.read(self.REG.Error) & 0x1B) == 0:
                status = self.MI.OK

                if n & irq_enable & 1:
                    status = self.MI.NOTAGERR

                if command == self.PCD.TRANSCEIVE:
                    n = self.read(self.REG.FIFOLevel)
                    last_bits = self.read(self.REG.Control) & 7

                    buffer_size = (n-1) * 8 + last_bits if last_bits != 0 else n * 8

                    n = 1 if n == 0 else n
                    n = self.MAX_LEN if n > self.MAX_LEN else n

                    for _ in range(n):
                        buffer.append(self.read(self.REG.FIFOData))
            else:
                status = self.MI.ERR

        return self.TransceiveResult(status, buffer, buffer_size)

    def request(self, reg_mode: int) -> RequestResult:
        tag_type = [reg_mode]

        self.write(self.REG.BitFraming, 7)

        res = self.transceive(self.PCD.TRANSCEIVE, tag_type)

        if res.status != self.MI.OK or res.size != 0x10:
            res.status = self.MI.ERR

        return self.RequestResult(res.status, res.size)

    def anti_collision(self) -> AntiCollisionResult:
        self.write(self.REG.BitFraming, 0)

        serial = [self.PICC.ANTICOLL, 0x20]

        res = self.transceive(self.PCD.TRANSCEIVE, serial)

        if res.status == self.MI.OK:
            if len(res.data) == 5:
                serial_check = 0
                for x in res.data[:4]:
                    serial_check ^= x
                if serial_check != res.data[4]:
                    res.status = self.MI.ERR
            else:
                res.status = self.MI.ERR

        return self.AntiCollisionResult(res.status, res.data)

    def calculate_crc(self, data: list[int]):
        self.clear_bit_mask(self.REG.DivIrq, 4)
        self.set_bit_mask(self.REG.FIFOLevel, 0x80)

        for b in data:
            self.write(self.REG.FIFOData, b)

        self.write(self.REG.Command, self.PCD.CALCCRC)

        i = 0xFF
        while True:
            n = self.read(self.REG.DivIrq)
            i -= 1
            if not (i and not (n & 4)):
                break

        return [
            self.read(self.REG.CRCResultL),
            self.read(self.REG.CRCResultM)
        ]

    def select_tag(self, serial: list[int]):
        buffer = [self.PICC.SElECTTAG, 0x70]

        for i in range(5):
            buffer.append(serial[i])

        buffer.extend(self.calculate_crc(buffer))

        res = self.transceive(self.PCD.TRANSCEIVE, buffer)

        if res.status == self.MI.OK and res.size == 0x18:
            logger.debug(f'select_tag: size={res.data[0]}')
            return res.data[0]

        return 0

    def authenticate(self, mode: int, addr: int, key: list[int], serial: list[int]) -> int:
        buffer = [mode, addr]
        buffer.extend(key)
        buffer.extend(serial[:4])

        res = self.transceive(self.PCD.AUTHENT, buffer)

        if res.status != self.MI.OK:
            logger.error('authenticate: error')

        # WTF
        if self.read(self.REG.Status2) & 8 == 0:
            logger.error('authenticate: error status2 & 8 == 0')

        return res.status

    def stop_crypto1(self):
        self.clear_bit_mask(self.REG.Status2, 8)

    def read_block(self, addr: int) -> list[int]:
        data = [self.PICC.READ, addr]
        data.extend(self.calculate_crc(data))
        res = self.transceive(self.PCD.TRANSCEIVE, data)
        if res.status != self.MI.OK:
            logger.error('read_block: read error')
            return []
        if len(res.data) == 16:
            logger.debug(f'Sector {addr}: {res.data}')
        return res.data

    def write_block(self, addr: int, data: list[int]):
        if len(data) != 16:
            logger.error('write_block: len(data) != 16')
            return self.MI.ERR

        buffer = [self.PICC.WRITE, addr]
        buffer.extend(self.calculate_crc(buffer))
        res = self.transceive(self.PCD.TRANSCEIVE, buffer)

        if res.status != self.MI.OK or res.size != 4 or res.data[0] & 0xF != 0xA:
            return self.MI.ERR
        
        buffer = []
        buffer.extend(data)
        buffer.extend(self.calculate_crc(buffer))
        
        res = self.transceive(self.PCD.TRANSCEIVE, buffer)

        if res.status != self.MI.OK or res.size != 4 or res.data[0] & 0xF != 0xA:
            return self.MI.ERR
        
        return self.MI.OK
    
    def dump_1k(self, key, uid) -> dict[int, list[int]]:
        buffer = dict()
        for i in range(64):
            status = self.authenticate(self.PICC.AUTHENT1A, i, key, uid)
            if status == self.MI.OK:
                buffer[i] = self.read_block(i)
            else:
                logger.error('dump_1k: authentication error')

        return buffer
        
        
