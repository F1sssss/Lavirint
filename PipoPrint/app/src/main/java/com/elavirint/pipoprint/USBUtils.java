package com.elavirint.pipoprint;

import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbDeviceConnection;
import android.hardware.usb.UsbEndpoint;
import android.hardware.usb.UsbInterface;
import android.hardware.usb.UsbManager;
import android.hardware.usb.UsbRequest;

import java.nio.ByteBuffer;
import java.util.HashMap;
import java.util.Iterator;

public class USBUtils {

    private static final String TAG = USBUtils.class.getSimpleName();

    private static final int TIMEOUT = 0;

    public static void listDevices(Context context, byte[] data) {
        UsbManager usbManager = (UsbManager) context.getSystemService(Context.USB_SERVICE);
        HashMap<String, UsbDevice> deviceMap = usbManager.getDeviceList();
        Iterator<UsbDevice> deviceIterator = deviceMap.values().iterator();

        while (deviceIterator.hasNext()) {
            sendData(context, deviceIterator.next(), data);
        }
    }

    public static boolean sendData(Context context, UsbDevice device, byte[] data) {
        UsbManager usbManager = (UsbManager) context.getSystemService(Context.USB_SERVICE);

        UsbInterface usbInterface = device.getInterface(0);
        UsbEndpoint endpoint = usbInterface.getEndpoint(1);

        if (!usbManager.hasPermission(device)) {
            PendingIntent permissionIntent = PendingIntent.getBroadcast(context, 0, new Intent("com.example.USB_PERMISSION"), 0);
            usbManager.requestPermission(device, permissionIntent);
            return false;
        }

        UsbDeviceConnection connection = usbManager.openDevice(device);

        UsbRequest usbRequest = new UsbRequest();
        usbRequest.initialize(connection, endpoint);

        ByteBuffer buffer = ByteBuffer.allocate(data.length);
        buffer.put(data);

        usbRequest.queue(buffer, data.length);

        if (connection.requestWait() == usbRequest) {
            return true;
        }

        return false;
    }
}