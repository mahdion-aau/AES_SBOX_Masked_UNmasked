# load the dataset
import numpy as np
from TRS import TRS
import matplotlib.pyplot as plt
import pprint  # print dict
import copy  # copy dict
import pickle
import time
from datetime import datetime
start_time = time.time()

points_per_clock = 125  # each clock is sampled with 125 points

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


def GenMaskedSbox(u, v):
    maskedsbox = []
    for j in range(256):    # j = p+k+u, i = j+u = p+k
        maskedsbox.append(sbox[j ^ u] ^ v)
    return maskedsbox


def centring_trace(trace_set):
    """ All traces in the set are centred: x-mean"""
    mean_t = np.mean(trace_set, axis=0)
    centred_trace = trace_set - mean_t.transpose()
    return centred_trace


# power traces and input bytes are stored in a trs file
def extract_trace_sets(trs):
    n_t = trs.number_of_traces
    n_s = trs.number_of_samples
    len_p = trs.cryptolen
    cycle_sample = points_per_clock  # each cycle is sampled with cycle_s points
    # The number of cycles/instructions for executing the gadget
    # cycle = int(n_s / cycle_sample)
    all_traces_ = trs.get_all_traces()
    # c_all_traces = centring_trace(all_traces_)
    all_data = trs.get_all_trace_data()
    print("data_len_in_trs_file:", all_data[0].shape)
    print("data_len_in_trs_file:", all_data[1].shape)

    return [all_traces_, all_data[0], all_data[1]]


# im: InterMediate
def im_data(all_data, ind):
    d = np.zeros(len(all_data))
    for i in range(len(all_data)):
        d[i] = all_data[i][ind]
    return d.astype(int)


# def im_data_computing_xor(all_data, ind_1, ind_2):
#     d = np.zeros(len(all_data))
#     for i in range(len(all_data)):
#         d[i] = np.bitwise_xor(all_data[i][ind_1], all_data[i][ind_2])
#     return d.astype(int)

def im_data_xor_2val(v1, v2):
    d = np.zeros(len(v1))
    for i in range(len(v1)):
        d[i] = np.bitwise_xor(v1[i], v2[i])
    return d.astype(int)


def table_sbox(im_data):
    t_d = np.zeros(len(im_data))
    for i in range(len(im_data)):
        t_d[i] = sbox[im_data[i]]
    return t_d.astype(int)


def table_MaskedSbox(im_data, u, v):
    t_d = np.zeros(len(im_data))
    for i in range(len(im_data)):
        msbox = GenMaskedSbox(u[i], v[i])
        t_d[i] = msbox[im_data[i]]
    return t_d.astype(int)


def calcNoise(data, traces, filt):
    # if the value "filt" does not exist in data: ind[0] =[], then Var = Nan
    ind = np.nonzero(data == filt)
    return np.var(traces[ind, :], axis=1)


def calMean(data, traces, filt):
    # if the value "filt" does not exist in data: ind[0] =[], then mean = Nan
    ind = np.nonzero(data == filt)
    return [np.mean(traces[ind, :], axis=1), len(ind[0])]


def computing_snr(data, traces):
    el = np.zeros((256, len(traces[0])))
    for i in range(256):
        el[i, :] = calcNoise(data, traces, i)
    elNoise = np.nanmean(el, axis=0)
    # print("____________________________________")
    # print("el_noise:")
    # # print("%s" % np.array_str(np.sqrt(elNoise), precision=2))
    # print(elNoise)

    mean_traces = np.zeros((256, len(traces[0])))
    n_traces = np.zeros(256)

    for i in range(256):
        [mean_traces[i, :], n_traces[i]] = calMean(data, traces, i)

    mean_of_means = np.nanmean(mean_traces, axis=0)
    cent_trace_means = (mean_traces - mean_of_means.transpose())
    # p_exp = np.var(cent_trace_means, axis=0)
    s = 0
    for i in range(256):
        if np.isnan(cent_trace_means[i][0]):
            s += 0
        else:
            s += n_traces[i] * cent_trace_means[i] ** 2
    p_exp = s / len(traces)

    # print("p_exp:")
    # print("%s" % np.array_str(p_exp, precision=2))

    s_n_r = p_exp / elNoise

    # print("snr:")
    # print("%s" % np.array_str(s_n_r, precision=2))
    # print("____________________________________")
    return [elNoise, p_exp, s_n_r]


def computing_snr_l(data, traces, start, end):
    l = end - start
    el = np.zeros((l, len(traces[0])))
    for i in range(start, end):
        el[i - start, :] = calcNoise(data, traces, i)
    elNoise = np.nanmean(el, axis=0)
    # print("____________________________________")
    # print("el_noise:")
    # # print("%s" % np.array_str(np.sqrt(elNoise), precision=2))
    # print(elNoise)

    mean_traces = np.zeros((l, len(traces[0])))
    n_traces = np.zeros(l)

    for i in range(start, end):
        [mean_traces[i - start, :], n_traces[i - start]] = calMean(data, traces, i)

    mean_of_means = np.nanmean(mean_traces, axis=0)
    cent_trace_means = (mean_traces - mean_of_means.transpose())
    # p_exp = np.var(cent_trace_means, axis=0)
    s = 0
    for i in range(start, end):
        if np.isnan(cent_trace_means[i - start][0]):
            s += 0
        else:
            s += n_traces[i - start] * cent_trace_means[i - start] ** 2
    p_exp = s / len(traces)

    # print("p_exp:")
    # print("%s" % np.array_str(p_exp, precision=2))

    s_n_r = p_exp / elNoise

    # print("snr:")
    # print("%s" % np.array_str(s_n_r, precision=2))
    # print("____________________________________")
    return [elNoise, p_exp, s_n_r]


