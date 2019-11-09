from globalvars import *

def feature_gen_time(signal, label):
    t_step = signal[1,0] - signal[0,0]
    l = len(signal)
    if label == 'time_f1':
    # total energy
        return np.sum(signal[:,1])*t_step
    elif label == 'time_f2':
    # mid-point energy
        return np.mean(signal[1:int(l/2),1])
    elif label == 'time_f3':
    # standard deviation over the latter half part
        return np.std(signal[int(l/2):l,1])
    elif label == 'time_f4':
    # slope of the rising part
        p = np.polyfit(signal[0:50,0],signal[0:50,1],1)
        return p[0]
    
def power_density_spectrum(sig):
    n=len(sig)
    Y = np.fft.fft(sig) # n-point discrete Fourier transform via FFT
    Y = Y / np.sqrt(n) # regularize the spectrum to preserve energy
    Y = abs(Y*Y)
    Y[1:int((n-1)/2)+1] *= 2 # freq=0 & freq=(1+k) when n=2k+1 component should not be doubled after taking a single side
    return Y[:int(n/2)+1] # signal power density spectrum
    
def feature_gen_freq(signal, label):
    Y = power_density_spectrum(signal[:,1])[2:]
    
    # Y[:100]=0
    # maxY = np.max(Y)
    # max_index = np.where(Y==maxY)[0][0]
    # if label == 'freq_f1':        
        # return max_index
    # elif label == 'freq_f2':
        # return np.sum(Y[2800:3100])
    # else: 
        # max2Y = np.max(Y)
        # max2Y_index = np.where(Y==max2Y)[0][0]
        # if label == 'freq_f3':
            # return np.sum(Y[5800:6100])
        # elif label == 'freq_f4':
            # return np.sum(Y[11800:12000])

    maxY = np.max(Y)
    max_index = np.where(Y==maxY)[0][0]
    if label == 'freq_f1':        
        return max_index
    elif label == 'freq_f2':
        return np.sum(Y[max_index-20:max_index+20])
    else: 
        Y[0:max_index+100] = 0
        max2Y = np.max(Y)
        max2Y_index = np.where(Y==max2Y)[0][0]
        if label == 'freq_f3':
            return max2Y_index
        elif label == 'freq_f4':
            return np.sum(Y[max2Y_index-20:max2Y_index+20])