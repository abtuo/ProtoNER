import json
import os
import subprocess
import torch
import numpy as np

with open('basic_config.json', 'r') as f:
    base_config = json.load(f)
from collections import defaultdict
from allennlp.nn import util


def execute(command):
    p = subprocess.Popen(command.split())
    p.wait()


# We delete the previous copies and logs
execute('rm -rf ' + os.getcwd() + '/copies/*')
execute('rm -rf ' + os.getcwd() + '/logs/*')
# Here is the list of all classes
classes = ['GPE', 'DATE', 'ORG', 'EVENT', 'LOC', 'FAC', 'CARDINAL', 'QUANTITY', 'NORP', 'ORDINAL', 'WORK_OF_ART',
           'PERSON', 'LANGUAGE', 'LAW', 'MONEY', 'PERCENT', 'PRODUCT', 'TIME']

GPU = [0, 1, 2] * 6  # I did it this way but you can do using some different way
configs = list(zip(classes, GPU))
for random_seed in range(1, 5):
    base_config['dataset_reader']['random_seed'] = random_seed
    processes = []

    for subseries in range(int(len(classes) / 3)):
        subconfigs = configs[(subseries * 3):(subseries * 3 + 3)]
        for config in subconfigs:
            # Here we edit the config for a particular experiment
            base_config['dataset_reader']['valid_class'] = config[0]
            base_config['dataset_reader']['drop_empty'] = False
            base_config['trainer']['cuda_device'] = -1
            this_dir = os.getcwd().split('/')[-1]

            copy_directory = os.getcwd()[:-(len(this_dir) + 1)] + '/copies/' + this_dir + '/pnet_' + config[
                0] + '_' + str(
                random_seed)

            if not os.path.exists(copy_directory):
                os.makedirs(copy_directory)

            # We create a copy of all the code and run it in this directorty.
            execute('rm -rf ' + copy_directory)
            execute('cp -r ' + os.getcwd() + '/base ' + copy_directory)

            model_directory = os.getcwd()[:-(len(this_dir) + 1)] + '/models/' + this_dir + '/pnet_' + config[
                0] + '_' + str(
                random_seed)

            if not os.path.exists(model_directory):
                os.makedirs(model_directory)

            # Here we save our config
            with open(copy_directory + '/config.json', 'w') as outfile:
                json.dump(base_config, outfile)

            # Here we substitute our config instead of the old one
            cmd = 'rm -f ' + model_directory + '/config.json'
            p = subprocess.Popen(cmd.split())
            p.wait()

            with open(model_directory + '/config.json', 'w') as outfile:
                json.dump(base_config, outfile)

            # Delete old logs (if there are some)
            execute('rm -f ' + model_directory + '/stdout.log')
            execute('rm -f ' + model_directory + '/stderr.log')

            # We need to edit the model after warming to load it
            '''
            try:
                # if we have done it already we would have loaded this flag successfully
                flag = np.load(model_directory + '/flag.npy')
            except:
                # We need to change the content of saved dictionary in the epoch we load from (the last one).
                for i_epoch in range(4, 5):
                    dic = torch.load(model_directory + '/training_state_epoch_{}.th'.format(i_epoch),
                                     map_location=util.device_mapping(-1))
                    p_keys = dic['optimizer']['state'].keys()
                    for p_key in p_keys:
                        dic['optimizer']['state'] = defaultdict(dict)
                    torch.save(dic, model_directory + '/training_state_epoch_{}.th'.format(i_epoch))
                np.save(model_directory + '/flag.npy', np.array([0]))
            '''
            # Then we run our experiment
            cmd = 'python3 ' + copy_directory + '/my_run.py train '
            cmd += copy_directory + '/config.json -s '
            cmd += model_directory + ' --recover'
            p = subprocess.Popen(cmd.split())
            processes.append(p)

        for i, process in enumerate(processes):
            process.wait()
