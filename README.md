# TCS_scanline_visualizer: A Python script for Thermal Conductivity Scanline visualisation
The Thermal Conductivity and Diffusivity Scanner (TCS) is an optical device that is used to determine thermal conductivity (TC) and diffusivity(TD)  of cut samples (cores or raw samples). This python script is developed to visualize raw TCS scanlines of consecutive sample scans.  

# Thermal conductivity and diffusivity scanner (TCS)
The thermal conductivity and diffusivity scanner (TCS) is an optical scanning method developed by Popov et al. (1983, 1985). The advantages of using a TCS are the high speed of operation, contactless mode of measurement, independence of the constraints for sample size and shape (including cylindrical samples), the ability to record variation of TC along the sample and the ability to deduce 3D anisotropy if the sample preparation is well understood.

![alt text](https://github.com/KoenVanNoten/TCS_scanline_visualizer/blob/master/TCS%20scanner.JPG)

The TCS consists of a flat platform, a movable device with an optical head with a heat source and three infrared sensors, multiple set of standards. The TCS software (LGM LIPPMAN) drives the movement of the TCS. The flat platform has a 2 cm-wide slit in the middle, on which samples and standards are placed. The optical head moves parallel to the slit, under the sample and standards, with a focused and continuously operated optical heat source and two IR temperature sensors at a constant distance to each other. While the optical head is moving below the standards and sample(s), the TCS software registers the measured temperatures of the cold sensor before heating (initial room temperature, TCold) and the temperature after heating (Thot) and displays them on the computer screen. 
For TD measurements, a third sensor is used that is positioned at a distance of 0.7 mm next to the hot sensor and which measures also the temperature after heating but at a position (SHy in Figure 32) parallel to the line hot sensor – heat source – cold sensor enabling to calculate the thermal diffusivity.

Depending on the speed of the motor, different sample resolutions can be obtained. At a 0.5 mm/s and at 1 mm/s speeds, the TCS samples a temperature (and thus TC) point every millimetre. Increasing the motor speed up to 2 mm/s decreases the spatial resolution up to 1.5 mm. To obtain the highest resolution, it is advied to use the slowest speed (0.5 mm/s). The TCS hence accurately samples temperature values at mm resolution making it possible to study and isolate layering, inhomogeneities and mineral layers. At each detection point, the difference between hot and cold temperatures below the standards and the sample is computed and is used for TC computation. It is advised to use those standards of which the TC approximates as closely as possible that of the sample. 

# A Python script for scanline visualisation
If a sample is scanned using a LGM LIPPMAN TCS with the TCS software, each TC (using the TC mode) and TD (using the TD mode) scan generates a text file in which following information is stored:
- both the cold and the warm temperature profiles measured by the two sensors;
- position of the sensors when they are measuring these temperatures;
- TC variation along the scanline between the Start and End position;
- the temperature profile of the second hot sensor used for TD measurement;
- the TD variation along the scanline between the Start and End position.

To optimise the visualisation of TC variability along a scanline, a python script was developed that generates a figure computed from three consecutive TC and TD measurements (at least 3 scans are necessary to obtain a solid mean). The generated figure illustrates the temperature profiles, the TC variation along the sample using the TC mode, and the TC and the TD variation along the sample using the TD mode. The mean TC and TD values are computed from the raw data and represent the mean TC value between the Start and End position. The modus is the TC/TD value that corresponds to the maximum of the cumulative distribution of the three scanlines.

# Caption to the generated figure
Title: editable; 

SC: temperature profile of the cold sensor; SH: temperature profile of the hot sensor; SHy: temperature profile of the second hot sensor used for TD measurements. 

#x.1 to# x.3: scanlines using the TC mode; #x.4 to x.6: scanlines using TD mode. 

The upper TC plot illustrates the TC variation along the scanline using the TC mode. The second TC plot and the TD plot are computed using the TD mode. Mean TC and TD values (blue line) are computed for each scanline and mean of three scanlines is indicated. Histograms illustrate the weighted (total sum = 1) cumulative distributions of TC and TD values. Maximum of the distribution is indicated as the modus (red line). 

![alt text](https://github.com/KoenVanNoten/TCS_scanline_visualizer/blob/master/084W1478%20-%20178.20%20-%2012-TC-TD.png)
