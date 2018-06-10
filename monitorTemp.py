#!/usr/bin/env python
import os
import glob
import time
import datetime
import csv

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folders = glob.glob(base_dir + '28*')
device_folder = device_folders[0]
device_file = device_folder + '/w1_slave'

id_map= {'28-041720c81bff':'freezer','28-031720194eff':'refrigerator'}

filename = "tempMonitor.csv"
fieldnames = ['time','id','sensor','value']

def gen_path(id):
    #print(os.path.join(base_dir,id))
    return os.path.join(base_dir,id,'w1_slave')

def gen_timestamp():
    return '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

def read_temp_raw(id):
    f = open(gen_path(id), 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(id):
    lines = read_temp_raw(id)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
	

with open(filename,'ab') as csvfile:
    writer = csv.DictWriter(csvfile,fieldnames=fieldnames)

    while True:
        for device_path in device_folders:
            device_id = os.path.basename(device_path)
            
            result = {'time':gen_timestamp(),
                    'id':device_id,
                    'sensor':id_map.get(device_id),
                    'value':read_temp(device_id)[1]}
            #print(gen_timestamp(),device_id,id_map.get(device_id),read_temp(device_id)[1])	
            #print(result)
            writer.writerow(result)
            csvfile.flush()
        time.sleep(1)
        

