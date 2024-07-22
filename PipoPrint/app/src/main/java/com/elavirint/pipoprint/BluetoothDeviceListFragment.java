package com.elavirint.pipoprint;

import android.bluetooth.BluetoothDevice;
import android.os.Bundle;

import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.RecyclerView;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.elavirint.pipoprint.utils.DataManager;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link BluetoothDeviceListFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class BluetoothDeviceListFragment extends Fragment {
    RecyclerView mRecyclerView;

    public BluetoothDeviceListFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param param1 Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment BluetoothDeviceListFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static BluetoothDeviceListFragment newInstance(String param1, String param2) {
        return new BluetoothDeviceListFragment();
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View view = inflater.inflate(R.layout.fragment_bluetooth_device_list, container, false);

        mRecyclerView = view.findViewById(R.id.recyclerView);

        BluetoothDeviceCardAdapter adapter = new BluetoothDeviceCardAdapter();
        for (BluetoothDevice device: DataManager.getInstance().getBluetoothController().findDevices()) {
            adapter.addDevice(device);
        }

        mRecyclerView.setAdapter(adapter);

        return view;
    }
}