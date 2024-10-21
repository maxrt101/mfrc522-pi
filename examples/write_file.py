#!/usr/bin/env python3
# Example on how to detect and read card UID and write specific blocks

from mfrc522pi import *
import traceback
import sys

BLOCK = 8


def main():
    if len(sys.argv) != 2:
        exit(f'Usage: python3 {sys.argv[0]} FILENAME')

    data_from_file = load_blocks(sys.argv[1])

    reader = MFRC522(reset=22)

    print('MFRC522 write from file example')
    print('Press ^C to stop')

    try:
        while True:
            res = reader.request(PICC.REQIDL)

            if res.status != Status.OK:
                continue

            print('\nDetected a card')

            res = reader.anti_collision()

            if res.status != Status.OK:
                print(f'AntiCollision error: {res.status.name}')
                continue

            uid = res.uid

            print(f'UID: {" ".join([f"0x{x:02X}" for x in uid])}')

            key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

            res = reader.select_tag(res.uid)

            if res.status != Status.OK:
                print(f'Selection error: {res.status.name}')
                continue

            status = reader.authenticate(PICC.AUTHENT1A, 8, key, uid)

            if status != Status.OK:
                print(f'Authentication error: {status.name}')
                continue

            status = reader.write_blocks(data_from_file.value)

            if status != Status.OK:
                print(f'Write error: {status.name}')
                continue

            reader.stop_crypto1()
            break

    except KeyboardInterrupt:
        print('Exiting...')
    except Exception as e:
        print(traceback.format_exc())
    finally:
        reader.cleanup()


if __name__ == '__main__':
    main()
