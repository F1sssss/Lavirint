package com.elavirint.pipoprint.activity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ListView;
import android.widget.Toast;

import androidx.appcompat.widget.Toolbar;

import androidx.appcompat.app.AppCompatActivity;

import com.elavirint.pipoprint.ListViewItem;
import com.elavirint.pipoprint.ListViewItemAdapter;
import com.elavirint.pipoprint.R;

import kotlin.NotImplementedError;

public class SelectPrinterTypeActivity extends AppCompatActivity {

    ListViewItem[] items = new ListViewItem[]{
            new ListViewItem(R.drawable.baseline_bluetooth_24, "Bluetooth"),
            new ListViewItem(R.drawable.baseline_cable_24, "USB"),
            new ListViewItem(R.drawable.serial_port_24, "Serial"),
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_select_printer_type);


        ListViewItemAdapter adapter = new ListViewItemAdapter(this, items);

        ListView listView = findViewById(R.id.list_view);
        listView.setAdapter(adapter);
        listView.setOnItemClickListener(this::onListItemClick);

        setSupportActionBar(findViewById(R.id.toolbar));

        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        toolbar.setNavigationIcon(R.drawable.baseline_arrow_back_24_white);
        toolbar.setTitle(R.string.select_printer_type_activity_title);
        setSupportActionBar(toolbar);
    }

    @Override
    public boolean onSupportNavigateUp() {
        onBackPressed();
        return true;
    }

    private void onListItemClick(AdapterView<?> parent, View view, int position, long id) {
        switch (position) {
            case 0:
                Intent intent = new Intent(this, SelectBluetoothPrinterActivity.class);
                startActivity(intent);
                break;
            case 1:
                break;
            case 2:
                break;
            default:
                throw new NotImplementedError();
        }
    }
}