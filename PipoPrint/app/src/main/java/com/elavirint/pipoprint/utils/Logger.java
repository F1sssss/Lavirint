package com.elavirint.pipoprint.utils;

import android.util.Log;

public class Logger {

    public static final String _TAG  = "PipoPrint";
    private static final boolean DEBUG_MODE = true;


    public static void d(String tag, String log) {
        if (DEBUG_MODE) {
            Log.d(tag, log);
        }
    }

    public static void d(String log) {
        if (DEBUG_MODE) {
            Log.d(_TAG, log);
        }
    }

    public static void d(Class<?> cls, String log) {
        if (DEBUG_MODE) {
            Log.d(cls.getSimpleName(), log);
        }
    }

    public static void e(String log) {
        if (DEBUG_MODE) {
            Log.e(_TAG, log);
        }
    }

    public static void e(String tag, String log) {
        if (DEBUG_MODE) {
            Log.e(tag, log);
        }
    }

    public static void e(Throwable exception) {
        if (DEBUG_MODE) {
            exception.printStackTrace();
        }
    }

    public static void s(String log) {
        if (DEBUG_MODE) {
            Log.d(_TAG, log);
        }
    }

    public static void s(String tag, String log) {
        if (DEBUG_MODE) {
            Log.d(tag, log);
        }
    }
}
