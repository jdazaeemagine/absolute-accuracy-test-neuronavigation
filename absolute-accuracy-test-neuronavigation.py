import sys
import xml.etree.ElementTree as ET
import os
import pandas as pd
import time
import numpy as np
import math
import datetime
import shutil


# Convert the angles from radians to degrees
def degree(x):
    pi = math.pi
    degree = (x * 180) / pi
    return degree


# Calculate the tilt deviation of the coil from
# the quaternion vector (RotationX, RotationY, RotationZ, Rotation W)
def tilt(quaternion):
    q1 = quaternion[0]
    q2 = quaternion[1]
    q3 = quaternion[2]
    q4 = quaternion[3]

    return degree(math.atan2(2 * (q1 * q4 + q2 * q3), 1 - 2 * (q3 ** 2 + q4 ** 2)))


# Calculate the rotation deviation of the coil from
# the quaternion vector (RotationX, RotationY, RotationZ, Rotation W)
def rotation(quaternion):
    q1 = quaternion[0]
    q2 = quaternion[1]
    q3 = quaternion[2]
    q4 = quaternion[3]

    left_side = math.sqrt(q1 ** 2 + q2 ** 2 + q3 ** 2)
    right_side = q4
    return degree(2 * math.atan2(left_side, right_side))
    # return math.atan2(2*(q1*q2 + q3*q4), 1 -2*(q2**2 + q3**2))


# Getting as input the name of the file, Convert the .xml config file into a pandas dataframe.
# Each column of this dataframe contains a specific parameter
def config2dataframe(file_name):
    root = ET.parse(file_name).getroot()

    aux = {}

    for children in root:
        for grandchild in children:
            aux[grandchild.attrib.get("name")] = grandchild.text

    return pd.DataFrame(aux, index=[0]).astype('double')


# When the script is not called properly, this message will pop up on the terminal window.
def printusage():
    print("Incorrect use of the script")
    print("Correct use: python horizon_accuracy_test.py <json_file_name> <config_file_name>")


# Calculate the absolute distance between two values
def distance(x, y):
    return abs(x - y)


# Receives as input the config, targets and stimuli dataframe.
# In a dictionary will store
# [measured values, expected values,
# distance between measured and expected values, Results (if it is above the threshold or not)]
# sorted by name of the value
def checking_results(df_config, df_stimuli):

    precision_ms = df_config.iloc[0]['Precision_m']
    precision_angle = df_config.iloc[0]['Precision_angle']

    measured_param = {}

    measured_param['Initial_Position_X'] = df_stimuli.iloc[0]['PositionX']
    measured_param['Initial_Position_Y'] = df_stimuli.iloc[0]['PositionY']
    measured_param['Initial_Position_Z'] = df_stimuli.iloc[0]['PositionZ']
    measured_param['Displaced_Position_X'] = df_stimuli.iloc[1]['PositionX'] - df_stimuli.iloc[0]['PositionX']
    measured_param['Displaced_Position_Y'] = df_stimuli.iloc[2]['PositionY'] - df_stimuli.iloc[0]['PositionY']
    measured_param['Displaced_Position_Z'] = df_stimuli.iloc[3]['PositionZ'] - df_stimuli.iloc[0]['PositionZ']
    measured_param['Rotation_Angle'] = rotation(df_stimuli.iloc[4][['RotationX', 'RotationY', 'RotationZ', 'RotationW']]) \
                                       - rotation(df_stimuli.iloc[0][['RotationX', 'RotationY', 'RotationZ', 'RotationW']])
    measured_param['Tilt_Angle'] = tilt(df_stimuli.iloc[0][['RotationX', 'RotationY', 'RotationZ', 'RotationW']]) \
                                   - tilt(df_stimuli.iloc[5][['RotationX', 'RotationY', 'RotationZ', 'RotationW']])

    output_dict = {}

    for name in df_config.columns[0:8]:

        if "Angle" not in name:

            param = measured_param[name]
            specification = df_config.iloc[0][name]
            dist = distance(param, specification)
            output_dict[name] = [param, specification, dist, dist < precision_ms]

        else:

            param = measured_param[name]
            specification = df_config.iloc[0][name]
            dist = distance(param, specification)
            output_dict[name] = [param, specification, dist, dist < precision_angle]

    return output_dict

# Execute internally the script lucid2stimguide.py and will move the files created
# to a folder named lucid2stimguide_output_files. Then, will return the dataframe corresponding
# to the stimulus .csv file
def json2dataframe(json_file):

    os.system('python lucid2stimguide.py ' + json_file)

    if not os.path.exists('lucid2stimguide_output_files'):
        os.makedirs("lucid2stimguide_output_files")

    shutil.move(json_file + "_targets.csv", "lucid2stimguide_output_files/" + json_file + "_target.csv")
    shutil.move(json_file + "_stimuli.csv", "lucid2stimguide_output_files/" + json_file + "_stimuli.csv")

    return pd.read_csv("lucid2stimguide_output_files/" + json_file + "_stimuli.csv")


# final result of the test (PASSED OR FAILED) as AND operation of partial results
def final_result_string(df_results):

    final_res = df_results.all(axis='columns')[3]

    if final_res is np.bool_(True):
        return "PASSED"
    else:
        return "FAILED"

# Map boolean values with Passed or Failed
def map_boolean(df_results):

    d = {True: 'PASSED', False: 'FAILED'}
    df_results.iloc[df_results.shape[0] - 1] = df_results.iloc[df_results.shape[0] - 1].replace(d)
    return df_results


def main():
    # Check if two arguments were given
    if len(sys.argv) < 3:
        printusage()

    elif not os.path.exists(sys.argv[1]) or not os.path.exists(sys.argv[2]):

        print("Any of the files taken as argument doesn't exits")

    else:

        data_file = sys.argv[1]
        config_file = sys.argv[2]

        # Check if file is a .json file (coming from Horizon API)
        # Or if file is a .csv file(coming from Visor2 System)
        if ".json" in data_file:

            df_stimuli = json2dataframe(data_file)

        elif ".csv" in data_file:

            df_stimuli = pd.read_csv(data_file)

        # Config xml file to dataframe
        df_config = config2dataframe(config_file)

        # Final results given obtained by Checking_results script
        df_results = pd.DataFrame(checking_results(df_config, df_stimuli),
                                  index=['Measured Values', 'Expected values', 'Distance', 'Result'])

        # Global result string of the test
        final_result_str = final_result_string(df_results)

        # df_results mapped
        df_results = map_boolean(df_results)

        # Save results on csv using a specific name given by the date and the global result
        date = datetime.datetime.now().strftime("%Y.%m.%d %H-%M-%S")
        output_file_name = date + "_Absolute_accuracy_test_Neuronavigation_Result=" + final_result_str + ".csv"

        path = os.path.join(os.path.os.path.dirname(os.path.realpath(__file__)), output_file_name)
        df_results.to_csv(output_file_name, sep=',', float_format='%.4f')

        print("Test results save successfully under: " + path)


if __name__ == "__main__":
    main()
