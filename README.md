# mfrc522pi

A small class to interface with the NFC reader Module MFRC522 on the Raspberry Pi.
This is a Python port of the example code for the NFC module MF522-AN.

## Requirements
This code requires you to have SPI-Py installed from the following repository:
https://github.com/lthiery/SPI-Py

## Examples
This repository includes a couple of examples showing how to read, write, and dump data from a chip. They are thoroughly commented, and should be easy to understand.

## Pins

| Name | Pin # | Pin name |
|:------:|:-------:|:--------:|
| SDA  | 24    |  GPIO8   |
| SCK  | 23    |  GPIO11  |
| MOSI | 19    |  GPIO10  |
| MISO | 21    |  GPIO9   |
| IRQ  | None  |   None   |
| GND  | Any   |   GND    |
| RST  | 22    |  GPIO25  |
| 3.3V | 1     |   3V3    |

## License
This code and examples are licensed under the GNU Lesser General Public License 3.0.
