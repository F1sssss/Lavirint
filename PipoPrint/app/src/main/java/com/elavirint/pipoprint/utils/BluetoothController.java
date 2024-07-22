package com.elavirint.pipoprint.utils;

import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;

import java.util.ArrayList;
import java.util.Set;

public class BluetoothController {
    private final ArrayList<BluetoothDevice> mDeviceList = new ArrayList<>();

    private BluetoothDevice mSelectedDevice;

    public ArrayList<BluetoothDevice> getDeviceList() {
        return mDeviceList;
    }

    public void selectDevice(int index) {
        mSelectedDevice = mDeviceList.get(index);
    }

    public void deselectDevice() {
        mSelectedDevice = null;
    }

    public void addDevice(BluetoothDevice newDevice) {
        for (BluetoothDevice device : mDeviceList) {
            if (device.getAddress().equals(newDevice.getAddress())) {
                Logger.d(BluetoothController.class, "device already exists");
                return;
            }
        }
        mDeviceList.add(newDevice);
    }

    @SuppressLint("MissingPermission")
    public ArrayList<BluetoothDevice> findDevices() {
        BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
        Set<BluetoothDevice> pairedDevices = adapter.getBondedDevices();
        for (BluetoothDevice device : pairedDevices) {
            addDevice(device);
        }

        return mDeviceList;
    }

    public void clearDeviceList() {
        deselectDevice();
        mDeviceList.clear();
    }

    public BluetoothDevice getSelected() {
        return mSelectedDevice;
    }
}
