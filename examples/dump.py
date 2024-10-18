#!/usr/bin/env python3

from mfrc522pi import MFRC522


def main():
    reader = MFRC522(reset=22)

    print('MFRC522 dump example')
    print('Press ^C to stop')

    try:
        while True:
            res = reader.request(reader.PICC.REQIDL)

            if res.status == reader.MI.OK:
                print('\nDetected a card')

            res = reader.anti_collision()

            if res.status == reader.MI.OK:
                print(f'UID: {" ".join([hex(x) for x in res.uid])}')

                key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                reader.select_tag(res.uid)

                print('Dumping card:')
                data = reader.dump_1k(key, res.uid)
                reader.stop_crypto1()

                for sector_id, sector_data in data:
                    print(f'{sector_id}: {" ".join([hex(x) for x in sector_data])}')
    except KeyboardInterrupt:
        reader.cleanup()
        print('Exiting...')


if __name__ == '__main__':
    main()
