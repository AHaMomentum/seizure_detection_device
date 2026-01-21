# seizure_detection_device
<h2> About </h2>
This repository comprises the source code to the algorithmic approach for a device detecting epileptic seizures using accelerometry and alerting caregivers in a timely manner via the cloud service AWS IoT Core.

<h2>Installation</h2>
Preconditions: 
<table>
  <tr>
    <td>Dataset</td>
    <td>Epilepsy Time Series Classification Dataset by Villar et al. (2016; n.d.-a)</td>
  </tr>
  <tr>
    <td>Cloud service subscription</td>
    <td>AWS IoT Core</td>
  </tr>
  <tr>
    <td>Accelerometer</td>
    <td>MPU-6050 Inertial Measurement Unit</td>
  </tr>
  <tr>
    <td>CPU</td>
    <td>Raspberry Pi Zero 2 W</td>
  </tr>
  <tr>
    <td>Python interpreter</td>
    <td>Pythonv3.8 or newer</td>
  </tr>
</table>
<ul>
  <li>Configure the Raspberry Pi Zero 2 W device as an <a href=https://docs.aws.amazon.com/iot/latest/developerguide/connecting-to-existing-device.html>AWS IoT Core thing</a></li>
  <li>Create folder "certficates" in the path /home/admin/... and place your AWS IoT Core credentials in said folder</li>
  <li>Copy this repository in the path /home/admin/..., by downloading manually or<a href=https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository> cloning with git</a></li>
  <li>Download the Dateset:Epilepsy by Villar et al. to the path /home/admin/seizure_device/... and name it "Epilepsy_Dataset"</li>
</ul>

<h2>Repository Content</h2>
<ul>
  <li><h4><a href=imu.py>imu.py</a></h4>
    Main module that including the classification algorithm and alerting the AWS IoT Core cloud service. It is executed as a Linux systemd service.</li>
  <li><h4><a href=preprocessing.py>preprocessing.py</a></h4>
    Processes the Dataset: Epilepsy by Villar et al. into a CSV file "TimeSeries_DataFrame.csv" to train the machine learning model.</li>
  <li><h4><a href=sampling.py>sampling.py</a></h4>
    Optional module to sample and integrate new data in the CSV file "TimeSeries_DataFrame.csv".</li>
</ul>

<h3>References</h3>
Villar, J. R. (n.d.-a). Dataset: Epilepsy. Time Series Classification. [Data set]. https://www.timeseriesclassification.com/description.php?Dataset=Epilepsy <br>
Villar, J. R., Vergara, P., Menéndez, M., de la Cal, E., González, V. M., & Sedano, J. (2016). Generalized Models for the Classification of Abnormal Movements in Daily Life and its Applicability to Epilepsy Convulsion Recognition. Scopus. https://doi.org/10.1142/S0129065716500374
