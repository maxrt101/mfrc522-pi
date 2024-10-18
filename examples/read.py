#!/usr/bin/env python3

from mfrc522pi import *
import traceback

BLOCK = 8


def main():
    reader = MFRC522(reset=22)

    print('MFRC522 reader example')
    print('Press ^C to stop')

    try:
        while True:
            res = reader.request(PICC.REQIDL)

            if res.status != Status.OK:
                continue

            print('\nDetected a card')

            res = reader.anti_collision()

            if res.status != Status.OK:
                print(f'AntiCollision error: {res.status}')
                continue

            print(f'UID: {" ".join([f"0x{x:02X}" for x in res.uid])}')

            key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

            status = reader.select_tag(res.uid)

            if status != Status.OK:
                print(f'Selection error: {res.status}')
                continue

            status = reader.authenticate(PICC.AUTHENT1A, 8, key, res.uid)

            if status != Status.OK:
                print(f'Authentication error: {res.status}')
                continue

            print(f'Reading block {BLOCK}')
            res = reader.read_block(BLOCK)
            reader.stop_crypto1()
            if res.status == Status.OK:
                print(' '.join(f'0x{x:02X}' for x in res.data))
            else:
                print(f'Error reading block {BLOCK}: {res.status}')
    except KeyboardInterrupt:
        print('Exiting...')
    except Exception as e:
        print(traceback.format_exc())
    finally:
        reader.cleanup()


if __name__ == '__main__':
    main()
