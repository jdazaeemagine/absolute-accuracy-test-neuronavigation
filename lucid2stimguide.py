import sys
import json
import csv

# converst a list of lists into a flat list:
# input: [[a], [b, c], [d]]
# output: [a, b, c, d]
def flatten(lst):
    return [item for sublist in lst for item in sublist]


# the "Stimuli" section of the input json file embeds a target object into
# the stimulus object.
# this function picks just the target name from the target object.
def target_name(target_dict):
    return target_dict['Name']


# combines sub-objects with the parent object or (if there are no sub-objects) just returns the parent object as a 1-element list.
# both the "Targets" and "Stimuli" sections of the input json file contain complex objects like:
# "Rotation": {"X": 0, "Y": 0, "Z": 0, "W": 0, "IsIdentity": false}
# this function combines the sub-objects (X, Y, Z, W, IsIdentity) with the parent object (Rotation)
def header_name(name):
    if name == 'Rotation':
        return ['RotationX', 'RotationY', 'RotationZ', 'RotationW', 'Isidentity']

    elif name == 'Position':
        return ['PositionX', 'PositionY', 'PositionZ']

    else:
        return [name]


# same as the function header_name but constructs the actual row data
def data_value(name, value):
    if name == 'Rotation':
        return [value['X'], value['Y'], value['Z'], value['W'], value['IsIdentity']]

    elif name == 'Position':
        return [value['X'], value['Y'], value['Z']]

    elif name == 'Intensity':
        return [value['Value']]

    elif name == 'Target':
        if value is None:
            return ['NULL']
        else:
            return [target_name(value)]
    else:
        return [value]


def headers(lst):
    if len(lst) < 1:
        return []

    result = []
    for item in lst[0]:
        result.append(item)
    return result


def values(dictionary):
    if len(dictionary) < 1:
        return []

    result = []
    for key in dictionary:
        result += data_value(key, dictionary[key])
    return result


# main program

if len(sys.argv) < 2:
    print('Usage:')
    print(sys.argv[0] + ' input.json')
    sys.exit()

input_file_name = sys.argv[1]
targets_file_name = input_file_name + '_targets.csv'
stimuli_file_name = input_file_name + '_stimuli.csv'

with open(input_file_name, 'r') as jsonfile:
    data_str = jsonfile.read()
    json_dict = json.loads(data_str)

    target_list = json_dict['Targets']
    target_headers = flatten(map(header_name, headers(target_list)))

    with open(targets_file_name, 'w', newline='') as targets_file:
        targets_writer = csv.writer(targets_file)
        targets_writer.writerow(target_headers)

        for target in target_list:
            target_values = values(target)
            targets_writer.writerow(target_values)

    stimulus_list = json_dict['Stimuli']
    stimuli_headers = flatten(map(header_name, headers(stimulus_list)))
    with open(stimuli_file_name, 'w', newline='') as stimuli_file:
        stimuli_writer = csv.writer(stimuli_file)
        stimuli_writer.writerow(stimuli_headers)

        for stimulus in stimulus_list:
            stimulus_values = values(stimulus)
            stimuli_writer.writerow(stimulus_values)
        

