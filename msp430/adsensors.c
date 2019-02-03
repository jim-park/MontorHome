//******************************************************************************
//
// Target device is TI MSP430g2231.
// This process responds to any char input to P1.2. Upon reception of a char;
// the voltage at P1.7 is sampled and a json string containing the result is
// transmitted to P1.1.
//
// __author__ = "James Park"
// __email__ = "jim@linuxnetworks.co.uk"
// __license__ = "Apache License, Version 2.0"
//
//******************************************************************************

#include <msp430g2231.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <float.h>
#include <math.h>

//------------------------------------------------------------------------------
// Hardware-related definitions
//------------------------------------------------------------------------------
#define UART_TXD   0x02                     // TXD on P1.1 (Timer0_A.OUT0)
#define UART_RXD   0x04                     // RXD on P1.2 (Timer0_A.CCI1A)

//------------------------------------------------------------------------------
// Conditions for 9600 Baud SW UART, SMCLK = 1MHz
//------------------------------------------------------------------------------
#define UART_TBIT_DIV_2     (1000000 / (9600 * 2))
#define UART_TBIT           (1000000 / 9600)

//------------------------------------------------------------------------------
// Sampling parameters
//------------------------------------------------------------------------------
#define SAMP_NUM 8

//------------------------------------------------------------------------------
// Global variables used for full-duplex UART communication
//------------------------------------------------------------------------------
unsigned int txData;                        // UART internal variable for TX
unsigned char rxBuffer;                     // Received UART character

//------------------------------------------------------------------------------
// Function prototypes
//------------------------------------------------------------------------------
void flash_p16(void);
void send_sample(unsigned int *);
unsigned int csum(char *);
void acquire_sample(unsigned int *);
void ADC10_init(void);
void GPIO_init(void);
void Clock_init(void);
void TimerA_UART_init(void);
void TimerA_UART_tx(unsigned char byte);
void TimerA_UART_print(char *string);

//------------------------------------------------------------------------------
// main
//------------------------------------------------------------------------------
int main(void)
{
  // For sample output
  unsigned int sample = 0, k = 0, i=0;
  unsigned int samp_win[SAMP_NUM] = { 0 };
  // Initalise stuff
  Clock_init();                           // Start clocks
  GPIO_init();                            // Setup GPIO
  ADC10_init();                           // Setup ADC1
  TimerA_UART_init();                     // Start Timer_A UART
  memset(samp_win, 0, sizeof(int)*SAMP_NUM);

  __enable_interrupt();                   //  Enable interrupts

  // infinite loop
  for (;;)
  {
    // Wait for incoming character
    __bis_SR_register(LPM0_bits);

    // Sample battery with ADC10
    acquire_sample(&sample);
    flash_p16();

    if (i < SAMP_NUM) {
      samp_win[i] = sample;
      i++;
    } else if ( i > SAMP_NUM ) {
      i = SAMP_NUM;
    } else {
      for ( k=1; k<SAMP_NUM; k++) {
        samp_win[k] = samp_win[k-1];
      }
      samp_win[0] = sample;
    }

    // Send sample over UART
    send_sample(&sample);

  }
}

//------------------------------------------------------------------------------
// Flash LED - Turn on and off Pin 1.6 for 0.5 secs.
//------------------------------------------------------------------------------
void flash_p16(void)
{
  P1OUT = 0x40;              // Turn on P1.6
  __delay_cycles(500000);
  P1OUT = 0x00;              // Turn off P1.6
}

//------------------------------------------------------------------------------
// Send 'sample' over UART.
//------------------------------------------------------------------------------
void send_sample(unsigned int * sample)
{
  /*
   *    This json message format is used:
   *    {"sensor":[{"id":"0", "val":"582"}, {"id":"1", "val":"542"}]}
   */
  char sstring[4] = "";  //buf to hold sample as str
  const char * out_str_start = "{\"sensor\":[{\"id\":\"1\",\"val\":\"";
  const char * out_str_end = "\"}]} ";
  char tmpstr[42]  = "";
  unsigned int chksum = 0;
  utoa(*sample, sstring, 10);
  strcat(tmpstr, out_str_start);
  strcat(tmpstr, sstring);
  strcat(tmpstr, out_str_end);
  chksum = csum(tmpstr);
  memset(sstring, 0, 4 * sizeof(char));
  utoa(chksum, sstring, 16);
  strcat(tmpstr, sstring);
  strcat(tmpstr, "\r\n");
  TimerA_UART_print(tmpstr);
}

//------------------------------------------------------------------------------
// Calculate a simple csum of the data to send with the data.
//------------------------------------------------------------------------------
unsigned int csum(char * str)
{
  short unsigned int ret = 0x0;
  short unsigned int i = 0;
  
  for (i=0; i<strlen(str); i++) {
    ret += str[i];
  }
  return ret & 0xFF;
}

//------------------------------------------------------------------------------
// Sample using the ADC10 and place result in 'sample'.
//------------------------------------------------------------------------------
void acquire_sample(unsigned int * sample)
{
  unsigned int cum_sample_tot = 0;
  unsigned short int i = 0;
  const unsigned short int num_samples = 8;

  for (i=0; i<num_samples; i++) {
    ADC10CTL0 |= ENC + ADC10SC;				   // Sampling and conversion start
    while (ADC10CTL1 & ADC10BUSY);       // ADC10BUSY?
    cum_sample_tot += 0x3FF & ADC10MEM;
  }

  // Return average
  *sample = cum_sample_tot/i;
}

