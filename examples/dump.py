#!/usr/bin/env python3
# Example on how to dump 1k of the card

from mfrc522pi import *
import traceback


def main():
    reader = MFRC522(reset=22)

    print('MFRC522 dump example')
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

            print('Dumping 1k:')
            res = reader.dump_1k(key, uid)
            reader.stop_crypto1()

            if res.status != Status.OK:
                print(f'Error dumping: {res.status.name}')
                continue

            for sector_id, sector_data in res.data.items():
                print(f'{sector_id:03}: {" ".join([f"0x{x:02X}" for x in sector_data])}')

    except KeyboardInterrupt:
        print('Exiting...')
    except Exception as e:
        print(traceback.format_exc())
    finally:
        reader.cleanup()


if __name__ == '__main__':
    main()
