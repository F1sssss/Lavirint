package com.elavirint.pipoprint.printer;

/**
 * Created by hansen on 18-1-2.
 */

public class NetworkPrinter implements Printer {
    @Override
    public void open() throws PrinterException {

    }

    @Override
    public void close() throws PrinterException {

    }

    @Override
    public int read(byte[] buf, int len) throws PrinterException {
        return 0;
    }

    @Override
    public void write(byte[] buf, int len) throws PrinterException {

    }

    @Override
    public int getType() {
        return PrinterCommon.NETWORK_PRINTER;
    }
}
