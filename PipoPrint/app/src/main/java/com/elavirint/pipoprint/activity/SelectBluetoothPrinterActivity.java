package com.elavirint.pipoprint.activity;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.recyclerview.widget.RecyclerView;

import android.bluetooth.BluetoothDevice;
import android.os.Bundle;
import android.widget.Button;
import android.widget.Toast;

import com.elavirint.pipoprint.BluetoothDeviceCardAdapter;
import com.elavirint.pipoprint.R;
import com.elavirint.pipoprint.utils.DataManager;


public class SelectBluetoothPrinterActivity extends AppCompatActivity {

    Toast toast;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_select_bluetooth_printer);

        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        toolbar.setNavigationIcon(R.drawable.baseline_arrow_back_24_white);
        toolbar.setTitle("Odaberite štampač");
        setSupportActionBar(toolbar);

        RecyclerView mRecyclerView = findViewById(R.id.recyclerView);

        BluetoothDeviceCardAdapter adapter = new BluetoothDeviceCardAdapter();
        for (BluetoothDevice device: DataManager.getInstance().getBluetoothController().findDevices()) {
            adapter.addDevice(device);
        }
        mRecyclerView.setAdapter(adapter);

        Button confirmButton = findViewById(R.id.print_button);
        confirmButton.setOnClickListener(view -> {
            if (toast != null) {
                toast.cancel();
            }

            toast = Toast.makeText(this, "Sent to print", Toast.LENGTH_LONG);
            toast.show();
        });

        Button selectPrinterButton = findViewById(R.id.select_printer_button);
        selectPrinterButton.setOnClickListener(view -> {
            if (toast != null) {
                toast.cancel();
            }
            toast = Toast.makeText(this, "Selected the printer", Toast.LENGTH_LONG);
            toast.show();
        });
    }

    @Override
    public boolean onSupportNavigateUp() {
        onBackPressed();
        return true;
    }
}