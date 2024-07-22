package com.elavirint.pipoprint;

import static androidx.core.content.ContextCompat.checkSelfPermission;

import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.pm.PackageManager;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.RecyclerView;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.Toast;

import com.elavirint.pipoprint.utils.BluetoothController;
import com.elavirint.pipoprint.utils.DataManager;

import java.io.IOException;
import java.io.OutputStream;
import java.util.Set;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link BluetoothPrintersFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class BluetoothPrintersFragment extends Fragment {

    private static final int BLUETOOTH_PERMISSION_REQUEST_CODE = 123;

    BluetoothDeviceCardAdapter btCardAdapter;

    Button button;

    Toast toast;

    RecyclerView recyclerView;

    public BluetoothPrintersFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param param1 Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment BluetoothPrinters.
     */
    // TODO: Rename and change types and number of parameters
    public static BluetoothPrintersFragment newInstance(String param1, String param2) {
        return new BluetoothPrintersFragment();
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_bluetooth_printers, container, false);

        if (ContextCompat.checkSelfPermission(requireContext(), android.Manifest.permission.BLUETOOTH) != PackageManager.PERMISSION_GRANTED) {
            // Bluetooth permissions are already granted
            // Perform your Bluetooth-related operations here
        } else {
            if (ActivityCompat.shouldShowRequestPermissionRationale(requireActivity(), Manifest.permission.BLUETOOTH)) {
                // Show an explanation to the user if needed
                // You can show a dialog explaining why you need the permission
            } else {
                // No explanation needed, request the permission
                ActivityCompat.requestPermissions(requireActivity(),
                        new String[]{Manifest.permission.BLUETOOTH, Manifest.permission.BLUETOOTH_ADMIN},
                        BLUETOOTH_PERMISSION_REQUEST_CODE);
            }
        }



        btCardAdapter = new BluetoothDeviceCardAdapter();
        for (BluetoothDevice device : DataManager.getInstance().getBluetoothController().findDevices()) {
            btCardAdapter.addDevice(device);
        }

        recyclerView = view.findViewById(R.id.recyclerView);
        recyclerView.setAdapter(btCardAdapter);

        button = view.findViewById(R.id.testPrintButton);
        button.setOnClickListener(this::onPrintButtonClick);

        return view;
    }

    private void onPrintButtonClick(View view) {
        BluetoothDevice device = DataManager.getInstance().getBluetoothController().getSelected();

        if (toast != null) {
            toast.cancel();
        }

        if (device == null) {
            toast = Toast.makeText(requireContext(), "Morate odabrati štampač.", Toast.LENGTH_SHORT);
            toast.show();
            return;
        }

        Executor executor = Executors.newSingleThreadExecutor();
        executor.execute(() -> {
            BluetoothSocket socket = null;
            OutputStream outputStream = null;

            try {
                if (checkSelfPermission(requireContext(), Manifest.permission.BLUETOOTH) != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[]{Manifest.permission.BLUETOOTH}, 0);
                }

                socket = device.createRfcommSocketToServiceRecord(device.getUuids()[0].getUuid());
                socket.connect();

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

                outputStream = socket.getOutputStream();
                outputStream.write(data);
                outputStream.flush();
                outputStream.close();
            } catch (IOException e) {
                throw new RuntimeException(e);
            } finally {
                try {
                    if (outputStream != null) {
                        outputStream.close();
                    }

                    if (socket != null) {
                        socket.close();
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }

        });
    }
}