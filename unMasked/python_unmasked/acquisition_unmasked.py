
import sys
from picosdk.ps5000a import ps5000a as ps
from picosdk.functions import mV2adc, assert_pico_ok
import random
import serial
import time
from datetime import datetime
import ctypes
import numpy as np
import TRS_TraceSet
import secrets
from tqdm import tqdm
### for changing variable through command line
import sys

start_time = time.time()

step = 1000  # Printing the related data on screen after step acquisitions

name_trs_file = "unM_230_20K_2MHz"

# Number of traces
Number_traces = 20000

# Number of samples rate = 250 MSa/s, timebase = (2 ^ 2)/10e-9 =4ns
# (Page 22, 3.6 Timebase, Programming with the PicoScope 5000 Series (A API))
# https://www.picotech.com/download/manuals/picoscope-5000-series-a-api-programmers-guide.pdf
timebase = 2
points_per_clock = 125  # each clock is sampled with points_per_clock points

samples = 12 * points_per_clock
x = 21 * points_per_clock

sbox = [
            0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
            0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
            0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
            0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
            0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
            0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
            0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
            0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
            0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
            0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
            0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
            0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
            0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
            0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
            0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
            0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]


class Acquisition_Gadget(object):
    if __name__ == "__main__":
        # The setting for acquisition (Picoscope) come from:
        # https://github.com/picotech/picosdk-python-wrappers/tree/master/ps5000aExamples

        # Serial port communication: look this up in 'device manager'
        port = '/dev/ttyUSB0'  # Serial port

        # The length of the TX data in Byte (B)
        # The TX data is: p and k
        ##################################################
        input_data_len = 2

        # The length of the RX data in Byte (B)
        # The RX data is: sbox(p XOR k)
        ##################################################
        output_data_len = 1

        print("Input length:  ", input_data_len)
        print("Output length: ", output_data_len)

        # Initialized random generator for generating inputs and randomness
        ##################################################
        random.seed()

        # Open serial port
        ##################################################
        ser = serial.Serial(port)
        print("Opening the serial port ...")

        # Wait for 200ms
        time.sleep(0.1)

        # Connect the scope
        # Create chandle and status ready for use
        ##################################################
        chandle = ctypes.c_int16()
        status = {}

        # Open 5000 series PicoScope
        #################################################
        # ps5000aOpenUnit(*handle, *serial, resolution)
        # handle = chandle = ctypes.c_int16()
        # serial = None: the serial number of the scope
        # Resolution set to 8 Bit
        resolution = ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_8BIT"]
        # Returns handle to chandle for use in future API functions
        status["openunit"] = ps.ps5000aOpenUnit(ctypes.byref(chandle), None, resolution)

        try:
            assert_pico_ok(status["openunit"])
        except:  # PicoNotOkError:
            powerStatus = status["openunit"]

            # When a USB 3.0 device is connected to a non-USB 3.0 port, this means:
            # PICO_USB3_0_DEVICE_NON_USB3_0_PORT = (uint)0x0000011EUL == 286;
            if powerStatus == 286:
                status["changePowerSource"] = ps.ps5000aChangePowerSource(chandle, powerStatus)
            else:
                raise
            assert_pico_ok(status["changePowerSource"])

        # Set up channel A
        print("Preparing channel A ...")
        #################################################
        # ps5000aSetChannel(handle, channel, enabled, coupling_type, ch_Range, analogueOffset)
        # handle = chandle = ctypes.c_int16()
        chA = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"]
        coupling_type = ps.PS5000A_COUPLING["PS5000A_DC"]
        chA_Range = ps.PS5000A_RANGE["PS5000A_500MV"]
        status["setChA"] = ps.ps5000aSetChannel(chandle, chA, 1, coupling_type, chA_Range, 0.3)
        assert_pico_ok(status["setChA"])

        # Set up channel B
        print("Preparing channel B ...")
        #################################################
        # ps5000aSetChannel(handle, channel, enabled, coupling_type, ch_Range, analogueOffset)
        # handle = chandle = ctypes.c_int16()
        chB = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"]
        coupling_type = ps.PS5000A_COUPLING["PS5000A_DC"]

        #  opt / picoscope / include / libps5000a / ps5000aApi.h:  enPS5000ARange
        chB_Range = ps.PS5000A_RANGE["PS5000A_5V"]
        status["setChB"] = ps.ps5000aSetChannel(chandle, chB, 1, coupling_type, chB_Range, 0)
        assert_pico_ok(status["setChB"])

        # Set up signal trigger (Using Channel B)
        print("Preparing the trigger through channel B ...")
        #################################################
        # Set number of pre and post trigger samples to be collected
        post_trigger = False
        # trigger threshold(mV)
        threshold = 2000
        # trigger direction Rising_edge: True, Falling_edge: False
        posedge_trigger = True
        delay = 0

        # if post_trigger:
        #     preTriggerSamples = 0  # preTriggerSamples
        #     postTriggerSamples = samples  # postTriggerSamples
        # else:
        #     preTriggerSamples = samples
        #     postTriggerSamples = 0

        if post_trigger:
            preTriggerSamples = 0  # preTriggerSamples
            postTriggerSamples = samples  # postTriggerSamples
        else:
            preTriggerSamples = samples + x
            postTriggerSamples = x

        # ps5000aSetSimpleTrigger(handle, enable,source, threshold, direction, delay, autoTrigger_ms)
        # handle = chandle = ctypes.c_int16()
        source = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"]
        # mV2adc(millivolts, range, maxADC): Takes a voltage value and converts it into adc counts
        # maxADC = ctypes.c_int16(32512) # 32512 the Max value that PicoScope can represent.
        # however, it should be 2 ^ 16 = 65536
        # when vertical values are represented by integer,
        # they are always in range (the range of vertical axis) [-32512, 32512]* uint
        # [-5v, 5V]
        threshold = mV2adc(threshold, chB_Range, ctypes.c_int16(32512))
        direction_rising = ps.PS5000A_THRESHOLD_DIRECTION["PS5000A_RISING"]
        direction_falling = ps.PS5000A_THRESHOLD_DIRECTION["PS5000A_FALLING"]

        if posedge_trigger:
            status["trigger"] = ps.ps5000aSetSimpleTrigger(chandle, 1, source, threshold, direction_rising, delay, 0)

        else:
            status["trigger"] = ps.ps5000aSetSimpleTrigger(chandle, 1, source, threshold, direction_falling, delay, 0)

        assert_pico_ok(status["trigger"])

        # Create buffers ready for assigning pointers for data collection
        #################################################
        # ps5000aSetDataBuffers(handle, source, * bufferMax, * bufferMin, bufferLth, segmentIndex, mode)
        # handle = chandle = ctypes.c_int16()
        Databuffer = (ctypes.c_int16 * samples)()
        point_bufferMax = ctypes.byref(Databuffer)
        status["setDataBuffers0"] = ps.ps5000aSetDataBuffers(chandle, 0, point_bufferMax, None, samples, 0, 0)
        assert_pico_ok(status["setDataBuffers0"])

        # Write TRS file header:
        #################################################
        # write_header(self, n, number_of_samples, isint, cryptolen, xscale, yscale):

        trs = TRS_TraceSet.TRS_TraceSet(name_trs_file + ".trs")
        # 65536 = 2 ^ 16
        # yscale is Vertical UNIT. unit=ChannelA.range/65536.
        # chA_Range = ps.PS5000A_RANGE["PS5000A_1V"]: 1 V ---> 1\65536
        # timebase = 1: 2/1e9 = 2 ns = 2e-9

        # The data stored in trs file is: p, k, s
        data_length = input_data_len + output_data_len
        print("data length in trs file: ", data_length)

        trs.write_header(Number_traces, samples, True, data_length, 2E-9, 1 / 65536)

        for i in tqdm(range(0, Number_traces)):

            # Generate inputs
            ##################################################
            p_int = secrets.randbits(8)  # type: int
            k_int = 230  # type: int

            # Converting p_int and k_int to "byte" type, in order to store in trs file
            p = p_int.to_bytes(1, sys.byteorder)
            k = k_int.to_bytes(1, sys.byteorder)

            # The input data
            input = k + p

            # Run block capture
            #################################################
            # ps5000aRunBlock(handle, noOfPreTriggerSamples, noOfPostTriggerSamples,
            # timebase,* timeIndisposedMs, segmentIndex, lpReady, * pParameter)
            # handle = chandle = ctypes.c_int16()
            status["runBlock"] = ps.ps5000aRunBlock(chandle, preTriggerSamples, postTriggerSamples, timebase, None, 0, None, None)
            assert_pico_ok(status["runBlock"])

            # Send inputs through serial port
            #################################################
            ser.write(input)

            # Receive outputs through serial port
            #################################################
            # Read outputs
            output = bytearray(ser.read(output_data_len))

            # Check for data collection to finish using ps5000aIsReady
            #################################################
            # ps5000aIsReady(chandle, * ready)
            # handle = chandle = ctypes.c_int16()
            ready = ctypes.c_int16(0)
            check = ctypes.c_int16(0)
            while ready.value == check.value:
                status["isReady"] = ps.ps5000aIsReady(chandle, ctypes.byref(ready))

            # Create overflow location
            #################################################
            # ps5000aGetValues(handle, startIndex, * noOfSamples, downSampleRatio,
            # downSampleRatioMode, segmentIndex, * overflow)
            # handle = chandle = ctypes.c_int16()
            overflow = ctypes.c_int16()
            # create converted type maxSamples
            cTotalSamples = ctypes.c_int32(samples)

            # Retried data from scope to buffers assigned above
            point_samples = ctypes.byref(cTotalSamples)  # pointer to number of samples
            point_overflow = ctypes.byref(overflow)  # pointer to overflow
            status["getValues"] = ps.ps5000aGetValues(chandle, 0, point_samples, 0, 0, 0, point_overflow)
            assert_pico_ok(status["getValues"])

            # If Overflow occurs, change the value analogueOffset in ps5000aSetChannel
            # overflow, returns a flag that indicates whether an over voltage has occurred on any of the
            # channels.It is a bit pattern with bit 0 denoting ChannelA and bit 1 ChannelB.
            if overflow.value != 0:
                print("overflow.value:", overflow.value)
                print("overflow!")

            # Write trace into trs file
            #################################################
            # The Data need to be saved in trs file
            data = bytearray(k + p)

            trs.write_trace(data, output, np.array(Databuffer), True)

            out = sbox[p_int ^ k_int].to_bytes(1, sys.byteorder)
            if out != output:
                print("ERROR: sbox[p ^ k] != s")
                print("out", hex(out))

            if i % step == 0:
                print('\n- i: {} -------------------------------------------------------'.format(i))
                print('- p: {} '.format(p.hex()))
                print('- k: {} '.format(k.hex()))
                print('- s: {} '.format(output.hex()))
                print('___________________________________________________________________')

        # Closing the trs file
        #################################################
        trs.close()
    print("The number of traces:", i + 1)


print("__________________________________")
print("Duration of acquisition (sec):", (time.time() - start_time))
print("Duration of acquisition (min):", (time.time() - start_time) / 60)
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)