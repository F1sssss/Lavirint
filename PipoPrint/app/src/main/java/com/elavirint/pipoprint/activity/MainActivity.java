package com.elavirint.pipoprint.activity;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import com.elavirint.pipoprint.R;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button button = findViewById(R.id.select_printer_button);
        button.setOnClickListener(this::onSelectPrinterButtonClick);
    }

    public void onSelectPrinterButtonClick(View view) {
        Intent intent = new Intent(this, SelectPrinterTypeActivity.class);
        startActivity(intent);
    }
}