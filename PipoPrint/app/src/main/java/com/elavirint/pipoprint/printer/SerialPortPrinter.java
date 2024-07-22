package com.elavirint.pipoprint.printer;

import android.util.Log;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.LineNumberReader;
import java.util.Iterator;
import java.util.Vector;


/**
 * Created by hansen on 18-1-2.
 */

public class SerialPortPrinter implements Printer {

	private static final String TAG = "SerialPortPrinter";

	private String mPath;
	private int mSpeed;

//	static {
//        try {
//            System.loadLibrary("serialport");
//        } catch (NoClassDefFoundError e) {
//            e.printStackTrace();
//        }
//	}

	/**
	 * @brief
	 *
	 * @param path of the serial port, e.g: /dev/ttyUSB0
	 * @param speed at which to open the serial port, e.g: 115200
	 *
	 * @return 
	 */
	public void selectPrinter(String path, int speed) {
		mPath = path;
		mSpeed = speed;
	}

    @Override
    public void open() throws PrinterException {
		try {
			Log.d(TAG,"open:"+mPath+"@"+mSpeed);
			native_open(mPath, mSpeed);
		} catch (Exception e) {
			e.printStackTrace();
			throw new PrinterException(PrinterCommon.ERR_OPEN);
		}
    }

    @Override
    public void close() throws PrinterException {
		native_close();
    }

    @Override
    public int read(byte[] buf, int len) throws PrinterException {
		int ret = 0;
		try {
			ret = native_read(buf, len);
		} catch (Exception e) {
			e.printStackTrace();
			throw new PrinterException(PrinterCommon.ERR_READ);
		}
		return ret;
    }

    @Override
    public void write(byte[] buf, int len) throws PrinterException {
		try {
			native_write(buf, len);
		} catch (Exception e) {
			e.printStackTrace();
			throw new PrinterException(PrinterCommon.ERR_WRITE);
		}
    }

	@Override
	public int getType() {
		return PrinterCommon.SERIAL_PRINTER;
	}

	private native void native_open(String path, int speed);
	private native void native_close();
	private native int  native_read(byte[] buf, int length);
	private native void native_write(byte[] buf, int length);

	//below code that copy from Google project android-serialport-api(SerialPortFinder.java)
	public class Driver {
		public Driver(String name, String root) {
			mDriverName = name;
			mDeviceRoot = root;
		}
		private String mDriverName;
		private String mDeviceRoot;
		Vector<File> mDevices = null;
		public Vector<File> getDevices() {
			if (mDevices == null) {
				mDevices = new Vector<File>();
				File dev = new File("/dev");
				File[] files = dev.listFiles();
				int i;
				for (i=0; i<files.length; i++) {
					if (files[i].getAbsolutePath().startsWith(mDeviceRoot)) {
						Log.d(TAG, "Found new device: " + files[i]);
						mDevices.add(files[i]);
					}
				}
			}
			return mDevices;
		}
		public String getName() {
			return mDriverName;
		}
	}

	private Vector<Driver> mDrivers = null;

	Vector<Driver> getDrivers() throws IOException {
		if (mDrivers == null) {
			mDrivers = new Vector<Driver>();
			LineNumberReader r = new LineNumberReader(new FileReader("/proc/tty/drivers"));
			String l;
			while((l = r.readLine()) != null) {
				// Issue 3:
				// Since driver name may contain spaces, we do not extract driver name with split()
				String drivername = l.substring(0, 0x15).trim();
				String[] w = l.split(" +");
				if ((w.length >= 5) && (w[w.length-1].equals("serial"))) {
					Log.d(TAG, "Found new driver " + drivername + " on " + w[w.length-4]);
					mDrivers.add(new Driver(drivername, w[w.length-4]));
				}
			}
			r.close();
		}
		return mDrivers;
	}

	public String[] getAllDevices() {
		Vector<String> devices = new Vector<String>();
		// Parse each driver
		Iterator<Driver> itdriv;
		try {
			itdriv = getDrivers().iterator();
			while(itdriv.hasNext()) {
				Driver driver = itdriv.next();
				Iterator<File> itdev = driver.getDevices().iterator();
				while(itdev.hasNext()) {
					String device = itdev.next().getName();
					String value = String.format("%s (%s)", device, driver.getName());
					devices.add(value);
				}
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		return devices.toArray(new String[devices.size()]);
	}

	public String[] getAllDevicesPath() {
		Vector<String> devices = new Vector<String>();
		// Parse each driver
		Iterator<Driver> itdriv;
		try {
			itdriv = getDrivers().iterator();
			while(itdriv.hasNext()) {
				Driver driver = itdriv.next();
				Iterator<File> itdev = driver.getDevices().iterator();
				while(itdev.hasNext()) {
					String device = itdev.next().getAbsolutePath();
					devices.add(device);
				}
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		return devices.toArray(new String[devices.size()]);
	}

}
