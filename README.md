# VDIF File Processor Instructions for Use

## Purpose 
This program is a set of python modules which can be used for conducting RADAR signal processing with vdif files, commonly used for RADAR astronomy. 

Particularly, this program can plot/print single-threaded vdif data as long as it is continuous, plot the spectral and waterfall plots, conduct auto-correlation and match filtering (for Linear Frequency Modulated Continuous Wave signals), and compensate for a changing return trip time using a PREDIX file.  

## Requirements
See the dependencies for this program in the requirements.txt file. Other versions of these libraries will probably work, but only the listed versions have been tested. You will also need a VDIF to analyse (can be constructed using the in-program VDIF file builder).

In case you want to do any of the doppler compensation/ simulation, a PREDIX file is required for the observation, with a column labelled RTT which contains the return trip time information.

## Steps

- Clone the repository to your device with `https://github.com/NoahTunesLaunchpadYT/VDIF-File-Processor.git`
- Paste the vdif file and PREDIX file (if applicable) into the root directory of the program for easy use.
- Run either main_UI.py, or main_script.py

### main_UI.py 
- Follow the prompts by typing commands into the terminal after running the prgram.

### main_script.py
- Use the main function to build and analyse vdif files according to a script.

## main_UI.py Examples
### Scenario 1, reading a vdif file

You have a vdif file and you want to know its contents.

You place a vdif file in the root directory of the program. You run main_ui.py. You get the following output. 
![image](https://github.com/user-attachments/assets/d39b0963-5d15-4e71-9e08-17763f606f44)
You type in `analyser` and see the avaialble vdif files,
![image](https://github.com/user-attachments/assets/e66e564d-ee7e-47a4-a01d-3c9cc5fab936)
You type `1` the index of the file you wish to process, 
![image](https://github.com/user-attachments/assets/a2d6ac99-cdd7-4797-8bf4-edc8ea8858b1)
You type `help` and see the following options,
![image](https://github.com/user-attachments/assets/b88a4844-c067-46a2-bcfa-fcfd2df1881f)
You type is_simple to verify that the file is simple as defined in the VDIF manual, (https://vlbi.org/wp-content/uploads/2019/03/VDIF_specification_Release_1.1.1.pdf). The output should look like, 
![image](https://github.com/user-attachments/assets/5970d830-87b5-435f-ac9e-6d6b228659d9)
NOTE: if the file is not simple, then the program will not function correctly
You can also type `properties` to see important properties of the file.
![image](https://github.com/user-attachments/assets/dda3f929-f34d-4b47-b107-eec822028cdf)
In our case, the VDIF file has a sample rate of 8 MHz, has 1 ms frames, and goes from 5:40 to 6:50 on 29-06-2025. 
The data in a vdif file can be printed/plotted with `print` and `plot`. These commands and many others will require a time range to be specified. Time ranges can be specified as seconds since epoch, or datetimes in format YYYY-MM-DD HH:MM:SS.sss.
![image](https://github.com/user-attachments/assets/f71b4f48-6331-45f6-889f-34f7d080677a)
Any function that involes plotting will display the graph and save it as a png to `plots/`

### Scenario 2, Create a synthetic vdif file with the vdif builder and a PREDIX file, 

You want to, for testing purposes, create a synthetic signal modelling the received signal of an reflected Linear FM CW transmission.
THe doppler effect will be modeled using the RTT column of a PREDIX file. 

You place a PREDIX file in the root directory of the program. You run main_ui.py. You get the following output. 
![image](https://github.com/user-attachments/assets/d39b0963-5d15-4e71-9e08-17763f606f44)
You type in `builder` and `help` to see the available commands
![image](https://github.com/user-attachments/assets/3e7a93df-6c69-4032-8d11-2f8bc19c1788)
If your predix file ahs multiple telescopes in it, use split_predix_file to split the file into one PREDIX file per telescope. 
You plot your telescope's PREDIX file to check that it is valid. Each of the columns will be printed. They must be numerical. 
![image](https://github.com/user-attachments/assets/7cc1f92d-e31f-4bb6-96b3-a9f9f7af439b)
![image](https://github.com/user-attachments/assets/88da1194-d4c4-44a7-a39a-10005edb45ae)
You type generate_vdif, which generates a vdif file based off specified parameters, and the RTT column of a PREDIX file
![image](https://github.com/user-attachments/assets/11705738-014d-4db6-8ce8-9f07954c9b7c)
After some loading the file should be ready of analysis
![image](https://github.com/user-attachments/assets/8c2c3aef-08bb-46a7-b205-8ba2e0c637e4)

### Scenario 3, Deramping real/synthetically generate VDIF files of Linear FM CW Radar

Using a similar process to scenario 1, load up the analyser with the vdif file to analyse, the program currenly assumes that the period of the Linear FM CW is 25 us, but that can be fix but finding the number in code and changing it. Type in auto_correlate to correlate the signal with itself. The graph below describes the equations used to do the matching. 
![image](https://github.com/user-attachments/assets/e7f1374d-90a9-4ef4-966c-c95f97f75e8d) a fast time vs slow time plot will also be generated. 
![image](https://github.com/user-attachments/assets/97d70ce4-1cc9-42dc-8455-18b87a9b824c)
Note that there are multiple lines in the plot for the same slow time value, that's due to the fact that the auto correlate is lining up with itself well in 2 positions, due to the nature of how the number of chirps in the duration of the sample isn't an integer. Despite the RTT changing, it is approximately changing linearly, causing the auto_matching to be strong. If `correlate_chirp` was used, then the signal wouldn't be correlated with itself, but with a user specified chirp signal. 
![image](https://github.com/user-attachments/assets/f84329f5-b2b0-4b75-bbce-688226f4e5a9)
Notice also that the line isn't perfectly verticle, this is due to the doppler effect. The match doesn't occur at the same time in each 25 us window because the return trip time is decreases, meaning the matches are happening earlier and earlier. To compensate for this, we can use the PREDIX file's RTT column in the same way we did in Scenario 2. The command that does this for us is "correlate_chirp_shifted", which gives us the following. 
![image](https://github.com/user-attachments/assets/c0ccd14f-a5ff-46c2-af25-89dbcd23f0a9)
The spike in the long time integration indicates that an object has reflected the transmitted signal. The process is very robust against noise. If the result is too noisy integrate over a longer time. 

Call 0421286031, email noahswest@icloud.com, or make an issue/pr to reach me. 

