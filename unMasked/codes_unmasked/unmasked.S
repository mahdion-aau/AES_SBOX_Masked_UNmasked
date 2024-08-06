@@@@ Sbox(p XOR k) based on lookup 

  .syntax unified
  .text
  .thumb
  
  .extern sbox       @@@@ lookup table


@@@@@ uint8_t UNMASKED(uint8_t p, uint8_t k, uint8_t s); For calculating:  Sbox(p XOR k) based on lookup 
@@@@@@@@ UNMASKED(in_r0: p, in_r1: k, out_r0: s)
@ r0 = &p, @ r1 = &k, @ r2 = &s

.global UNMASKED
.func UNMASKED
UNMASKED:
	push     {lr}
	push	 {r3-r7}

  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop

############################################
@@@@ Clearing registers
    eors  r3, r3      @ r3 = 0
    eors  r4, r4      @ r4 = 0
    eors  r5, r5      @ r5 = 0
    eors  r6, r6      @ r6 = 0
    eors  r7, r7      @ r7 = 0

############################################
@@@@ Clearing write/read buses
    # mov  r4, #0         @ r4 = 0
    str  r4, [r2, #0]
    ldr  r4, [r2, #0]
############################################

    ldr  r6, =sbox      @ The address of the  "sbox"
    ldr  r4, [r2, #0]   @ Clearing read bus
    ldrb r3, [r0, #0]   @ r3 = p
    ldr  r4, [r2, #0]   @ Clearing read bus
    ldrb r5, [r1, #0]   @ r5 = k

    eors r3, r5         @ r3 = p xor k    @ ADDRound key

    lsls r3, r3, #2     @ r3 = r3 * 4  @ it is the address of elements in sbox

    ldr  r4, [r2, #0]   @ Clearing read bus
    ldrb r7, [r6, r3]   @ r7 = sbox[(p xor k)*4]
    strb r7, [r2, #0]   @ r7 = sbox[(p xor k)*4]


  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  @ Trigger
  @ scale.c: LPC13XX_GPIO1->GPIODATA &= ~( 0x1 <<  0 ) ; // initialise SCALE_GPIO_PIN_TRG = 0
  @ SCALE_GPIO_PIN_TRG in scale board: pin33: PIO1_0
  @ PIO1_0: https://www.digikey.pl/htmldatasheets/production/660585/0/0/1/lpc1311fhn33-551.html : 9.4 Register description
  @ baseaddress: 0x50010000, offset: 0x3ffc, baseaddress: 0x50010000, offset: 0x3ffc
  @ address: 0x5001ffc; producing this value: needs several instructions:
  @ https://developer.arm.com/documentation/den0042/a/Unified-Assembly-Language-Instructions/Instruction-set-basics/Constant-and-immediate-values
  @ Creating Trigger:                                       _____
  @ changing the value in add 0x5001ffc (0 --> 1 --> 0) ___|     |____ 
  

  @ Start of trigger
  movs r4, #80
  lsls r4, r4, #8
  movs r5, #1
  eors r4, r5  //0x5001
  lsls r4, #16 //0x50010000
  movs r5, #63 //0x3f
  lsls r5,r5,#8 //0x3f00
  eors r4,r5    //0x50013f00
  movs r5, #252
  eors r4,r5    //0x50013ffc
  movs r5,#1
  ldr  r6, [r4, #0]  @ r6 = 0 : SCALE_GPIO_PIN_TRG = 0
  # test: str  r6, [r3, #0]  @ r6 = 0xfc0f0000
  eors r5, r6  @ r5 = 1 @ Start trigger: SCALE_GPIO_PIN_TRG = 1
  str  r5, [r4, #0]
  # test: str  r5, [r3, #4] @ r6 = 0xfd0f0000
  nop
  nop
  nop
  nop
  str  r6, [r4, #0] @ End trigger: r6 = 0 : SCALE_GPIO_PIN_TRG = 0
	
  pop {r3-r7}
  pop {pc}
	
.endfunc


.end
