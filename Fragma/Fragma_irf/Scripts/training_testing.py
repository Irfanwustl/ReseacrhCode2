"""
DATE: 2024/04/06
FUNC: split data into training, validation and testing group, train and test CNN model for FRAGMA
INPUT FORMAT: chr     p1      p2      context metDens label   W_1     W_2     W_3     W_4     W_5     W_6     W_7     W_8     W_9     W_10    W_11   C_1      C_2     C_3     C_4     C_5     C_6     C_7     C_8     C_9     C_10    C_11 
AUTH  : Rong QIAO
"""

from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter

import sys
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

import torch
from torch.utils.data import Dataset, DataLoader
from torch import nn

import network



def DNA_reverse(sequence):
    return sequence[::-1]


def DNA_complement(sequence):
    trantab = str.maketrans('ACGTacgtNn','TGCAtgcaNn')
    string = sequence.translate(trantab)
    return string


# summarize the cg information into dict, and get the data number for M and U group
def data_summary(data_file):
    
    M_num = 0
    U_num = 0
    M_id = []
    U_id = []
    cg_dict = {}
    with open(data_file, 'r') as fr:
        line = fr.readline().rstrip().lstrip().split()
        while line:
            line = fr.readline().rstrip().lstrip().split()
            if len(line) <= 1:
                break
            
            cg_id = line[0]+':'+line[1]
            
            sequence = line[3]    # 12bp context
            w_seq = sequence[0:11]
            c_seq = DNA_complement(DNA_reverse(sequence))[0:11]
            if 'N' in w_seq or 'N' in c_seq:
                continue
            
            w_ratio = [float(x) for x in line[6:17]]     # [0.4,0.5,0.2,0.3]
            c_ratio = [float(x) for x in line[17:28]]

            label = line[5]

            if label == 'M':
                M_num += 1
                M_id.append(cg_id)
            elif label == 'U':
                U_num += 1
                U_id.append(cg_id)

            cg_dict[cg_id] = {'w_seq':w_seq, 'c_seq':c_seq, 'w_ratio':w_ratio, 'c_ratio':c_ratio, 'label':label}
    
    return cg_dict, M_num, U_num, M_id, U_id

# INPUT: data_file name
# OUTPUT: cg_dict: {
#                   'chr:start':
#                            w_seq:'ACGT'(str), c_seq:'ACGT'(str), w_ratio:[0.2](list), c_ratio[0.2](list), label:M or U
#                  }



# define dataloader
class TorchDataset(Dataset):
    
    def __init__(self, cg_dict, id_list):
        self.cg_dict = cg_dict
        self.id_list = id_list
    
    def __getitem__(self, idx):
        select_id = self.id_list[idx]
        w_seq = self.cg_dict[select_id]['w_seq']
        c_seq = self.cg_dict[select_id]['c_seq']
        w_ratio = self.cg_dict[select_id]['w_ratio']
        c_ratio = self.cg_dict[select_id]['c_ratio']
        
        w_matrix = transfer(w_seq, w_ratio)
        c_matrix = transfer(c_seq, c_ratio)
        
        matrix = np.vstack((w_matrix, c_matrix))
        
        label_mapping = {'M':1, 'U':0}
        label = label_mapping[self.cg_dict[select_id]['label']]
        
        return matrix, label, select_id
    
    def __len__(self):
        return len(self.id_list)
    

# build the feature matrix
def transfer(seq, ratio_list):
    
    seq_mapping = {'A':0, 'C':1, 'G':2, 'T':3}
    matrix = np.zeros((len(seq_mapping), len(seq)))
    for index in range(len(seq)):
        
        row = seq_mapping[seq[index]]
        col = index

        matrix[row, col] = ratio_list[index]

    return matrix


# define logger  
class Logger(object):
    
    def __init__(self, filename='log.txt'):
        self.terminal = sys.stdout
        self.log = open(filename, 'a')
        
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
        
    def flush(self):
        pass



