# mfrc522pi utilities
from mfrc522pi.data import *
import struct


MAGIC = bytes('MFRC522PI_DUMP'.encode('utf-8'))


def save_dump_result(filename: str, data: DumpResult) -> Status:
    with open(filename, 'wb') as f:
        f.write(MAGIC)
        f.write(struct.pack('>I', len(data.data)))
        for sector_id, sector_data in data.data.items():
            f.write(struct.pack('>I', sector_id))
            for b in sector_data:
                f.write(struct.pack('B', b))

    return Status.OK


def load_dump_result(filename: str) -> DumpResult:
    result = DumpResult(Status.OK, dict())
    with open(filename, 'rb') as f:
        magic = f.read(len(MAGIC))
        if magic != MAGIC:
            result.status = Status.DATA_CORRUPTED_ERROR
            return result
        sectors_count = struct.unpack('>I', f.read(4))[0]
        for _ in range(sectors_count):
            sector_id = struct.unpack('>I', f.read(4))[0]
            sector_data = []
            for i in range(16):
                sector_data.append(struct.unpack('B', f.read(1))[0])
            result.data[sector_id] = sector_data
    return result

