# ![Logo](https://github.com/FloEll/CWSI/blob/main/icon.png) CWSI plugin for QGIS 3

This is a small description of this very simple plugin to calculate the crop water stress index (CWSI) from thermal images of land surface temperatures. 

This plugin is still experimental and if you find bugs or if you have suggestions to improve this plugin please contact me!
Running the CWSI plugin:

# 1. minimum requirements:

To run the CWSI plugin you'll need an image or a map with land surface temperatures e.g. of a field with crops. This image can be recorded by satellite, plane, drone or by a handheld thermal camera. If you are new to thermography: you can also simply download thermal images from various sources. The image should be a one/single band .tif image and each pixel should represent a temperature measurement. The temperatures can be recorded in Kelvin or °C since the plugin is automatically going to convert it to °C.
You'll further have to define an output raster in a location where you want to store your output (e.g. your Desktop) and also for your output file. The output raster is automatically loaded into your QGIS project after the CWSI has been calculated. The output file contains statistics and model values.
The CWSI calculaton is based on equation 9.6 from:
Jones, H. G., 1992. Plants and microclimate, 2nd ed.: Cambridge University Press, Cambridge, UK.

# 2. optional input of field measurements:

If you measured the temperature of a wet and dry surface you can also input that in the Twet and Tdry box respectively. Please use a °C format and input the temperatures as an integer e.g 23 or as a float e.g. 23.0 without a unit (°C or so). 
If you don't have measurements of Trdy and Twet you can also use measurements of air temperature Tair. Tair is then increased by a default value of 5 °C following a workflow decribed here:
Irmak, S. Haman, D. Z., Bastug, R. 2000. Determination of crop water stress index for 
irrigation timing and yield estimation of corn. Agronomy Journal 92


Press 'OK' to run the CWSI plugin. 











