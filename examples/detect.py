#!/usr/bin/env python3
# Example for debug. Help to see what is read from the module

from mfrc522pi import *
import time
import sys


def main():
    reader = MFRC522(reset=22)

    timeout = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5

    print(f'MFRC522 detect example (timeout={timeout})')
    print('Press ^C to stop')

    try:
        while True:
            reader.write(REG.BitFraming, 7)
            res = reader.transceive(PCD.TRANSCEIVE, [PICC.REQIDL])
            print(f'STATUS={res.status} DATA={res.data} SIZE={res.size}')
            time.sleep(timeout)

    except KeyboardInterrupt:
        reader.cleanup()
        print('Exiting...')


if __name__ == '__main__':
    main()
