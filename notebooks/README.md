WQP Processing
==============

The standard workflow for the processing of the satellite image to obtain the WQPs estimates accounts for the order as shown next:

1. `downloadMeteoARPA.ipynb`: Retrieval and storage of the temperature measurements from an in-situ sensor of the meteorological network of ARPA Lombardia.
2. `downloadWEkEO.ipynb`: Request the Sentinel-3 images through the [Harmonized Data Access API](https://www.wekeo.eu/docs/harmonised-data-access-api) from WEkEO.
3. `WQP_Production.ipynb`: Production of the WQP maps
4. `WQP_Coregistration.ipynb`: Coregistration of the WQP maps from the Sentinel-3 satellite images
5. `WQP_Statistics.ipynb`: Computation of the descriptive statistics of the WQPs for each lake
6. `WQP_istSOS.ipynb`: Upload the retrieved descriptive statistics into the istSOS platform