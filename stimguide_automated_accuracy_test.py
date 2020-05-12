import sys
import xml.etree.ElementTree as ET
import os
import pandas as pd
import time
import numpy as np
import math
import datetime


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
    measured_param['Rotation_Angle'] = rotation(df_stimuli.iloc[2][['RotationX', 'RotationY', 'RotationZ', 'RotationW']]) - rotation(df_targets.iloc[0][['RotationX', 'RotationY', 'RotationZ', 'RotationW']]) 
    measured_param['Tilt_Angle'] = tilt(df_targets.iloc[0][['RotationX', 'RotationY', 'RotationZ', 'RotationW']]) - tilt(df_stimuli.iloc[3][['RotationX', 'RotationY', 'RotationZ', 'RotationW']])
    
    
    output_dict = {}
    
    for name in df_config.columns[0:7]:
        
        if name.find("Angles") is not -1:
            
            param = measured_param[name]
            specification = df_config.iloc[0][name] 
            dist = distance(param, specification)
            output_dict[name] = [param, dist, abs(distance)<precision_cms]
            
            
        else:
            
            param = measured_param[name]
            specification = df_config.iloc[0][name] 
            dist = distance(param, specification)
            output_dict[name] = [param, dist, abs(dist)<precision_angle]
            
    
    return output_dict
    
def main():
    
    if len(sys.argv)<3:
        printusage()
        
    else:
            
        json_file = sys.argv[1]
        config_file = sys.argv[2]

        os.system('python lucid2stimguide.py ' + json_file)
        
        #time.sleep(5)
        
        df_targets = pd.read_csv(json_file+"_targets.csv")
        df_stimuli = pd.read_csv(json_file+"_stimuli.csv")
        

        df_config = config2dataframe(config_file)
        df_results = pd.DataFrame(Checking_results(df_config, df_targets, df_stimuli))
        
        final_result = df_results.all(axis='columns')[2]
        
        if final_result is np.bool_(True):
            final_result_str = "PASSED"
        else:
            final_result_str = "FAILED"

        
        mask = df_results.applymap(type) == bool
        d = {True: 'PASSED', False: 'FAILED'}
        
        df_results = df_results.where(mask, df_results.replace(d))
        
        date = datetime.datetime.now().strftime("%Y-%m-%d %X")
        output_file_name = date + "- STIMGUIDE AUTOMATED ACCURACY TEST RESULT: "+final_result_str+".csv"
        
        df_results.to_csv(output_file_name, sep = ',',float_format='%.4f', index=False)
        
        print("Test results save successfully under: "+ 
              os.path.dirname(os.path.realpath(__file__))+"/"+ output_file_name)
        

  
if __name__ == "__main__":
    main()

    
