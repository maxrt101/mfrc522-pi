#!/usr/bin/env python3
# Example on how to detect and read card UID and write specific blocks

from mfrc522pi import *
import traceback

BLOCK = 8


def main():
    reader = MFRC522(reset=22)

    print('MFRC522 write example')
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

            print(f'Reading block {BLOCK}')
            res = reader.read_block(BLOCK)

            if res.status != Status.OK:
                print(f'Error reading block {BLOCK}: {res.status.name}')

            original_data = res.data

            print(' '.join(f'0x{x:02X}' for x in res.data))

            print(f'Writing 0xFF x 16 to block {BLOCK}')
            res = reader.write_block(BLOCK, [0xFF for _ in range(16)])

            if res != Status.OK:
                print(f'Error writing block {BLOCK}: {res.name}')

            print(f'Reading block {BLOCK} to confirm write success')
            res = reader.read_block(BLOCK)

            if res.status != Status.OK:
                print(f'Error reading block {BLOCK}: {res.status.name}')

            print(' '.join(f'0x{x:02X}' for x in res.data))

            print(f'Restoring original data of block {BLOCK}')
            res = reader.write_block(BLOCK, original_data)

            if res != Status.OK:
                print(f'Error writing block {BLOCK}: {res.name}')

            print(f'Reading block {BLOCK} to confirm write success')
            res = reader.read_block(BLOCK)

            if res.status != Status.OK:
                print(f'Error reading block {BLOCK}: {res.status.name}')

            print(' '.join(f'0x{x:02X}' for x in res.data))

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
