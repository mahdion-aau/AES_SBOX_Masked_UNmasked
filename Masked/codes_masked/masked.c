
//sudo make --no-builtin-rules -f ${TARGET}/build/lib/scale.mk BSP="${TARGET}/build" USB="/dev/ttyUSB0" PROJECT="masked" PROJECT_SOURCES="masked.c $masked.h masked.S" clean all program
//arm-none-eabi-objdump -D -bbinary -marm masked.bin -Mforce-thumb > example.asm
#include <stdio.h>
#include <stdlib.h>
#include "masked.h"

int main( int argc, char* argv[]){
    if( !scale_init(&SCALE_CONF)){
        return -1;
    }

    // Variables are 8-bits only. However,
    // they considered as a word (4 bytes),
    // but the remaining 3 bytes are set to zero
    uint8_t p[4];      // plaintext
    uint8_t k[4];      // key
    uint8_t ms[4];      // sbox_out;   // sbox(p XOR k)


//    uint8_t output[4];

    while(true) {

        // Receiving the key, one byte
        k[0] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);
        // Receiving the plaintext, one byte
        p[0] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);
        // Receiving u, one byte
        u[0] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);
        // Receiving v, one byte
        v[0] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);

        ms[0] = 0;

        // Setting the remaining 3 bytes to zero
        for (int i = 1; i < 4; i++) {
            p[i] = 0;
            k[i] = 0;
            u[i] = 0;
            v[i] = 0;
            ms[i] = 0;
        }

        GenMaskedSbox();

        ///////////////////////////////////////////////////////////////////////////////////////////////////
        // Sending the sbox_out
//        scale_gpio_wr( SCALE_GPIO_PIN_TRG, true);

            Masked(&(p[0]), &(k[0]), &(ms[0]));

//        scale_gpio_wr( SCALE_GPIO_PIN_TRG, false);
        ///////////////////////////////////////////////////////////////////////////////////////////////////

        scale_uart_wr(SCALE_UART_MODE_BLOCKING,( (char) ms[0] ));
//        Masked(&(p[0]), &(k[0]), output);

//        for (int i = 0; i < 4; i++) {
//            scale_uart_wr(SCALE_UART_MODE_BLOCKING, (char) output[i]);
//        }

    }
    return 0;
}



