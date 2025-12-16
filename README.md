# seizure_detection_device
<h3> About </h3>
This repository comprises the source code to the algorithmic approach for a device detecting epileptic seizures using accelerometry and alerting caregivers in a timely manner via the cloud service AWS IoT Core.
<details>
  <summary><h3>Dependencies</h3></summary>
  <table>
    <tr>
      <td>Dataset</td>
      <td>Epilepsy Time Series Classification Dataset by Villar et al. (2016; n.d.-a)</td>
    </tr>
    <tr>
      <td>Accelerometer</td>
      <td>MPU-6050 Inertial Measurement Unit</td>
    </tr>
  </table>
</details>

<details>
  <summary><h3>Repository Content</h3></summary>
    <ul>
      <li>
        <h4>imu.py</h4>
        Main module that including the classification algorithm and alerting the AWS IoT Core cloud service. It is executed as a Linux systemd service.
      </li>
      <li>
        <h4>sampling.py</h4>
        Optional module to sample and integrate new data in the data set that the machine learning model is trained on (CSV file "TimeSeries_DataFrame.csv"). 
      </li>
      <li>
        <h4>TimeSeries_DataFrame.csv</h4>
        CSV file of the processed data ready to train the machine learning model on.
      </li>
    </ul>
</details>

<h3>References</h3>
Villar, J. R. (n.d.-a). Dataset: Epilepsy. Time Series Classification. [Data set]. https://www.timeseriesclassification.com/description.php?Dataset=Epilepsy <br>
Villar, J. R., Vergara, P., Menéndez, M., de la Cal, E., González, V. M., & Sedano, J. (2016). Generalized Models for the Classification of Abnormal Movements in Daily Life and its Applicability to Epilepsy Convulsion Recognition. Scopus. https://doi.org/10.1142/S0129065716500374
