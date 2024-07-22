package com.elavirint.pipoprint.printer;

public interface Printer {
    public void open() throws PrinterException;
    public void close() throws PrinterException;
	public int  read(byte[] buf, int len) throws PrinterException;
	public void write(byte[] buf, int len) throws PrinterException;
	public int getType();
}
