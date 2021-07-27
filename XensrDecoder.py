import sys
import struct
import json
from tkinter import *
from tkinter.filedialog import askopenfilename,asksaveasfilename
from tkinter.messagebox import showerror
import tkinter.scrolledtext
import pandas as pd
import pytz
from datetime import datetime, timedelta
from tzwhere import tzwhere


class GPX():
    def __init__(self,file,GPSdf):
        self.saveas = file
        self.df = GPSdf
        return

    def header(self):
        return '<?xml version="1.0"?>\n<gpx xmlns="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd http://www.garmin.com/xmlschemas/PowerExtension/v1 http://www.garmin.com/xmlschemas/PowerExtensionv1.xsd" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" creator="Jorge and Gavin" version="1.1" xmlns:gpxpx="http://www.garmin.com/xmlschemas/PowerExtension/v1">\n<trk>\n<trkseg>\n'
        #return "<gpx version=\"1.1\" creator=\"Jorge and Gavin's Xensr to GPX converter\">\n"

    def footer(self):
        return '</trkseg>\n</trk>\n</gpx>'

    def save(self):
        f = open(self.saveas, "w")
        f.write(self.header())
        for trkpt in  self.df.values:
            f.write(trkpt)
        f.write(self.footer())
        f.close()

class XensrDat():
    def __init__(self,file):
        self.filename=file
        #print ("Open file " + self.filename)
        self.IMURECORD=36
        self.GPSRECORD=24
        self.EVENTRECORD=40
        self.SIGNATURE=152389
        self.GPSDIV=10**7
        self.MICRODIV=10**6
        self.HDSDIV=10**2


    def getHeader(self):
    # header length = 132 bytes, little-endian '<'
    # 4 filetype
    # 2 major version
    # 2 minor version
    # 25 fileid
    # 13 id
    # 12 timestamp (2 year, 2 month, 2 day, 2 hour, 2 min, 2 sec)
    # 7 fillbytes/flags/options (zeroes)
    # 4 imudataoffset
    # 4 imudatabytes
    # 4 gpsdataoffset
    # 4 gpsdatabytes
    # 4 eventdataoffset
    # 4 eventdatabytes
    # 4 iddataoffset
    # 4 iddatabytes
    # 2 numberofevents
    # 2 sportmode (1002 kiteboarding)
    # 4 duration (seconds, divide by 100)
    # 6 timestampbinary
    # 46 padding
        self.header_fmt = '<L 2H 25p 7x 8L 2H L 6B 46x'
        self.header_len = struct.calcsize(self.header_fmt)
        self.header_unpack = struct.Struct(self.header_fmt).unpack_from

        self.header = []

        self.fileHandle = open(self.filename, 'rb')
        data = self.fileHandle.read(self.header_len)
        self.fileHandle.close()

        self.header = self.header_unpack(data)
        if self.header[0] != self.SIGNATURE:
            raise IOError("Unknown file 0x%04x" % self.header[0])
        self.tsepoch = self.decodeXensrTimeStamp()

    def getID(self):
      return self.header[3].decode()

    def getSport(self):
      return int(self.header[13])

    def getDuration(self):
      return (float(self.header[14])/self.HDSDIV)

    def getImuOffset(self):
      return int(self.header[4])

    def getImuBytes(self):
       return int(self.header[5])

    def getImuEntries(self):
      return self.getImuBytes()/self.IMURECORD

    def getGPSOffset(self):
     return int(self.header[6])

    def getGPSBytes(self):
     return int(self.header[7])

    def getGPSEntries(self):
     return self.getGPSBytes()/self.GPSRECORD

    def getEventOffset(self):
     return int(self.header[8])

    def getEventBytes(self):
      return int(self.header[9])

    def getEventEntries(self):
       return int(self.header[12])

    def getJSONOffset(self):
       return int(self.header[10])

    def getJSONBytes(self):
       return int(self.header[11])

    def getJSONData(self):
        self.fileHandle = open(self.filename, 'rb')
        self.fileHandle.seek(self.getJSONOffset(),0)

        self.JSONdata = json.loads(self.fileHandle.read(self.getJSONBytes()).decode())
        self.fileHandle.close()

        return json.dumps(self.JSONdata, sort_keys=True, indent=4)
    #return data

    def convertGPSLongToDegrees(self,value):
      return float(value)/self.GPSDIV

    def convertTimeOffsetToMicro(self,value):
       return float(value)/self.MICRODIV

    def getEvents(self):
    # iterate over filestruct
        self.event_fmt = '<40B'
        self.event_len = struct.calcsize(self.event_fmt)
        self.event_unpack = struct.Struct(self.event_fmt).unpack_from

        self.events = []
        self.fileHandle = open(self.filename, 'rb')
        self.fileHandle.seek(self.getEventOffset(),0)
        data = self.fileHandle.read(self.getEventBytes())
        self.fileHandle.close()

        # iterate over data
        #self.events = data.iter_unpack('<40B',data) ####GF EDIT
        self.events = struct.iter_unpack(self.event_fmt,data)
        #self.header = self.header_unpack(data)

        from pprint import pprint
        pprint(list(self.events))

    def decodeXensrTimeStamp(self):
        self.tsyear = int(self.header[15]+2000)
        self.tsmon = int(self.header[16])
        self.tsday = int(self.header[17])
        self.tshour = int(self.header[18])
        self.tsmin = int(self.header[19])
        self.tssec = int(self.header[20])

        return datetime(self.tsyear,self.tsmon,self.tsday,self.tshour,self.tsmin,self.tssec)

    def getRelativeTimeStamp(self,offset):
       return self.tsepoch + offset

    def headerDebug(self):
    #from pprint import pprint
    #pprint(self.header)
        self.output = []
        self.output.append("Xensr file version %d.%02d " % (int(self.header[1]), int(self.header[2])))
        self.output.append("File ID: %s" % self.getID())
        self.output.append("Sport ID: %d" % self.getSport())
        self.output.append("Base timestamp: %s" % self.tsepoch)
        self.output.append("Duration: %.2fs" % self.getDuration())
        self.output.append("IMU data: 0x%06x - 0x%06x (%d entries)" % (self.getImuOffset(),self.getImuOffset()+self.getImuBytes(), self.getImuEntries()))
        self.output.append("GPS data: 0x%06x - 0x%06x (%d entries)" % (self.getGPSOffset(),self.getGPSOffset()+self.getGPSBytes(),self.getGPSEntries()))
        self.output.append("Event data: 0x%06x - 0x%06x (%d entries)" % (self.getEventOffset(),self.getEventOffset()+self.getEventBytes(),self.getEventEntries()))
        self.output.append("JSON data: 0x%06x - 0x%06x" % (self.getJSONOffset(),self.getJSONOffset()+self.getJSONBytes()))
        self.output.append("\n")
        return self.output


    #def imudata(self):

    #def gpsdataentry(self):
    def getGPSdf(self):
    # 4 timeoffset
    # 4 altitude?
    # 4 latitude * 1e7 
    # 4 longitude * 1e7 
    # 4 speed in m/s /1.5
    # 4 unknown
   
    # iterate over filestruct
        self.gps_fmt = '<6l'
        self.gps_len = struct.calcsize(self.gps_fmt)
        self.gps_unpack = struct.Struct(self.gps_fmt).unpack_from

        self.gps = []
        self.fileHandle = open(self.filename, 'rb')
        self.fileHandle.seek(self.getGPSOffset(),0)
        data = self.fileHandle.read(self.getGPSBytes())
        self.fileHandle.close()

        # iterate over data
        self.gps = struct.iter_unpack(self.gps_fmt,data)
        #self.header = self.header_unpack(data)
        self.GPSdf = pd.DataFrame(self.gps)

    def Remove_Outlier_Indices(self,df):
        Q1 = df.quantile(0.25)
        Q3 = df.quantile(0.75)
        IQR = Q3 - Q1
        return  ~((df < (Q1 - 3 * IQR)) |(df > (Q3 + 3 * IQR)))

    def timezone_offset(self):
        """To comply with GPX standard, local time must be converted to UCT.
        This method runs rather slowly - 4/5 seconds.
        Returns the datetime.timedelta offset that must by deducted to obtain UCT"""
        latitude = self.JSONdata['latitude']
        longitude = self.JSONdata['longitude']
        self.dt = datetime.strptime(self.JSONdata['timestamp'],'%y%m%d%H%M%S')
        
        tzw = tzwhere.tzwhere(forceTZ=True)
        timezone_str = tzw.tzNameAt(latitude, longitude,forceTZ=True)
        timezone = pytz.timezone(timezone_str)
        timezone_aware_datetime = timezone.localize(self.dt, is_dst=None)
        return timezone_aware_datetime.utcoffset()

    
    def processGPSdf(self):
        # Calculate columns and then quantize time
        self.GPSdf = self.GPSdf[self.Remove_Outlier_Indices(self.GPSdf)]
        self.GPSdf['time2'] = self.GPSdf[0]/1e5
        self.tzoffset = self.timezone_offset()
        self.GPSdf['time'] = self.GPSdf['time2'].apply(lambda x: f'{(timedelta(seconds=int(x)) + self.dt - self.tzoffset).isoformat()}Z')
        self.GPSdf['lat'] = self.GPSdf[2]/self.GPSDIV
        self.GPSdf['lon'] = self.GPSdf[3]/self.GPSDIV
        self.GPSdf['ele'] = self.GPSdf[1]/10           # elevation in metres
        #self.GPSdf['speed'] = self.GPSdf[4]/1e7*1.5    # speed in m/s not used
        # quantize time
        self.GPSdf = self.GPSdf.set_index('time2',drop=False)
        seconds = range(int(self.GPSdf.index.max())+1)
        self.GPSdf = self.GPSdf.append(pd.DataFrame(seconds)).sort_index()
        self.GPSdf = self.GPSdf.fillna(method='backfill')
        self.GPSdf = self.GPSdf.loc[seconds]
        # generate GPX format
        self.GPSdf['gpx'] = self.GPSdf.apply(lambda x: f'<trkpt lon="{x.lon}" lat="{x.lat}">\n<ele>{x.ele}</ele>\n<time>{x.time}</time>\n</trkpt>\n',axis=1)
        self.GPSdf = self.GPSdf['gpx']
        

        

    #def eventdata(self):


    def __del__(self):
        self.fileHandle.close()
        print ("Close file " + self.filename)

