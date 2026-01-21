import numpy as np
import pandas as pd
from scipy.io import arff
import smbus2
from time import sleep
import math

#empty
DATA_ACCELEROMETER = []

#MPU6050 Registers and Adresses
PWR_MGMT_1 		= 0x6B	#power management register
SMPLRT_DIV 		= 0x19	#sample rate register
CONFIG 			= 0x1A	#configuration register
GYRO_CONFIG 	= 0x1B	#gyroscope configuration register
INT_ENABLE 		= 0x38	#interrupt enable register
ACCEL_XOUT_H 	= 0x3B
ACCEL_YOUT_H 	= 0x3D
ACCEL_ZOUT_H 	= 0x3F
GYRO_XOUT_H 	= 0x43
GYRO_YOUT_H 	= 0x45
GYRO_ZOUT_H 	= 0x47

def MPU_init():
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)	#write to sample rate register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)	#write to power management register
	bus.write_byte_data(Device_Address, CONFIG, 0)		#write to configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)#write to gyroscope config regsiter
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)	#write to interrupt register
	
def read_raw(addr):	#read the 16bit values from the MPU6050 IMU sensor
	high = bus.read_byte_data(Device_Address, addr)
	low = bus.read_byte_data(Device_Address, addr+1)
	value = ((high << 8) | low )
	if (value > 32768):
		value = value - 65536	#sign value
	return value

#give information to fetch data
bus = smbus2.SMBus(1)
Device_Address = 0x68
MPU_init()
print("IMU sensor found. Data is being sampled.")

def save_dataframe(list):
	sampled_df = pd.DataFrame([list])
	print(sampled_df)
	print("Proceed to csv? Type ok or no: ")
	proceed = input()
	if proceed == "ok":
		sampled_df.to_csv('/home/admin/seizure_device/TimeSeries_DataFrame.csv', mode='a', header=False)
	elif proceed == "no":
		exit

try:
	while True:
		#Read Acc data
		acc_x = (read_raw(ACCEL_XOUT_H))/16384.0
		acc_y = (read_raw(ACCEL_YOUT_H))/16384.0
		acc_z = (read_raw(ACCEL_ZOUT_H))/16384.0
		#class float -> gives the G on the IMU
		Xa = round(acc_x, 6)
		Ya = round(acc_y, 6)
		Za = round(acc_z, 6)
		Axm = Xa*9.81
		Aym = Ya*9.81
		Azm = Za*9.81
		invariant = np.sqrt((Xa*Xa) + (Ya*Ya) + (Za*Za))
		mount_invariant = round(invariant, 6)
		print("Invariant:", mount_invariant)
		
		if len(DATA_ACCELEROMETER) == 205:
			print("Sampling completed! Was the activity of type 0 or 1?")
			activity = input()
			if activity == "1":
				DATA_ACCELEROMETER.append(1)
				save_dataframe(DATA_ACCELEROMETER)
			elif activity == "0":
				DATA_ACCELEROMETER.append(0)
				save_dataframe(DATA_ACCELEROMETER)
		else:
			DATA_ACCELEROMETER.append(mount_invariant)
		
		sleep(1/16.0)
except KeyboardInterrupt:
	exit