def main(args):
    
    data_file = args.data_file
    output_path = args.output_path
    
    sys.stdout = Logger(output_path+'/log.txt')

    # data parameters
    TRAIN_PRO = 0.7
    VALID_PRO = 0.15
    TEST_PRO = 0.15

    BATCH_SIZE = 64
    
    
    # model parameters
    conv1_out_channels = 64
    conv1_kernel_size = 4
    conv2_out_channels = 64
    conv2_kernel_size = 4
    linear1_in = 320
    linear2_in = 10
    
    
    # training parameters
    lr = 0.001
    epoches = 100

    # ============ data processing =======================
    print('data processing ...')
    
    # get number for two classes and summarize the info into cg_dict
    cg_dict, M_num, U_num, M_id, U_id = data_summary(data_file)
#     print("Load data info: M: {}, U:{}".format(M_num, U_num))


    # down sampling
    if M_num > U_num:
        total_data = U_num
        M_new_id = np.random.choice(M_id, total_data, replace=False)
        U_new_id = U_id
    else:
        total_data = M_num
        M_new_id = M_id
        U_new_id = np.random.choice(U_id, total_data, replace=False)
    print('training: validation: testing is {}:{}:{}'.format(TRAIN_PRO, VALID_PRO, TEST_PRO))


    # get train, valid and test dataset id
    [M_train, M_test, U_train, U_test] = train_test_split(M_new_id, U_new_id, test_size=VALID_PRO+TEST_PRO, random_state=10)
    [M_val, M_test, U_val, U_test] = train_test_split(M_test, U_test, test_size=TEST_PRO/(TEST_PRO+VALID_PRO), random_state=10)
    
    train_id = list(M_train) + list(U_train)
    valid_id = list(M_val) + list(U_val)
    test_id = list(M_test) + list(U_test)

    # create data loader
    train_data = TorchDataset(cg_dict, train_id)
    trainDataLoader = DataLoader(dataset=train_data, batch_size = BATCH_SIZE, shuffle=True)

    valid_data = TorchDataset(cg_dict, valid_id)
    validDataLoader = DataLoader(dataset=valid_data, batch_size = BATCH_SIZE, shuffle=False)

    test_data = TorchDataset(cg_dict, test_id)
    testDataLoader = DataLoader(dataset=test_data, batch_size = BATCH_SIZE, shuffle=False)


    # ============ model building =======================
    
    dev = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


    net = network.CNN(conv1_out_channels, conv1_kernel_size, conv2_out_channels, conv2_kernel_size, linear1_in, linear2_in).to(dev)
    loss_fn = nn.BCELoss()
    optimizer = torch.optim.Adam(net.parameters(), lr)
#     print(loss_fn)
#     print(optimizer)
    
    
    # ============ training and validation =======================
    print('training...')
    
    bestValidLoss = 1000000
    bestValidAcc = 0
    train_loss_list = []
    valid_loss_list = []
    train_acc_list = []
    valid_acc_list = []
    for epoch in range(epoches):

        net.train()
        train_loss = 0
        train_correct_num = 0
        trainOutputList = []
        trainPredictList = []
        trainLabelList = []
        for batch_idx, (batch_data, batch_label, batch_id) in enumerate(trainDataLoader):

            batch_data = batch_data.to(dev, dtype=torch.float)
            batch_label = batch_label.reshape(-1, 1).to(dev, dtype=torch.float)

            optimizer.zero_grad()
            batch_output = net(batch_data)

            batch_loss = loss_fn(batch_output, batch_label)
            batch_loss.backward()
            optimizer.step()

            train_loss += batch_loss.item()
            train_correct_num += sum(batch_output.cpu().detach().ge(0.5)==batch_label.cpu().detach())

            trainOutputList = trainOutputList + batch_output.cpu().detach().numpy().reshape(-1).tolist()
            trainPredictList = trainPredictList + batch_output.cpu().detach().ge(0.5).numpy().reshape(-1).tolist()
            trainLabelList = trainLabelList + batch_label.cpu().detach().numpy().reshape(-1).tolist()

        train_loss /= len(trainDataLoader.dataset)
        train_acc = (train_correct_num / len(trainDataLoader.dataset) * 100).item()
        train_auc = roc_auc_score(np.array(trainLabelList), np.array(trainOutputList))


        net.eval()
        valid_loss = 0
        valid_correct_num = 0
        validOutputList = []
        validPredictList = []
        validLabelList = []
        with torch.no_grad():
            for batch_data, batch_label, batch_id in validDataLoader:

                batch_data = batch_data.to(dev, dtype=torch.float)
                batch_label = batch_label.reshape(-1, 1).to(dev, dtype=torch.float)

                batch_output = net(batch_data)

                valid_loss += loss_fn(batch_output, batch_label).item()          
                valid_correct_num += sum(batch_output.cpu().detach().ge(0.5)==batch_label.cpu().detach())

                validOutputList = validOutputList + batch_output.cpu().detach().numpy().reshape(-1).tolist()
                validPredictList = validPredictList + batch_output.cpu().detach().ge(0.5).numpy().reshape(-1).tolist()
                validLabelList = validLabelList + batch_label.cpu().detach().numpy().reshape(-1).tolist()

        valid_loss /= len(validDataLoader.dataset)
        valid_acc = (valid_correct_num / len(validDataLoader.dataset) * 100).item()
        print('Epoch: {} | training_loss: {} | training_acc: {}% | validation_loss: {} | validation_acc: {}%'.format(epoch+1, train_loss, train_acc, valid_loss, valid_acc))

        train_loss_list.append(train_loss)
        valid_loss_list.append(valid_loss)
        train_acc_list.append(train_acc)
        valid_acc_list.append(valid_acc)

        if valid_loss < bestValidLoss:
            bestValidLoss = valid_loss
            bestValidAcc = valid_acc            
