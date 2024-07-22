package com.elavirint.pipoprint.activity;

import androidx.appcompat.app.AppCompatActivity;

import android.app.PendingIntent;
import android.content.Intent;
import android.os.Bundle;

import com.elavirint.pipoprint.PipoPrintService;

public class PrintActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    protected void onStart() {
        super.onStart();

        Intent printIntent = new Intent(this, PipoPrintService.class);
        printIntent.setAction("PRINT_FROM_BASE64_COMMANDS");
        printIntent.setData(getIntent().getData());
        overridePendingTransition(0, 0);
        printIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_NO_ANIMATION);
        moveTaskToBack(true);  // Keeps app in the background

        startService(printIntent);
    }
}