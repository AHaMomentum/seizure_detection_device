#SECTION ONE
import smbus2
import json
import numpy as np
import pandas as pd
from time import sleep
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from imblearn.over_sampling import BorderlineSMOTE

df_csv = pd.read_csv('/home/admin/seizure_device/TimeSeries_DataFrame.csv')                                             #import the csv data set as dataframe
df_TimeSeries = df_csv.drop(df_csv.columns[0], axis=1)                                                                  #drop one index to prevent the first index to be read as column

#SECTION TWO
DATA_ACCELEROMETER = []                                                                                                 #list wo be used in first sliding window
COUNTER = []                                                                                                            #list to be used in second sliding window
SEND_ALERT = False                                                                                                      #variable decides if seizure alert is sent
# MPU6050 Registers and Adresses
PWR_MGMT_1 = 0x6B                                                                                                       #power management register
SMPLRT_DIV = 0x19                                                                                                       #sample rate register
CONFIG = 0x1A                                                                                                           #configuration register
GYRO_CONFIG = 0x1B                                                                                                      #gyroscope configuration register
INT_ENABLE = 0x38                                                                                                       #interrupt enable register
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47
# Set AWS ENDPOINT, CERTIFICATES AND TOPICS
ENDPOINT = "a4edo4tnhltxs-ats.iot.eu-central-1.amazonaws.com"
CLIENT_ID = "arn:aws:iot:eu-central-1:154514163632:thing/Seizure_monitor"
PATH_TO_CERTIFICATE = "/home/admin/certificates/certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "/home/admin/certificates/private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "/home/admin/certificates/AmazonRootCA1.pem"
MESSAGE = "seizure_prediction"
TOPIC = "seizure_alert"

#SECTION THREE
def mpu_init(): 
    """ 
    Initializes the registers and the MPU-6050.  
    Arguments:
    none
    """
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)  # write to sample rate register                                 #use a regular sample speed (manually decreased by code)
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)  # write to power management register                            #use the regular power mode
    bus.write_byte_data(Device_Address, CONFIG, 0)  # write to configuration register
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)  # write to gyroscope config regsiter
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)  # write to interrupt register

def read_raw(addr): 
    """ 
    Reads the 16bit binary values from the IMU 
    Arguments:
    addr: The register address to be read out 
    """
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr + 1)
    value = ((high << 8) | low)
    if (value > 32768):
        value = value - 65536                                                                                           #sign the value if needed
    return value

def write_service():
    """ 
    Writes to text file whenever the systemd service is started and run
    Arguments:
    none
    """
    with open("/home/admin/seizure_device/service.txt", "w") as text:
        print(f"Service started.", file=text)

#SECTION FOUR
bus = smbus2.SMBus(1)                                                                                                   #configures i2c bus 1 to be addressed
Device_Address = 0x68                                                                                                   #configures device 0x68 to be addressed
mpu_init()                                                                                                              #MPU intialization
print("IMU sensor found. Start building random forest classifier.")
write_service()                                                                                                         #write to text

X = df_TimeSeries.drop(['activity'], axis=1)                                                                      #X are the net acceleration features
y = df_TimeSeries["activity"]                                                                                           #y is the activity target
bsmote = BorderlineSMOTE(random_state=42, kind='borderline-2')                                                          #initializing boderlineSMOTE, randomstate allows reproduction
X_bd, y_bd = bsmote.fit_resample(X, y)                                                                                  #resampling X, y with SMOTE
train_X, test_X, train_y, test_y = train_test_split(X_bd, y_bd, test_size=0.3, random_state=42)                  #randomly spitting the resampled data into train & test data
model = RandomForestClassifier(random_state=42, bootstrap=False)                                                        #initializing the Random Forest Classifier
model.fit(train_X, train_y)                                                                                             #fit RFC on training data
pred_y = model.predict(test_X)                                                                                          #make prediction on test data X
print("Accuracy: ", model.score(test_X, test_y))                                                                        #get the accuracy of the model
cm = confusion_matrix(test_y, pred_y)                                                                                   #compute the confusion matrix of the model
print(cm)
class_report = classification_report(test_y, pred_y)                                                                    #get the classification report of the model
print("Classification report: ", class_report)

