#!/usr/bin/env python3
# Main class that works with RC522 using SPI

from mfrc522pi.logger import logger
from mfrc522pi.result import *
from mfrc522pi.status import *
from mfrc522pi.data import *
from mfrc522pi.abi import *
import RPi.GPIO as GPIO
import spi


class MFRC522:
    MAX_LEN = 16

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
        tmp = self.read(REG.TxControl)
        if ~(tmp & 0x03):
            self.set_bit_mask(REG.TxControl, 0x03)

    def antenna_off(self):
        self.clear_bit_mask(REG.TxControl, 0x03)

    def version(self) -> int:
        return self.read(REG.Version)

    def reset(self):
        self.write(REG.Command, PCD.RESETPHASE)

    def init(self):
        GPIO.output(self.reset_pin, 1)

        self.reset()

        self.write(REG.TMode, 0x8D)
        self.write(REG.TPrescaler, 0x3E)
        self.write(REG.TReloadL, 30)
        self.write(REG.TReloadH, 0)

        self.write(REG.TxAuto, 0x40)
        self.write(REG.Mode, 0x3D)

        self.antenna_on()

    def cleanup(self):
        self.stop_crypto1()
        spi.closeSPI(self.spi)
        GPIO.cleanup()

    def transceive(self, command: int, data) -> Result[TransceiveResult]:
        buffer = []
        buffer_size = 0
        status = Status.TRANSCEIVE_ERROR

        if command == PCD.AUTHENT:
            irq_enable = 0x12
            wait_irq = 0x10
        elif command == PCD.TRANSCEIVE:
            irq_enable = 0x77
            wait_irq = 0x30
        else:
            irq_enable = 0
            wait_irq = 0

        self.write(REG.CommIEn, irq_enable | 0x80)
        self.clear_bit_mask(REG.CommIrq, 0x80)
        self.set_bit_mask(REG.FIFOLevel, 0x80)

        self.write(REG.Command, PCD.IDLE)

        for b in data:
            self.write(REG.FIFOData, b)

        self.write(REG.Command, command)

        if command == PCD.TRANSCEIVE:
            self.set_bit_mask(REG.BitFraming, 0x80)

        i = 2000
        while True:
            n = self.read(REG.CommIrq)
            i -= 1
            # FIXME: WTF
            if ~((i != 0) and ~(n & 1) and ~(n & wait_irq)):
                break

        self.clear_bit_mask(REG.BitFraming, 0x80)

        if i != 0 and (self.read(REG.Error) & 0x1B) == 0:
            status = Status.OK

            # FIXME: WTF
            if n & irq_enable & 1:
                status = Status.NO_TAG_ERROR

            if command == PCD.TRANSCEIVE:
                n = self.read(REG.FIFOLevel)
                last_bits = self.read(REG.Control) & 7

                buffer_size = (n-1) * 8 + last_bits if last_bits != 0 else n * 8

                n = 1 if n == 0 else n
                n = self.MAX_LEN if n > self.MAX_LEN else n

                for _ in range(n):
                    buffer.append(self.read(REG.FIFOData))

        return Result(status, TransceiveResult(buffer, buffer_size))

    def request(self, reg_mode: int) -> Result[RequestResult]:
        tag_type = [reg_mode]

        self.write(REG.BitFraming, 7)

        res = self.transceive(PCD.TRANSCEIVE, tag_type)

        if res.size != 0x10:
           res.status = Status.REQUEST_BAD_SIZE_ERROR

        return Result(res.status, RequestResult(res.size))

    def anti_collision(self) -> Result[AntiCollisionResult]:
        self.write(REG.BitFraming, 0)

        serial = [PICC.ANTICOLL, 0x20]

        res = self.transceive(PCD.TRANSCEIVE, serial)

        if res.status == Status.OK:
            if len(res.data) == 5:
                serial_check = 0
                for x in res.data[:4]:
                    serial_check ^= x
                if serial_check != res.data[4]:
                    res.status = Status.BAD_CRC_ERROR
            else:
                res.status = Status.ANTI_COLLISION_BAD_UID_SIZE_ERROR

        return Result(res.status, AntiCollisionResult(res.data))

    def calculate_crc(self, data: list[int]):
        self.clear_bit_mask(REG.DivIrq, 4)
        self.set_bit_mask(REG.FIFOLevel, 0x80)

        for b in data:
            self.write(REG.FIFOData, b)

        self.write(REG.Command, PCD.CALCCRC)

        i = 0xFF
        while True:
            n = self.read(REG.DivIrq)
            i -= 1
            if not (i and not (n & 4)):
                break

        return [
            self.read(REG.CRCResultL),
            self.read(REG.CRCResultM)
        ]

    def select_tag(self, serial: list[int]) -> Result[SelectTagResult]:
        buffer = [PICC.SElECTTAG, 0x70]

        for i in range(5):
            buffer.append(serial[i])

        buffer.extend(self.calculate_crc(buffer))

        res = self.transceive(PCD.TRANSCEIVE, buffer)

        if res.status == Status.OK and res.size != 0x18:
            res.status = Status.SELECT_TAG_BAD_SIZE_ERROR
        else:
            logger.debug(f'select_tag: size={res.data[0]}')

        return Result(res.status, SelectTagResult(res.data[0]))

    def authenticate(self, mode: int, addr: int, key: list[int], serial: list[int]) -> Status:
        buffer = [mode, addr]
        buffer.extend(key)
        buffer.extend(serial[:4])

        res = self.transceive(PCD.AUTHENT, buffer)

        if res.status != Status.OK:
            logger.error(f'authenticate: error {res.status.name}')

        # FIXME: WTF
        if self.read(REG.Status2) & 8 == 0:
            logger.error('authenticate: error status2 & 8 == 0')

        return res.status

    def stop_crypto1(self):
        self.clear_bit_mask(REG.Status2, 8)

    def read_block(self, addr: int) -> Result[BlockData]:
        data = [PICC.READ, addr]
        data.extend(self.calculate_crc(data))
        res = self.transceive(PCD.TRANSCEIVE, data)
        if res.status != Status.OK:
            logger.error('read_block: read error')
        else:
            if len(res.data) == 16:
                logger.debug(f'Sector {addr}: {res.data}')
        return Result(res.status, BlockData(addr, res.data))

    def write_block(self, addr: int, data: list[int]) -> Status:
        if len(data) != 16:
            logger.error('write_block: len(data) != 16')
            return Status.WRITE_BLOCK_BAD_SIZE_ERROR

        buffer = [PICC.WRITE, addr]
        buffer.extend(self.calculate_crc(buffer))
        res = self.transceive(PCD.TRANSCEIVE, buffer)

        if res.status != Status.OK:
            return res.status

        if res.size != 4 or res.data[0] & 0xF != 0xA:
            return Status.WRITE_BLOCK_BAD_DATA_ERROR
        
        buffer = []
        buffer.extend(data)
        buffer.extend(self.calculate_crc(buffer))
        
        res = self.transceive(PCD.TRANSCEIVE, buffer)

        if res.status != Status.OK:
            return res.status

        if res.size != 4 or res.data[0] & 0xF != 0xA:
            return Status.WRITE_BLOCK_BAD_DATA_ERROR
        
        return Status.OK

    def read_blocks(self, key: list[int], uid: list[int], block_count: int) -> Result[BlocksData]:
        buffer = dict()
        for i in range(block_count):
            status = self.authenticate(PICC.AUTHENT1A, i, key, uid)
            if status == Status.OK:
                block = self.read_block(i)
                if block.status != Status.OK:
                    return Result(block.status, BlocksData(buffer))
                buffer[i] = block.data
            else:
                return Result(status, BlocksData(buffer))

        return Result(Status.OK, BlocksData(buffer))

    def write_blocks(self, data: BlocksData) -> Status:
        for block_id, block_data in data.data.items():
            status = self.write_block(block_id, block_data)
            if status != Status.OK:
                return status
        return Status.OK
