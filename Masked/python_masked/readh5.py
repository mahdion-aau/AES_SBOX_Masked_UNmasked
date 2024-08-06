# load the dataset
import h5py
import numpy as np

# power traces and input bytes are stored in a HDF5 file
filename = "M_230_40K_2MHz.h5"
fhandle = h5py.File(filename)
idset = fhandle['input_k_p_u_v']
tset = fhandle['trace_set']
odset = fhandle['output_ms']
k = np.array(idset[:, 0], dtype='int')
x = np.array(idset[:, 1], dtype='int')
u = np.array(idset[:, 2], dtype='int')
v = np.array(idset[:, 3], dtype='int')
inputs = np.array(idset[:, :], dtype='int')
msb = np.array(odset[:, :], dtype='int')


def keys(f):
    return [key for key in f.keys()]
print(keys(fhandle))