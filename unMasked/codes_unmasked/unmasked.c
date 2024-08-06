
//sudo make --no-builtin-rules -f ${TARGET}/build/lib/scale.mk BSP="${TARGET}/build" USB="/dev/ttyUSB0" PROJECT="unmasked" PROJECT_SOURCES="unmasked.c $unmasked.h unmasked.S" clean all program
//arm-none-eabi-objdump -D -bbinary -marm unmasked.bin -Mforce-thumb > example.asm
#include <stdio.h>
#include <stdlib.h>
#include "unmasked.h"

int main( int argc, char* argv[]){
    if( !scale_init(&SCALE_CONF)){
        return -1;
    }

    // Variables are 8-bits only. However,
    // they considered as a word (4 bytes),
    // but the remaining 3 bytes are set to zero
    uint8_t p[4];      // plaintext
    uint8_t k[4];      // key
    uint8_t s[4];      // sbox_out;   // sbox(p XOR k)


    while(true) {

        // Receiving the key, one byte
        k[0] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);

        // Receiving the plaintext, one byte
        p[0] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);

        s[0] = 0;

        // Setting the remaining 3 bytes to zero
        for (int i = 1; i < 4; i++) {
            p[i] = 0;
            k[i] = 0;
            s[i] = 0;
        }
        ///////////////////////////////////////////////////////////////////////////////////////////////////

        UNMASKED(&(p[0]), &(k[0]), &(s[0]));
//        UNMASKED(&(p[0]), &(k[0]), output);

        ///////////////////////////////////////////////////////////////////////////////////////////////////
        // Sending the sbox_out
        scale_uart_wr(SCALE_UART_MODE_BLOCKING, (char) s[0]);

    }
    return 0;
}


