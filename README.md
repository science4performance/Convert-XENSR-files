# Convert-XENSR-files
This is Python code to convert XENSR SESH*.DAT files to .GPX format<br>
I have an old XENSR unit that records GPS data and IMU data for my kitesurfing sessions.
Unfortunately the MyXensr website is no longer maintained, so it is not possible to view my data.
However, joriws put some partial Python code up on kitform.com: https://kiteforum.com/viewtopic.php?t=2406619
I have extended this code, so that it now converts XENSR SESH*.DAT files to .GPX format.

- The main code can be run from the command line with the command 
- >python XensrDecoder.py
- Click on the button to select the DAT file
- Click on the convert button to generate a GPX file
- Some sample SESH*.DAT files are provided, one for kitesurfing at Hillhead and on is a bike ride, which I also recorded on my Garmin head unit
- I struggled to interpret the events data 
- I created a test file SESH008.DAT to try to understand the IMU data, but gave up on that
- There are two Jupyter notebooks: one shows my experimentation and the other can be used to test the methods in the python file

