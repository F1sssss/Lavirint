package com.elavirint.pipoprint;

import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbDeviceConnection;
import android.hardware.usb.UsbEndpoint;
import android.hardware.usb.UsbInterface;
import android.hardware.usb.UsbManager;
import android.os.Bundle;

import androidx.fragment.app.Fragment;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.elavirint.pipoprint.utils.Logger;

import java.util.Collection;


/**
 * A simple {@link Fragment} subclass.
 * Use the {@link USBPrintersFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class USBPrintersFragment extends Fragment {

    public static final String ACTION_USB_PERMISSION = "ACTION_USB_PRINTER_PERMISSION";
    UsbManager usbManager;

    public USBPrintersFragment() {
        // Required empty public constructor
    }

    public static USBPrintersFragment newInstance() {
       return new USBPrintersFragment();
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    public Collection<UsbDevice> getUsbDevices() {
        usbManager = (UsbManager) requireContext().getSystemService(Context.USB_SERVICE);
        return usbManager.getDeviceList().values();
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_usb_printers, container, false);



        usbManager = (UsbManager) requireContext().getSystemService(Context.USB_SERVICE);

        for (UsbDevice device : usbManager.getDeviceList().values()) {
            System.out.println(device.getProductName());
            System.out.println(device.getManufacturerName());
            System.out.println(device.getDeviceName());
            System.out.println(device.getVendorId());
            System.out.println(device.getProductId());
            System.out.println(device.getSerialNumber());
            System.out.println();
        }

        UsbDevice usbDevice = usbManager.getDeviceList().entrySet().iterator().next().getValue();

        if (usbManager.hasPermission(usbDevice)) {
            // Your app has permission to access the USB device
            // Perform USB operations here
        } else {
            // Request USB permission
            PendingIntent permissionIntent = PendingIntent.getBroadcast(requireContext(), 0, new Intent(ACTION_USB_PERMISSION), PendingIntent.FLAG_IMMUTABLE);
            usbManager.requestPermission(usbDevice, permissionIntent);
        }

        UsbDeviceConnection connection = usbManager.openDevice(usbDevice);
        UsbInterface usbInterface = usbDevice.getInterface(0);
        connection.claimInterface(usbInterface, true);

        UsbEndpoint outEndpoint = null;
        for (int ii = 0; ii < usbInterface.getEndpointCount(); ii++) {
            UsbEndpoint endpoint = usbInterface.getEndpoint(ii);
            if (endpoint.getType() == 2 && endpoint.getDirection() != 128) {
                outEndpoint = endpoint;
                break;
            }
        }

        if (outEndpoint != null) {
            Logger.d(USBPrintersFragment.class, "tTest");
            byte[] data = new byte[]{
                    27, 64,
                    27, 45, 0,
                    27, 45, 48,
                    84, 101, 115, 116,
                    84, 101, 115, 116,
                    84, 101, 115, 116,
                    84, 101, 115, 116,
                    84, 101, 115, 116,
                    84, 101, 115, 116,
                    84, 101, 115, 116,
                    84, 101, 115, 116,
                    13, 10, 0
            };
            connection.bulkTransfer(outEndpoint, data, data.length, 0);
        }

        return view;
    }
}