package com.elavirint.pipoprint.printer;

public class PrinterCommon {
    public static final int ERR_OPEN  = 1;
    public static final int ERR_CLOSE = 2;
    public static final int ERR_READ  = 3;
    public static final int ERR_WRITE = 4;
    public static final int ERR_PARAM = 5;
    public static final int ERR_NO_PAPER = 6;

    public static final int USB_PRINTER       = 0x1;
    public static final int SERIAL_PRINTER    = 0x2;
    public static final int NETWORK_PRINTER   = 0x3;
    public static final int BLUETOOTH_PRINTER = 0x4;
}
