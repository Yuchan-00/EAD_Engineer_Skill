/* E2 first measurement: real AVR firmware -> simavr -> VCD of PORTB */
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>
#include "avr/avr_mcu_section.h"
AVR_MCU(16000000, "atmega128");
AVR_MCU_VCD_FILE("blink.vcd", 1000);
const struct avr_mmcu_vcd_trace_t _mytrace[] _MMCU_ = {
    { AVR_MCU_VCD_SYMBOL("PORTB"), .what = (void*)&PORTB, },
};
int main(void) {
    DDRB = 0xFF;
    for (unsigned int i = 0; i < 200; i++) {
        PORTB ^= 1;
        for (volatile unsigned int d = 0; d < 400; d++) {}
    }
    cli();
    sleep_mode();   /* simavr ends the run on sleep with interrupts off */
    return 0;
}
