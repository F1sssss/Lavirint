package com.elavirint.pipoprint.printer;

import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbDeviceConnection;
import android.hardware.usb.UsbEndpoint;
import android.hardware.usb.UsbInterface;
import android.hardware.usb.UsbManager;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;

/**
 * Created by hansen on 18-1-2.
 */

public class UsbPrinter implements Printer {

    public static final String ACTION_USB_PERMISSION = "ACTION_USB_PRINTER_PERMISSION";

	private final Context mContext;
    private UsbDevice mUsbDevice;
    private UsbManager mUsbManager;
    private UsbEndpoint mEpWrite;
    private UsbEndpoint mEpRead;
    private UsbDeviceConnection mUsbConnection;

	public UsbPrinter(Context context) {
		mContext = context;
		mUsbManager = (UsbManager) context.getSystemService(Context.USB_SERVICE);
	}

	public void selectPrinter(UsbDevice device) {
		mUsbDevice = device;
	}

	@Override
	public void open() throws PrinterException {
		if (!mUsbManager.hasPermission(mUsbDevice)) {
			PendingIntent pi = PendingIntent.getBroadcast(mContext, 0, new Intent(ACTION_USB_PERMISSION), 0);
			mUsbManager.requestPermission(mUsbDevice, pi);
		}

		UsbInterface usbIf = mUsbDevice.getInterface(0);
		mEpWrite = usbIf.getEndpoint(1);
		mEpRead = usbIf.getEndpoint(0);
		mUsbConnection = mUsbManager.openDevice(mUsbDevice);
		if (mUsbConnection != null) {
			if (!mUsbConnection.claimInterface(usbIf, true)) {
				throw new PrinterException(PrinterCommon.ERR_OPEN);
			}
		} else {
			throw new PrinterException(PrinterCommon.ERR_OPEN);
		}
	}

	@Override
	public void close() throws PrinterException {
		if (mUsbConnection != null) {
			mUsbConnection.close();
			mUsbConnection = null;
		} else {
			throw new PrinterException(PrinterCommon.ERR_CLOSE);
		}
	}

	@Override
	public int read(byte[] buf, int len) throws PrinterException {
		return read(buf, len, 1000);
	}

	@Override
	public void write(byte[] buf, int len) throws PrinterException {
		write(buf, buf.length, 1000);
	}

	@Override
	public int getType() {
		return PrinterCommon.USB_PRINTER;
	}

	public int read(byte[] buf, int len, int timeout) throws PrinterException {
		int ret = 0;
		if (buf != null && mUsbConnection != null && mEpWrite != null) {
			if((ret = mUsbConnection.bulkTransfer(mEpRead, buf, len, timeout)) < 0) {
				throw new PrinterException(PrinterCommon.ERR_READ);
			}
		} else {
			throw new PrinterException(PrinterCommon.ERR_READ);
		}
		return ret;
	}

	public void write(byte[] buf, int len, int timeout) throws PrinterException {
		if (mUsbConnection != null && mEpWrite != null) {
			if(mUsbConnection.bulkTransfer(mEpWrite, buf, len, timeout) < 0) {
				throw new PrinterException(PrinterCommon.ERR_WRITE);
			}
		} else {
			throw new PrinterException(PrinterCommon.ERR_WRITE);
		}
	}

    public List<UsbDevice> getPrinterList() {
        final HashMap<String, UsbDevice> usbList = mUsbManager.getDeviceList();
        final List<UsbDevice> result = new ArrayList<UsbDevice>();
        if (usbList != null) {
            UsbDevice device;
            final Iterator<UsbDevice> iterator = usbList.values().iterator();
            while (iterator.hasNext()) {
                device = iterator.next();
                UsbInterface usbInterface = device.getInterface(0);
                if (usbInterface != null) {
                    //refer: http://www.usb.org/developers/defined_class/#BaseClassFFh
                    if (usbInterface.getInterfaceClass() == 0x07) {
                        result.add(device);
                    } else {
                        //Log.d(TAG, "ignored usb class:" + usbInterface.getInterfaceClass()
                        //        + " product:" + device.getProductName()
                        //        + " Manufacturer:" + device.getManufacturerName());
                    }
                }
            }
        }
        return result;
    }
}
