## Raspberry Pi Zero W - Python code for RFIDReader/Writer and GPS Module - Internet Of Things

## Requirements
This code requires you to have SPI-Py installed from the following repository:
https://github.com/lthiery/SPI-Py

## Pins
You can use [this](http://i.imgur.com/y7Fnvhq.png) image for reference.
![alt text](https://raw.githubusercontent.com/saurabhk7/iot_project/raspi-zero-w-GPIO-pin.png)


| Name | Pin # | Pin name   |
|------|-------|------------|
| SDA  | 24    | GPIO8      |
| SCK  | 23    | GPIO11     |
| MOSI | 19    | GPIO10     |
| MISO | 21    | GPIO9      |
| IRQ  | None  | None       |
| GND  | Any   | Any Ground |
| RST  | 22    | GPIO25     |
| 3.3V | 1     | 3V3        |

## Usage
Import the class by importing MFRC522 in the top of your script. For more info see the examples.
