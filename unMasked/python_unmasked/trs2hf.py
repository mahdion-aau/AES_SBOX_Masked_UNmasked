import h5py
import trsfile
import numpy as np


class TRS:
    def __init__(self, trs_file_name) -> object:
        trace_root = trsfile.open(trs_file_name, 'r')
        self.pos = trace_root.engine.data_offset  # data_offset
        headers = trace_root.engine.headers
        for header, value in headers.items():  # Gives the access to key & value f header
            if 'NUMBER_TRACES' in header.name:
                self.number_of_traces = value
            elif 'NUMBER_SAMPLES' in header.name:
                self.number_of_samples = value
            elif 'SAMPLE_CODING' in header.name:
                self.is_float = value.is_float  # sample_coding
            elif 'LENGTH_DATA' in header.name:
                self.cryptolen = value
        self.traces = [trace_root[i] for i in range(self.number_of_traces)]

        self.in_data_len = 2
        self.output_len = 1
        self.data_length = self.in_data_len + self.output_len

    def get_trace_sample(self, ind):  # ind = index # Gives the samples of the index_th trace
        if ind < self.number_of_traces:
            return self.traces[ind].samples

    def get_all_traces(self):
        """ This function extracts all traces from TRS file"""
        all_trace = np.zeros((int(self.number_of_traces), self.number_of_samples))
        for i in range(self.number_of_traces):
            all_trace[i] = self.get_trace_sample(i)
        return all_trace

    def get_trace_data(self, ind):  # Gives the data of the index_th trace
        in_data_ind = np.zeros((int(self.in_data_len)), np.dtype('B'))
        c_ind = np.zeros((int(self.output_len)), np.dtype('B'))
        d_ind = self.traces[ind].data

        if ind < self.number_of_traces:  # Check the correctness of the number_of_traces
            in_data_length = int(self.in_data_len)
            # Extracting in_data
            for i in range(0, in_data_length):
                in_data_ind[i] = d_ind[i]

            # Extracting output data
            for i in range(in_data_length, int(self.data_length)):
                c_ind[i - in_data_length] = d_ind[i]

        return [in_data_ind, c_ind]

    def get_all_trace_data(self):
        input_data = np.zeros((self.number_of_traces, int(self.in_data_len)), np.dtype('B'))  # input
        output_data = np.zeros((self.number_of_traces, int(self.output_len)), np.dtype('B'))  # output
        for i in range(int(self.number_of_traces)):
            [in_data_int, out_data_int] = self.get_trace_data(i)
            input_data[i] = in_data_int
            output_data[i] = out_data_int

        return [input_data, output_data]


name = 'unM_120_20K_2MHz'

trs = TRS(name + ".trs")
[d1, d2] = trs.get_all_trace_data()
hf = h5py.File(name + '.h5', 'w')
hf.create_dataset('trace_set', data=trs.get_all_traces())
hf.create_dataset('input_k_p', data=d1)
hf.create_dataset('output_sbox', data=d2)
hf.create_dataset('num_trace', data=trs.number_of_traces)
hf.create_dataset('num_sample', data=trs.number_of_samples)
hf.create_dataset('len_data', data=trs.cryptolen)