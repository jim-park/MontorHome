adsensors.c requires cross compilation.

Using TI's toolchain

To compile

`msp430-gcc -mmcu=msp430g2231 -o adsensors.bin adsensors.c`


To Program msp430 device

`mspdebug rf2500`

`> prog ./adsensors.bin`
