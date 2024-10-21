# mfrc522pi

Small library to detect/read/write MIFARE 13.56 MHz tags/cards/etc using RFID-MFRC522 module.  
This fork doesn't add anything fundamentally new, just updates the API and makes the code more readable.  

## How to run
 - `git clone https://github.com/lthiery/SPI-Py`
 - `cd SPI-Py`
 - `sudo python setup.py install`
 - `cd ../`
 - `git clone git@github.com:maxrt101/mfrc522-pi.git`
 - `cd mfrc522-pi`
 - `sudo python setup.py install`
 - `python3 examples/read.py`

## Examples
This repository includes a couple of examples showing how to read, write, and dump data from a card.

## How to connect to PI
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

Run `sudo raspi-config` and select `Interface Options` -> `SPI` - > `Yes`, after that select `Finish` and reboot the device.  
If you can't read cards, you may need to add `dtoverlay=spi0-hw-cs` to `/boot/firmware/config.txt` and reboot the device again.  

## License
This code and examples are licensed under the GNU Lesser General Public License 3.0.
