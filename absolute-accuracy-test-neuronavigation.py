import sys
import xml.etree.ElementTree as ET
import os
import pandas as pd
import time
import numpy as np
import math
import datetime
import shutil

def degree(x):
    pi=math.pi
    degree=(x*180)/pi
    return degree

def tilt(quaternion):
    
    q1 = quaternion[0]
    q2 = quaternion[1]
    q3 = quaternion[2]
    q4 = quaternion[3]
    
    return degree(math.atan2(2*(q1*q4 + q2*q3), 1 -2*(q3**2 + q4**2)))

def rotation(quaternion):
    
    q1 = quaternion[0]
    q2 = quaternion[1]
    q3 = quaternion[2]
    q4 = quaternion[3]

    
    left_side = math.sqrt(q1**2+q2**2+q3**2)
    right_side = q4
    return degree(2*math.atan2(left_side, right_side))
    #return math.atan2(2*(q1*q2 + q3*q4), 1 -2*(q2**2 + q3**2))

def config2dataframe(file_name):
    root = ET.parse(file_name).getroot()
    
    aux = {}

    for children in root: 
        for grandchild in children:
            
            aux[grandchild.attrib.get("name")] = grandchild.text

    return pd.DataFrame(aux, index = [0]).astype('double')

def printusage():
    
    print("Incorrect use of the script")
    print("Correct use: python horizon_accuracy_test.py <json_file_name> <config_file_name>")


def distance(x, y):
    
    return abs(x-y)
    
def Checking_results(df_config, df_targets, df_stimuli):
    
    
    precision_cms = df_config.iloc[0]['Precision_m']
    precision_angle = df_config.iloc[0]['Precision_angle']
    
    measured_param = {}
    
    measured_param['Motor_Position_X'] = df_targets.iloc[0]['PositionX']
    measured_param['Motor_Position_Y'] = df_targets.iloc[0]['PositionY']
    measured_param['Motor_Position_Z'] = df_targets.iloc[0]['PositionZ']
    measured_param['Treatment_Target_Displaced_Position_X'] = df_stimuli.iloc[0]['PositionX'] - df_targets.iloc[0]['PositionX']
    measured_param['Displaced_Position_Y'] = df_stimuli.iloc[1]['PositionY'] - df_targets.iloc[0]['PositionY']
    measured_param['Displaced_Position_Z'] = df_stimuli.iloc[2]['PositionZ'] - df_targets.iloc[0]['PositionZ']
    measured_param['Rotation_Angle'] = rotation(df_stimuli.iloc[3][['RotationX', 'RotationY', 'RotationZ', 'RotationW']]) - rotation(df_targets.iloc[0][['RotationX', 'RotationY', 'RotationZ', 'RotationW']]) 
    measured_param['Tilt_Angle'] = tilt(df_targets.iloc[0][['RotationX', 'RotationY', 'RotationZ', 'RotationW']]) - tilt(df_stimuli.iloc[4][['RotationX', 'RotationY', 'RotationZ', 'RotationW']])
    
    
    output_dict = {}

    for name in df_config.columns[0:8]:
        
        if name.find("Angles") is not -1:
            
            param = measured_param[name]
            specification = df_config.iloc[0][name] 
            dist = distance(param, specification)
            output_dict[name] = [param, specification, dist, abs(distance)<precision_cms]
            
            
        else:
            
            param = measured_param[name]
            specification = df_config.iloc[0][name] 
            dist = distance(param, specification)
            output_dict[name] = [param, specification, dist, abs(dist)<precision_angle]
            
    
    return output_dict

    
def main():
    
    if len(sys.argv)<3:
        printusage()
        
    elif not os.path.exists(sys.argv[1]) or not os.path.exists(sys.argv[2]):
        
        print("Any of the files taken as argument doesn't exits")
    
    else:
            
        json_file = sys.argv[1]
        config_file = sys.argv[2]

        os.system('python lucid2stimguide.py ' + json_file)

        if not os.path.exists('lucid2stimguide_output_files'):
            os.makedirs("lucid2stimguide_output_files")
        
        shutil.move(json_file+"_targets.csv", "lucid2stimguide_output_files/"+json_file+"_target.csv")
        shutil.move(json_file+"_stimuli.csv", "lucid2stimguide_output_files/"+json_file+"_stimuli.csv")

        df_targets = pd.read_csv("lucid2stimguide_output_files/"+json_file+"_target.csv")
        df_stimuli = pd.read_csv("lucid2stimguide_output_files/"+json_file+"_stimuli.csv")
        

        df_config = config2dataframe(config_file)
        df_results = pd.DataFrame(Checking_results(df_config, df_targets, df_stimuli), index=['Measured Values','Expected values', 'Distance', 'Result'])
        
        final_result = df_results.all(axis='columns')[3]
        
        if final_result is np.bool_(True):
            final_result_str = "PASSED"
        else:
            final_result_str = "FAILED"

        
        d = {True: 'PASSED', False: 'FAILED'}


        df_results.iloc[df_results.shape[0]-1]= df_results.iloc[df_results.shape[0]-1].replace(d)
        
        date = datetime.datetime.now().strftime("%Y.%m.%d %H-%M-%S")
        output_file_name = date +"_Absolute_accuracy_test_Neuronavigation_Result="+final_result_str+".csv"

        path = os.path.join(os.path.os.path.dirname(os.path.realpath(__file__)), output_file_name)
        df_results.to_csv(output_file_name, sep = ',',float_format='%.4f')

        print("Test results save successfully under: "+ path)
        

  
if __name__ == "__main__":
    main()
