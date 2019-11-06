from globalvars import *


def save_variable(filepath, variable):   
    with open(filepath, 'wb') as file:
        pickle.dump(variable, file)


def load_variable(filepath):
    with open(filepath, 'rb') as file:
        return pickle.load(file)

def initialization(disp_progress=False, direct_load=True):
#   read all data into data_buf and descriptions.
#   data_buf = {'power':[array([time,val]),...], 'force':[array([time,val]),...]}
#   descriptions.columns.values # column titles
#   descriptions.iloc[0,:] ordescriptions.loc[1,:]   # get the first row with attributes

    data_buf_path = data_path+'data_buf'
    if direct_load & os.path.exists(data_buf_path):
        data_buf = load_variable(data_buf_path)
    else:
        data_buf = {}    
        for signal in signal_type:        
            data_buf[signal]=[]
            signal_path = data_path + type_folders[signal]
            file_list = os.listdir(signal_path)
            file_list.sort()
            for i,file in enumerate(file_list):
                data = pd.read_fwf(signal_path+file, header=None) 
                # read_csv generates many NaN columns; no idea how to remove with its parameters
                data_buf[signal].append(data.values)
                # data.values[:,0] --- time; data.values[:,1] --- signal value;
                if disp_progress:
                    print( signal+' data %d/%d is read' % (i+1, len(file_list)))
        save_variable(data_buf_path, data_buf)
    
    description_path = data_path + '003_EXPTABLE_withWeldClassification.xls'
    descriptions = pd.read_excel(description_path, skiprows = list(range(0,6)))
    descriptions = descriptions.drop(descriptions.index[0]) 
    # delete the first row (which is invalid)
    
    return data_buf, descriptions

def data_segmentation(raw_data, signal_type):
# return the beginning and the end index of the main signal segment
# for power signal, use threshold
# for force signal, use moving total variance

    if signal_type == 'power':
        threshold = 20        
        loc = np.where(raw_data[:,1] > threshold)[0]
        ind_l = loc[0]; ind_u = loc[-1];
        
    elif signal_type == 'force':
        threshold = 0.3
        threshold_antijit = 0.4
        moving_len = 100
        l = len(raw_data)
        
        filtered_data = np.zeros(l)
        for i in range(1,l-1):
            filtered_data[i] = (raw_data[i,1]*2-raw_data[i-1,1]-raw_data[i+1,1])/3
        # apply a high-pass filter
        var_tmp = abs(filtered_data[0:l-1]-filtered_data[1:l])        
        moving_totvar = [np.sum(var_tmp[1:moving_len])]
        for i in range(l-moving_len-1):
            tmp_totvar = moving_totvar[i] - var_tmp[i] + var_tmp[i+moving_len]
            moving_totvar.append(tmp_totvar)
        moving_totvar = np.array(moving_totvar)
        # moving_var is the total variance of raw data over a segment of length moving_len
        estimated_threshold = np.percentile(moving_totvar,80)*threshold
        tmp = np.array(moving_totvar > estimated_threshold).astype(int)
        
        # tmp could be very noisy near the threshold; anti-jittering is needed
        tmp_totvar = np.sum(tmp[1:moving_len])
        for i in range(1,l-moving_len*2-2):
            tmp_totvar = tmp_totvar - tmp[i-1] + tmp[i-1+moving_len]
            tmp[i-1] = tmp_totvar
        loc = tmp > threshold_antijit*moving_len
        
        ind_u = np.where(loc)[0][-1]
        # upper index
        loc = ~loc[0:ind_u]
        ind_l = np.where(loc)[0][-1]
        # lower index
        ind_l=ind_l+moving_len; ind_u=ind_u+moving_len;
        
    return ind_l, ind_u


def segment_all(data_buf, disp_progress=False, direct_load=True):

    preprocessed_data_path = data_path + 'data'
    segment_index_path = data_path + 'seg_ind'
    if direct_load & os.path.exists(preprocessed_data_path) & os.path.exists(segment_index_path):
        preprocessed_data = load_variable(preprocessed_data_path)
        seg_ind = load_variable(segment_index_path)
    else:
        preprocessed_data={} 
        seg_ind = {}
        for signal in signal_type:        
            preprocessed_data[signal]=[]
            seg_ind[signal]=[]
            for i,raw_sig in enumerate(data_buf[signal]):
                (ind_l,ind_u) = data_segmentation(raw_sig, signal)
                preprocessed_data[signal].append(raw_sig[ind_l:ind_u,:])
                seg_ind[signal].append([ind_l,ind_u])
                # data.values[:,0] --- time; data.values[:,1] --- signal value;
                if disp_progress:
                    print( signal+' data %d is done' % (i+1))
        save_variable(preprocessed_data_path, preprocessed_data)
        save_variable(segment_index_path, seg_ind)
    
    return preprocessed_data, seg_ind
