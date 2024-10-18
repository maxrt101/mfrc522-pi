#!/usr/bin/env python3

from mfrc522pi import MFRC522
import time
import sys


def main():
    reader = MFRC522(reset=22)

    timeout = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5

    print(f'MFRC522 detect example (timeout={timeout})')
    print('Press ^C to stop')

    try:
        while True:
            reader.write(reader.REG.BitFraming, 7)
            res = reader.transceive(reader.PCD.TRANSCEIVE, [reader.PICC.REQIDL])
            print(res)
            time.sleep(timeout)

    except KeyboardInterrupt:
        reader.cleanup()
        print('Exiting...')


if __name__ == '__main__':
    main()
