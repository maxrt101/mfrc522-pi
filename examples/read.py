#!/usr/bin/env python3

from mfrc522pi import MFRC522


def main():
    reader = MFRC522(reset=22)

    print('MFRC522 reader example')
    print('Press ^C to stop')

    try:
        while True:
            res = reader.request(reader.PICC.REQIDL)

            if res.status == reader.MI.OK:
                print('\nDetected a card')

            res = reader.anti_collision()

            if res.status == reader.MI.OK:
                print(f'UID: {" ".join(["0x{:02X}".format(x) for x in res.uid])}')

                key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                reader.select_tag(res.uid)

                status = reader.authenticate(reader.PICC.AUTHENT1A, 8, key, res.uid)

                if status == reader.MI.OK:
                    print('Reading block 8')
                    data = reader.read_block(8)
                    reader.stop_crypto1()
                    print(' '.join('0x{:02X}'.format(x) for x in data))
                else:
                    print('Authentication error')
    except KeyboardInterrupt:
        reader.cleanup()
        print('Exiting...')


if __name__ == '__main__':
    main()
