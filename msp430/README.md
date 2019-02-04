## Cross compilation instructions for MSP430

> Assumes some standard Linux command line

TI's cross compilation toolchain (msp430-gcc) can be downloaded from <http://www.ti.com/tool/MSP430-GCC-OPENSOURCE>

TI's programming and debugging tool is available (for a price) from <http://www.ti.com/tool/MSPDS>

Another programming and debugging tool (mspdebug) is freely available from Daniel Beers excellent githib at <https://github.com/dlbeer/mspdebug>

To compile

>`msp430-gcc -mmcu=msp430g2231 -o adsensors.bin adsensors.c`


To Program msp430 device (using Daniel Beers mspdebug)

>`mspdebug rf2500`

at the mspdebug prompt

>`> prog ./adsensors.bin`

>`> run`
