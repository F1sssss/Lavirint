package com.elavirint.pipoprint.utils;

import android.content.Context;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbManager;

import java.util.ArrayList;

public class UsbController {
    private final ArrayList<UsbDevice> mDeviceList = new ArrayList<>();

    private UsbDevice mSelectedDevice;

    public ArrayList<UsbDevice> getDeviceList() {
        return mDeviceList;
    }

    public void selectDevice(int index) {
        mSelectedDevice = mDeviceList.get(index);
    }

    public void deselectDevice() {
        mSelectedDevice = null;
    }

    public void addDevice(UsbDevice newDevice) {
        for (UsbDevice device : mDeviceList) {
            if (device.getDeviceId() == newDevice.getDeviceId()) {
                Logger.d(UsbController.class, "device already exists");
                return;
            }
        }
        mDeviceList.add(newDevice);
    }

    public ArrayList<UsbDevice> findDevices() {
    }
}