#SECTION FIVE
try:
    print("Random Forest Classifier successfully build. Connecting to AWS.")                                                #Establish mqtt connection with AWS IoT Core
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,                                                                                                  #Get the global variables declared above
        cert_filepath=PATH_TO_CERTIFICATE,
        pri_key_filepath=PATH_TO_PRIVATE_KEY,
        client_bootstrap=client_bootstrap,
        ca_filepath=PATH_TO_AMAZON_ROOT_CA_1,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=240,
    )
    print("Connecting to {} with client ID '{}'...".format(ENDPOINT, CLIENT_ID))
    connect_future = mqtt_connection.connect()
    connect_future.result()
    print("Connected!")
    print('Begin Publish')
except:
    print("Connection failed!")

#SECTION SIx
try:
    while True:
        acc_x = (read_raw(ACCEL_XOUT_H)) / 16384.0                                                                      #Read out signed 16-bit values from accelerometer and
        acc_y = (read_raw(ACCEL_YOUT_H)) / 16384.0                                                                      #transform them into alphanumerical values
        acc_z = (read_raw(ACCEL_ZOUT_H)) / 16384.0
        Xa = round(acc_x, 6)                                                                                            #Xa, Ya, and Za are the linear accelerations in measured in g
        Ya = round(acc_y, 6)                                                                                            #The acceleration in m/s^2 can be calculated by Xa * 9.8,
        Za = round(acc_z, 6)                                                                                            #Ya * 9.81 and Za * 9.81.
        mount_invariant = np.sqrt((Xa * Xa) + (Ya * Ya) + (Za * Za))                                                    #Calculation of the net acceleration/magnitude to obtain the
        invariant = round(mount_invariant, 6)                                                                           #mounting invariant
        DATA_ACCELEROMETER.append(invariant)                                                                            #Append to the first global list

        window = []
        process_list = False                                                                                            #true when enough elements in sliding window to be 205 features required for RFC.
        if len(DATA_ACCELEROMETER) <= 205:                                                                              #less than the expected input features
            process_list = False
            pass
        for i in range(len(DATA_ACCELEROMETER) - 205 + 1):                                                              #if enough elements in sliding window
            window = DATA_ACCELEROMETER[i:i + 205]                                                                      #move sliding window one element to the right
            process_list = True                                                                                         #set process_list true to make predictions on the sliding window
        if process_list == True:
            array_input = np.array([window])                                                                            #turn current sliding window into numpy array
            new_prediction = model.predict(array_input.reshape(1, -1))                                                  #reshape array into two-dimensional array and make prediction
            probability = model.predict_proba(array_input.reshape(1, -1))                                               #compute probabilities for the prediction
            COUNTER.append(new_prediction[0])                                                                           #append the prediction to the second global list

        prediction_sum = 0
        if len(COUNTER) <= 240:                                                                                         #240 / 0.0625 = 15. 15 second windows
            pass                                                                                                        #less than 15 seconds
        for j in range(len(COUNTER) - 240 + 1):                                                                         #enough elements in the sliding window
            last_predictions = COUNTER[j:j + 240]                                                                       #move window one element to the right
            prediction_sum = sum(last_predictions)                                                                      #get sum of window
        if prediction_sum >= 10:                                                                                        #prediction sum >10 --> seizure activity
            print("Seizure alert!")
            if SEND_ALERT == False:                                                                                     #If the send_alert var is False, an SMS is triggered
                print("Send message")
                data = 1
                message = {MESSAGE: data}                                                                               #this is sent to the mqtt broker in AWS IoT Core
                mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)           #publish to AWS IoT Core
                print("Published: '" + json.dumps(message) + "' to the topic: " + "'seizure_alert'")                    #confirm publishing
                SEND_ALERT = True                                                                                       #Set send_alert var True to prevent resending SMS for same seizure
            if SEND_ALERT == True:                                                                                      #seizure has already been reported, do nothing
                pass
        elif prediction_sum <= 9:                                                                                       #if prediction sum < 10, false-positive errors are assumed.
            SEND_ALERT = False
        sleep(1 / 16.0)                                                                                                 #16Hz = 1/16.0 seconds = 0.0625 seconds
except KeyboardInterrupt:
    exit                                                                                                                #If Ctrl+C, program is exited