#             print('saving model...')
            modelPath = output_path+'/best_model.pt'
            torch.save(net.state_dict(), modelPath)
#             fw = open('validResult.txt', 'w')
#             fw.write('label'+'\t'+'output'+'\t'+'predict'+'\n')
#             for idx in range(len(validOutputList)):
#                 fw.write(str(validLabelList[idx])+'\t'+str(validOutputList[idx])+'\t'+str(validPredictList[idx])+'\n')
#             fw.close()
            valid_auc = roc_auc_score(np.array(validLabelList), np.array(validOutputList))

    print('training finish =====================')
    print("trainingg auc: {}".format(train_auc))
    print("validation_auc: {}".format(valid_auc))

    
    
    # ============ testing =======================
    print("testing...")

    net.eval()
    test_loss = 0
    test_correct_num = 0
    testOutputList = []
    testPredictList = []
    testLabelList = []
    testIdList = []
    with torch.no_grad():
        for batch_data, batch_label, batch_id in testDataLoader:
            
            batch_data = batch_data.to(dev, dtype=torch.float)
            batch_label = batch_label.reshape(-1, 1).to(dev, dtype=torch.float)

            batch_output = net(batch_data)

            test_loss += loss_fn(batch_output, batch_label).item()          
            test_correct_num += sum(batch_output.cpu().detach().ge(0.5)==batch_label.cpu().detach())

            testOutputList = testOutputList + batch_output.cpu().detach().numpy().reshape(-1).tolist()
            testPredictList = testPredictList + batch_output.cpu().detach().ge(0.5).numpy().reshape(-1).tolist()
            testLabelList = testLabelList + batch_label.cpu().detach().numpy().reshape(-1).tolist()
            testIdList = testIdList + list(batch_id)


    test_loss /= len(testDataLoader.dataset)
    test_acc = (test_correct_num / len(testDataLoader.dataset) * 100).item()

    fw = open(output_path+'/testResult.txt', 'w')
    fw.write('chr\t'+'p1\t'+'p2\t'+'label\t'+'output\t'+'predict\n')
    for idx in range(len(testOutputList)):
        chr = testIdList[idx].split(':')[0]
        start = testIdList[idx].split(':')[1]
        end = str(int(start)+12)
        fw.write(chr+'\t'+start+'\t'+end+'\t'+str(testLabelList[idx])+'\t'+str(testOutputList[idx])+'\t'+str(testPredictList[idx])+'\n')
    fw.close()
    test_auc = roc_auc_score(np.array(testLabelList), np.array(testOutputList))

    print('testing finish =====================')
    print("testing auc: {}".format(test_auc))


def argparser():

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter, add_help=True)
    parser.add_argument('--data_file', default=None, type=str)
    parser.add_argument('--output_path', default=None, type=str)

    args = parser.parse_args()

    return args
        
        
if __name__ == '__main__':
    
    args = argparser()
    main(args)