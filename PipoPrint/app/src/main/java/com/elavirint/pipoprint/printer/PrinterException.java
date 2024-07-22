package com.elavirint.pipoprint.printer;

public class PrinterException extends Exception {

	private int mErrCode = 255;

    public PrinterException() {
    }

 	public PrinterException(String name) {
		super(name);
	}

	public PrinterException(Throwable cause) {
		super(cause);
	}

	public PrinterException(String name, Throwable cause) {
		super(name, cause);
	}

	public PrinterException(int errCode) {
		mErrCode = errCode;
	}

	public int getErrorCode() {
		return mErrCode;
	}
   
}