def individual_poi(s_n_r, threshold):
    p_i_o = []
    k = int(len(s_n_r) / points_per_clock)
    for i in range(k):
        a = s_n_r[i * points_per_clock:(i + 1) * points_per_clock]
        ind = np.argmax(a)
        if a[ind] > threshold:
            p_i_o.append(ind + i * points_per_clock)
    return p_i_o


name = "M_230_40K_2MHz"
trs = TRS(name + ".trs")
n_t = trs.number_of_traces
n_s = trs.number_of_samples
[t, data, out] = extract_trace_sets(trs)
print("-------------------------------------------------------------------------------")
print('-------> Info:')
print('[+] Input length: {}'.format(trs.in_data_len))
print('[+] Output length: {}'.format(trs.output_len))
print('[+] Number of traces: {}'.format(n_t))
print('[+] Number of samples: {}'.format(n_s))
t = centring_trace(t)


# Computing the intermediate values:
# data in trs file:
# k + p + sbox(p^k) (x = p)

# Var(a) = Var(-a)
####################################################################################################
in_d = data
out_d = out
k = im_data(data, 0)
x = im_data(data, 1)
u = im_data(data, 2)
v = im_data(data, 3)

x_xor_k = im_data_xor_2val(k, x)
x_xor_k_4 = x_xor_k * 4
s_x_xor_k = table_sbox(x_xor_k)
x_xor_k_xor_u = im_data_xor_2val(x_xor_k, u)
x_xor_k_xor_u_4 = x_xor_k_xor_u * 4

mSB_x_k_u = table_MaskedSbox(x_xor_k_xor_u, u, v)
mSB_xor_u = im_data_xor_2val(mSB_x_k_u, u)
mSB1_xor_v = im_data_xor_2val(mSB_xor_u, v)
out_ = im_data(out, 0)


all_im_str = ["u", "v", "x", "k",
              "x_xor_k",  "x_xor_k_xor_u",
              "x_xor_k_xor_u_4", "mSB_x_k_u",
              "mSB_xor_u", "mSB1_xor_v"
              ]
all_im = [u, v, x, k,
          x_xor_k, x_xor_k_xor_u,
          x_xor_k_xor_u_4, mSB_x_k_u,
          mSB_xor_u, mSB1_xor_v
          ]

dic_im = {}
if len(all_im) != len(all_im_str):
    print(len(all_im))
    print(len(all_im_str))
    print("len(all_im) != len(all_im_str)")

for i in range(len(all_im_str)):
    dic_im[all_im_str[i]] = all_im[i]

# print("pprint.pprint(dic_im, sort_dicts=False)")
# pprint.pprint(dic_im, sort_dicts=False)

e_p_s_dic = dict.fromkeys(all_im_str, {})
print("pprint.pprint(e_p_s_dic, sort_dicts=False)")
pprint.pprint(e_p_s_dic, sort_dicts=False)

eln_pvar_snr_base_dic = {"im_values": [], "val_are_not": [], "el_noise": [], "p_var": [], "snr": [], "poi": []}
eln_pvar_snr_dic = {}
for j, (key, value) in enumerate(dic_im.items()):
    del eln_pvar_snr_dic
    eln_pvar_snr_dic = copy.deepcopy(eln_pvar_snr_base_dic)

    threshold = 0.02  # in SNR for selecting poi

    start_ = 0
    end_ = 256

    [el, p, snr] = computing_snr_l(value, t, start_, end_)

    eln_pvar_snr_dic.setdefault("im_values", []).append(value)

    s_v = set(value)
    x = []  # values that are not in data
    for i in range(start_, end_):
        i_in_s_v = i in s_v
        if not i_in_s_v:
            x.append(i)

    eln_pvar_snr_dic.setdefault("val_are_not", []).append(x)
    eln_pvar_snr_dic.setdefault("el_noise", []).append(el)
    eln_pvar_snr_dic.setdefault("p_var", []).append(p)
    eln_pvar_snr_dic.setdefault("snr", []).append(snr)
    x_scale = [i / points_per_clock for i in range(n_s)]
    plt.plot(x_scale, snr)
    # plt.plot(snr)

    eln_pvar_snr_dic.setdefault("poi", []).append((individual_poi(snr, threshold)))
    e_p_s_dic[key] = eln_pvar_snr_dic

print("pprint.pprint(e_p_s_dic, sort_dicts=False)")
pprint.pprint(e_p_s_dic, sort_dicts=False)


# Saving the e_p_s_dic dict in hard disk
with open('dis_snr_unmasked.pkl', 'wb') as output:
    # Pickle dictionary using protocol 0.
    pickle.dump(e_p_s_dic, output)

poi = []
for j, (key, value) in enumerate(e_p_s_dic.items()):
    poi += e_p_s_dic[key]["poi"][0]
poi = np.sort(list(set(list(poi))))

print("____________________________________________________________________________________")
print("len_poi =", len(list(poi)), "from", n_s, "samples")
print("poi =", list(poi))
k = int(n_s / points_per_clock)
print("cycles:", list((poi / points_per_clock + 1).astype(int)))

print("\n____________________________________________________________________________________")
print("Duration of acquisition (sec):", (time.time() - start_time))
print("Duration of acquisition (min):", (time.time() - start_time) / 60)
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

plt.legend(["u", "v", "x", "k",
            "x+k", "x+k+u", "(x+k+u)*4",
            "MaskedS(x+k+u)=S(x+k)+v=mSB",
            "mSB+u=mSB1", "mSB1+v"], loc="upper left")
plt.title("SNR_based_on_values")
plt.xlabel("Samples * 125")
plt.xticks([i for i in range(int(n_s / points_per_clock))])
plt.ylabel("snr")
plt.grid()
plt.show()
