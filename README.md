# Convert-XENSR-files
## This is Python code to convert XENSR SESH*.DAT files to .GPX format
I have an old XENSR unit that records GPS data and IMU data for my kitesurfing sessions.
Unfortunately the MyXensr website is no longer maintained, so it is not possible to view my data.
However, joriws put some partial Python code up on kitform.com: https://kiteforum.com/viewtopic.php?t=2406619
I have extended this code, so that it now converts XENSR SESH*.DAT files to .GPX format. Jumps as recorded as waypoints that show up when visualized.
- You can use a website, such as https://www.gpsvisualizer.com/ to view the resulting file
![alt text](https://github.com/science4performance/Convert-XENSR-files/blob/main/Plot.png)

## Run the code
- The main code can be run from the command line with the command 
- >python XensrDecoder.py
![alt text](https://github.com/science4performance/Convert-XENSR-files/blob/main/Window.png)
- Click on the button to select the DAT file
- Click on the convert button to generate a GPX file
- Some sample SESH*.DAT files are provided, one for kitesurfing at Hillhead and on is a bike ride, which I also recorded on my Garmin head unit
- Jumps are recorded as waypoints in the GPX file 
- There is  a Jupyter notebook: showing some experimentation 

