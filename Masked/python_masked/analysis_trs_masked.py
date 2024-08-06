from TRS import TRS
import matplotlib.pyplot as plt
from tqdm import tqdm

# The value of Mask_ORD in TRS.py/analysis_trs_gadget.py/acquisition.py must be equalMask_ORD = 2
step = 1000


name = "m40"
trs = TRS(name+".trs")  # The name of the trs file (name.trs)
print('-------> The trs file contains {} traces'.format(trs.number_of_traces))
print('[+] Each trace contains {:d} samples'.format(trs.number_of_samples))

trs.plot_initial()

for i in range(int(trs.number_of_traces)):
    # print(trs.get_trace_sample(i))

    # Checking the correctness
    #################################################
    # print("[+] i =", i, "________________________________")
    [in_data_int, out_data_int] = trs.get_trace_data(i)

    in_data_byte = bytearray([j for j in in_data_int])
    out_data_byte = bytearray([j for j in out_data_int])

    k = in_data_byte[0]
    p = in_data_byte[1]
    u = in_data_byte[2]
    v = in_data_byte[3]

    s = out_data_byte

    if i % step == 0:
        print('- in_data {}: {}'.format(i, in_data_byte.hex()))
        print('- o {}: {}'.format(i, out_data_byte.hex()))
        print('i={0}'.format(i))
        print('- p: {}, k: {}'.format(hex(p), hex(k)))

        print('_________________________________________________________________________________________')
    trs.plot_trace(0, trs.number_of_samples, i)
[input_data, output_data] = trs.get_all_trace_data()
trs.plot_show('Time points', 'Voltage', 'Traces', 'Traces')
