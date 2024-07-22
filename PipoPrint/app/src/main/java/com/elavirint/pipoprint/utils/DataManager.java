package com.elavirint.pipoprint.utils;

import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.hardware.usb.UsbDevice;

import java.util.ArrayList;
import java.util.Set;

public class DataManager {
    private static DataManager instance;

    private BluetoothController mBluetoothController = new BluetoothController();
    private final ArrayList<UsbDevice> mUsbDeviceList = new ArrayList<UsbDevice>();

    private PrinterType mPrinterType = PrinterType.None;
    private int mSelectedUsbDeviceIndex = -1;

    public void selectBluetoothDevice(int position) {
        mPrinterType = PrinterType.Bluetooth;
        getBluetoothController().selectDevice(position);
    }

    public enum PrinterType {
        None,
        Bluetooth,
        Usb,
        Serial
    }

    private DataManager() {

    }

    public static DataManager getInstance() {
        if (instance == null) {
            instance = new DataManager();
        }
        return instance;
    }

    public ArrayList<UsbDevice> getUsbDeviceList() {
        return mUsbDeviceList;
    }

    public void addUsbDevice(UsbDevice device) {
        for (UsbDevice existingDevice : mUsbDeviceList) {
            if (existingDevice.getDeviceId() == device.getDeviceId()) {
                Logger.d(DataManager.class, "device already exists");
                return;
            }
        }
    }

    public void clearUsbDeviceList() {
        mUsbDeviceList.clear();
    }

    public BluetoothController getBluetoothController() {
        return mBluetoothController;
    }
}