//------------------------------------------------------------------------------
// Initialise ADC10 - use channel 7, Pin 1.7.
//------------------------------------------------------------------------------
void ADC10_init(void)
{
  ADC10CTL0 = SREF_1 + ADC10SHT_3 + REFON + ADC10ON + REF2_5V + ADC10IE;
  ADC10CTL1 = INCH_7;                       // input A1
}


//------------------------------------------------------------------------------
// Initialise GPIO
// P1.1(tx) & P1.2(rx) for UART use,
// P1.7 for ADC10 sampling.
//------------------------------------------------------------------------------
void GPIO_init(void)
{
    P1OUT = 0x00;                           // Initialize all GPIO
    P1SEL = UART_TXD + UART_RXD;            // Timer function for TXD/RXD pins
    P1DIR = 0xFF & ~UART_RXD & ~0x80;       // Set all pins but RXD and P1.7 (ADC10) to output
    P2OUT = 0x00;
    P2SEL = 0x00;
    P2DIR = 0xFF;
}


//------------------------------------------------------------------------------
// Initialise clock to 1 Mhz, disable watchdog.
//------------------------------------------------------------------------------
void Clock_init(void)
{
    WDTCTL = WDTPW + WDTHOLD;               // Stop watchdog timer
    if (CALBC1_1MHZ==0xFF)					        // If calibration constants erased
    { while(1);}                            // do not load, trap CPU!!
    DCOCTL = 0;                             // Select lowest DCOx and MODx settings
    BCSCTL1 = CALBC1_1MHZ;
    DCOCTL = CALDCO_1MHZ;
}

//------------------------------------------------------------------------------
// Configure Timer_A for full-duplex UART operation.
//------------------------------------------------------------------------------
void TimerA_UART_init(void)
{
    TACCTL0 = OUT;                          // Set TXD Idle as Mark = '1'
    TACCTL1 = SCS + CM1 + CAP + CCIE;       // Sync, Neg Edge, Capture, Int
    TACTL = TASSEL_2 + MC_2;                // SMCLK, start in continuous mode
}

//------------------------------------------------------------------------------
// Output one byte using the Timer_A UART.
//------------------------------------------------------------------------------
void TimerA_UART_tx(unsigned char byte)
{
    while (TACCTL0 & CCIE);                 // Ensure last char got TX'd
    TACCR0 = TAR;                           // Current state of TA counter
    TACCR0 += UART_TBIT;                    // One bit time till first bit
    TACCTL0 = OUTMOD0 + CCIE;               // Set TXD on EQU0, Int
    txData = byte;                          // Load global variable
    txData |= 0x100;                        // Add mark stop bit to TXData
    txData <<= 1;                           // Add space start bit
}

//------------------------------------------------------------------------------
// Tx a string over UART using the Timer_A.
//------------------------------------------------------------------------------
void TimerA_UART_print(char *string)
{
    while (*string) {
        TimerA_UART_tx(*string++);
    }
}

//------------------------------------------------------------------------------
// Timer_A UART - Transmit Interrupt Handler.
//------------------------------------------------------------------------------
#if defined(__TI_COMPILER_VERSION__) || defined(__IAR_SYSTEMS_ICC__)
#pragma vector = TIMERA0_VECTOR
__interrupt void Timer_A0_ISR(void)
#elif defined(__GNUC__)
void __attribute__ ((interrupt(TIMERA0_VECTOR))) Timer_A0_ISR (void)
#else
#error Compiler not supported!
#endif
{
    static unsigned char txBitCnt = 10;

    TACCR0 += UART_TBIT;                    // Add Offset to CCRx
    if (txBitCnt == 0) {                    // All bits TXed?
        TACCTL0 &= ~CCIE;                   // All bits TXed, disable interrupt
        txBitCnt = 10;                      // Re-load bit counter
    }
    else {
        if (txData & 0x01) {
          TACCTL0 &= ~OUTMOD2;              // TX Mark '1'
        }
        else {
          TACCTL0 |= OUTMOD2;               // TX Space '0'
        }
        txData >>= 1;
        txBitCnt--;
    }
}

//------------------------------------------------------------------------------
// Timer_A UART - Receive Interrupt Handler.
//------------------------------------------------------------------------------
#if defined(__TI_COMPILER_VERSION__) || defined(__IAR_SYSTEMS_ICC__)
#pragma vector = TIMERA1_VECTOR
__interrupt void Timer_A1_ISR(void)
#elif defined(__GNUC__)
__attribute__((interrupt(TIMERA1_VECTOR))) void Timer_A1_ISR (void)
#else
#error Compiler not supported!
#endif
{
    static unsigned char rxBitCnt = 8;
    static unsigned char rxData = 0;

    switch ( TAIV ) {
    case TAIV_TACCR1:                        // TACCR1 CCIFG - UART RX
        TACCR1 += UART_TBIT;                 // Add Offset to CCRx
        if (TACCTL1 & CAP) {                 // Capture mode = start bit edge
            TACCTL1 &= ~CAP;                 // Switch capture to compare mode
            TACCR1 += UART_TBIT_DIV_2;       // Point CCRx to middle of D0
        }
        else {
            rxData >>= 1;
            if (TACCTL1 & SCCI) {            // Get bit waiting in receive latch
                rxData |= 0x80;
            }
            rxBitCnt--;
            if (rxBitCnt == 0) {             // All bits RXed?
                rxBuffer = rxData;           // Store in global variable
                rxBitCnt = 8;                // Re-load bit counter
                TACCTL1 |= CAP;              // Switch compare to capture mode
                __bic_SR_register_on_exit(LPM0_bits);  // Clear LPM0 bits from 0(SR)
            }
        }
        break;
    }
}