class MyFrame(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.master.title("Xensr session converter to GPX")
        self.master.rowconfigure(2, weight=1)
        self.master.columnconfigure(3, weight=1)
        self.grid(sticky=W+E+N+S)

        self.button = Button(self, text="Open Xensr SESH.DAT", command=self.load_file)
        self.button.grid(row=1, column=0, sticky=W)

        self.convert = Button(self, text="Convert and save GPX v1.1", state=DISABLED, command=self.save_file)
        self.convert.grid(row=1, column=1, sticky=W)

        self.quit = Button(self, text="Quit", command=self.closeWindow)
        self.quit.grid(row=1, column=2, sticky=E)

        self.text = tkinter.scrolledtext.ScrolledText(self, height=50, width=80)
        self.text.grid(row=2,column=0, columnspan=3, sticky=W)
        self.text.bind('<<Modified>>', self.textModified)
        self.text.edit_modified(False)

    def textModified(self, event):
        self.text.see(END)
        self.text.edit_modified(False)

    def load_file(self):
        fname = askopenfilename(filetypes=(("Xensr session files", ".DAT"),
        ("All files", "*.*") ))
        if fname:
            try:
                #print("""here it comes: self.settings["template"].set(fname)""")
                self.text.insert(END, "Loading: " + fname + "\n")
                self.data = XensrDat(fname)
                self.text.insert(END, "Processing header\n")
                self.data.getHeader()
                self.text.insert(END, "\n".join(self.data.headerDebug()))
                self.text.insert(END, "JSON container:\n" + str(self.data.getJSONData()) + "\n")
                self.text.insert(END, "Processing data..."+ "\n")
                self.data.getGPSdf()
                self.data.processGPSdf()
                self.text.insert(END, "READY to convert"+ "\n")
                
            except IOError as err:
                #showerror("Open Source File", "Failed to read file\n'%s'\n" % fname)
                self.text.insert(END, "IO error: {0}".format(err))
            except OSError as err:
                self.text.insert(END, "OS error: {0}".format(err))
            except:
                print("Unexpected error:", sys.exc_info()[0])

        # enable save button
        self.convert.configure(state=NORMAL)

        return

    def save_file(self):
        # TODO: check if file opened first
        if not self.data.filename: return
        savename = asksaveasfilename(filetypes=(("GPX files", "*.GPX"),
        ("All files", "*.*") ), initialfile=self.data.filename+".GPX")

        if savename:
            try:
                self.text.insert(END,"Saving file: " + savename + "\n")

                self.gpxout = GPX(savename,self.data.GPSdf);
                self.gpxout.save()

                #self.text.insert(END, self.gpxout.header())

                # setup iterator or something to go over wpt-data (events)                
                #self.data.getEvents()
                #for trkpt in self.data.GPSdf.values:
                #    self.text.insert(END, trkpt+ "\n")
                
                #self.text.insert(END, self.gpxout.footer())
                self.text.insert(END, "\n File saved:" +savename + "\n")
            except IOError as err:
                self.text.insert(END, "IO error: {0}".format(err))
            except OSError as err:
               self.text.insert(END, "OS error: {0}".format(err))
            except:
               print("Unexpected error:", sys.exc_info()[0])

        return

    def closeWindow(self):
        self.text.insert(END, "Goodbye\n")
        self.master.title('Close this window')
        #self.destroy() # close this window's buttos
        #self.master.destroy() # remove window
        #sys.exit() # exit

if __name__ == "__main__":
    MyFrame().mainloop()