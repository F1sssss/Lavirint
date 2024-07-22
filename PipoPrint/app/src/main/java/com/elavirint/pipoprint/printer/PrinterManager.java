
package com.elavirint.pipoprint.printer;


import android.graphics.Bitmap;
import android.graphics.Color;
import android.util.Log;
import android.util.Xml;

import java.io.UnsupportedEncodingException;
import java.lang.System;
import java.nio.charset.StandardCharsets;


public class PrinterManager {

	private static final int PRINTER_BUFFER_LEN = 4096;

	public static final int FULL_CUT   = 0;
	public static final int HALF_CUT   = 1;

	public static final int ALIGN_LEFT   = 0;
	public static final int ALIGN_MIDDLE = 1;
	public static final int ALIGN_RIGHT  = 2;

	public static final int FONT_DEFAULT       = 0;		//12x24
	public static final int FONT_SMALL         = 1<<0;	//9x17
	public static final int FONT_INVERSE       = 1<<1;
	public static final int FONT_UPSIDE_DOWN   = 1<<2;
	public static final int FONT_EMPHASIZED    = 1<<3;
	public static final int FONT_DOUBLE_HEIGHT = 1<<4;
	public static final int FONT_DOUBLE_WIDTH  = 1<<5;
	//public static final int FONT_DELETELINE     = 1<<6;
	public static final int FONT_UNDERLINE     = 1<<7;

	public static final int UNDERLINE_ZERO   = 0;
	public static final int UNDERLINE_HIGH_1 = 1;
	public static final int UNDERLINE_HIGH_2 = 2;

	public static final int CODEBAR_STRING_MODE_NONE  = 0;
	public static final int CODEBAR_STRING_MODE_ABOVE = 1;
	public static final int CODEBAR_STRING_MODE_BELOW = 2;
	public static final int CODEBAR_STRING_MODE_BOTH  = 3;

	public static final int UPC_A   = 65;
	public static final int UPC_E   = 66;
	public static final int EAN13   = 67;
	public static final int EAN8    = 68;
	public static final int CODE39  = 69;
	public static final int I25     = 70;
	public static final int CODEBAR = 71;
	public static final int CODE93  = 72;
	public static final int CODE128 = 73;
	public static final int CODE11  = 74;
	public static final int MSI     = 75;

	public static final int CHAR_SET_USA           = 0;
	public static final int CHAR_SET_FRANCE        = 1;
	public static final int CHAR_SET_GERMANY       = 2;
	public static final int CHAR_SET_ENGLAND       = 3;
	public static final int CHAR_SET_DENMARK_I     = 4;
	public static final int CHAR_SET_SWEDEN        = 5;
	public static final int CHAR_SET_ITALY         = 6;
	public static final int CHAR_SET_SPAIN_I       = 7;
	public static final int CHAR_SET_JAPAN         = 8;
	public static final int CHAR_SET_NORWAY        = 9;
	public static final int CHAR_SET_DENMARK_II    = 10;
	public static final int CHAR_SET_SPAIN_II      = 11;
	public static final int CHAR_SET_LATIN_AMERICA = 12;
	public static final int CHAR_SET_KOREA         = 13;
	public static final int CHAR_SET_CROATIA       = 14;
	public static final int CHAR_SET_CHINA         = 15;

	public static final int CODE_PAGE_CP437       = 0;//English
	public static final int CODE_PAGE_KATAKANA    = 1;//Janpanese
	public static final int CODE_PAGE_CP850       = 2;//Western Europe
	public static final int CODE_PAGE_CP860       = 3;//Portuguese
	public static final int CODE_PAGE_CP863       = 4;//Canadian-French
	public static final int CODE_PAGE_CP865       = 5;//Nordic
	public static final int CODE_PAGE_CP1251      = 6;//Cyrillic
	public static final int CODE_PAGE_CP866       = 7;//Cyrillic2
	public static final int CODE_PAGE_MIK         = 8;//Cyrillic,Bulgarian
	public static final int CODE_PAGE_CP755       = 9;//East Europe, Latvian2
	public static final int CODE_PAGE_IRAN        = 10;//Iran System encoding standard
	public static final int CODE_PAGE_CP862       = 15;//Hebrew
	public static final int CODE_PAGE_CP1252      = 16;//Latin1
	public static final int CODE_PAGE_CP1253      = 17;//Greek
	public static final int CODE_PAGE_CP852       = 18;//Latin2
	public static final int CODE_PAGE_CP858       = 19;//West Europe
	public static final int CODE_PAGE_IRAN2       = 20;//Iran2
	public static final int CODE_PAGE_LATVIAN     = 21;//Latvian
	public static final int CODE_PAGE_CP864       = 22;//Arabic
	public static final int CODE_PAGE_ISO_8859_1  = 23;//West Europe
	public static final int CODE_PAGE_CP737       = 24;//Greek
	public static final int CODE_PAGE_CP1257      = 25;//Baltic
	public static final int CODE_PAGE_THAI        = 26;//Thai1
	public static final int CODE_PAGE_CP720       = 27;//Arabic
	public static final int CODE_PAGE_CP855       = 28;//Cyrillic script
	public static final int CODE_PAGE_CP857       = 29;//Turkish
	public static final int CODE_PAGE_CP1250      = 30;//Central Europe
	public static final int CODE_PAGE_CP775       = 31;//Estonian, Lithuanian, Latvian
	public static final int CODE_PAGE_CP1254      = 32;//Turkish
	public static final int CODE_PAGE_CP1255      = 33;//Hebrew
	public static final int CODE_PAGE_CP1256      = 34;//Arabic
	public static final int CODE_PAGE_CP1258      = 35;//Vietnamese
	public static final int CODE_PAGE_ISO_8859_2  = 36;//Latin2
	public static final int CODE_PAGE_ISO_8859_3  = 37;//Latin3
	public static final int CODE_PAGE_ISO_8859_4  = 38;//Baltic
	public static final int CODE_PAGE_ISO_8859_5  = 39;//Cyrillic
	public static final int CODE_PAGE_ISO_8859_6  = 40;//Arabic
	public static final int CODE_PAGE_ISO_8859_7  = 41;//Greek
	public static final int CODE_PAGE_ISO_8859_8  = 42;//Hebrew
	public static final int CODE_PAGE_ISO_8859_9  = 43;//Turkish
	public static final int CODE_PAGE_ISO_8859_15 = 44;//Latin9
	public static final int CODE_PAGE_CP874       = 45;//Thai
	public static final int CODE_PAGE_CP856       = 46;//Hebrew

	public static final int CODE_PAGE_BIG5        = 98;//Traditional Chinese
	public static final int CODE_PAGE_GB18030     = 99;//Simplified Chinese

	public static final int BITMAP_ZOOM_NONE   = 0;
	public static final int BITMAP_ZOOM_WIDTH  = 1;
	public static final int BITMAP_ZOOM_HEIGHT = 2;
	public static final int BITMAP_ZOOM_BOTH   = 3;

	public static final int TYPE_PAPER_WIDTH_58MM = 0;
	public static final int TYPE_PAPER_WIDTH_76MM = 1;
	public static final int TYPE_PAPER_WIDTH_80MM = 2;

	//only used for BIG5 and GB18030
	private static final byte code_page[][] = {
		{(byte)0x1D,(byte)0xFE},
		{(byte)0x1C,(byte)0xFF},
	};

	private final int bmp_byte_width[] = {
		48,//58mm
		50,//76mm
		72,//80mm
	};

	private final int dots_per_line[] = {
		384,//58mm
		400,//76mm
		576,//80mm
	};


	private Printer mPrinter;
	private String mEncoding = "UTF-8";
	private int mPaperWidthType = TYPE_PAPER_WIDTH_58MM;

	public PrinterManager(Printer printer, int paperWidthType) {
		mPrinter = printer;
		mPaperWidthType = paperWidthType;
	}

	/**
	 * @brief Get the printer type
	 *
	 * @return printer type which defined in PrinterCommon
	 */
	public int getPrinterType() {
		return mPrinter.getType();
	}

	/**
	 * @brief Connect the printer
	 *
	 * @return 
	 */
	public void connect() throws PrinterException {
		mPrinter.open();
	}

	/**
	 * @brief Disconnect the printer
	 *
	 * @return 
	 */
	public void disconnect() throws PrinterException {
		mPrinter.close();
	}

	/**
	 * @brief Check paper status, only used by serial port printer
	 *
	 * @return
	 */
	public void checkPaper() throws PrinterException {
		byte[] status = new byte[1];
		sendCmd(PrinterCommand.cmdGSrn(1));
		mPrinter.read(status, 1);
		if (status[0] != 0) {
			throw new PrinterException(PrinterCommon.ERR_NO_PAPER);
		}
	}

	/**
	 * @brief Set default string encoding
	 *
	 * @param encoding
	 *
	 * @return 
	 */
	public void setStringEncoding(String encoding) throws PrinterException {
		if (encoding == null) {
			throw new PrinterException(PrinterCommon.ERR_PARAM);
		}
		mEncoding = encoding;
	}

	/**
	 * @brief Send string data to printer
	 *
	 * @param data
	 *
	 * @return 
	 */
	public void sendData(String data) throws PrinterException {
		sendData(data, mEncoding);
	}

	/**
	 * @brief Send string data by appoint encoding
	 *
	 * @param data
	 * @param encoding
	 *
	 * @return 
	 */
	public void sendData(String data, String encoding) throws PrinterException {
		if (data == null || encoding == null) {
			throw new PrinterException(PrinterCommon.ERR_PARAM);
		}
		try {
			byte[] bytes = data.getBytes(encoding);
			mPrinter.write(bytes, bytes.length);
		} catch (UnsupportedEncodingException e) {
			e.printStackTrace();
		}
	}

	/**
	 * @brief Write command to printing buffer
	 *
	 * @param cmd
	 *
	 * @return 
	 */
	public void sendCmd(byte[] cmd) throws PrinterException {
		sendCmd(cmd, 0);
	}

	/**
	 * @brief Write command to printing buffer
	 *
	 * @param cmd
	 * @param delay in ms for print. usually, serial printer needed
	 *
	 * @return 
	 */
	public void sendCmd(byte[] cmd, int delay) throws PrinterException {
	    //PT486 serial print need delay
		boolean needDelay = false;
		int wait = ((delay > 0) ? (delay) : (50));
		if (mPrinter.getType() == PrinterCommon.SERIAL_PRINTER) {
			needDelay = true;
		}

		if (cmd.length > PRINTER_BUFFER_LEN) {
			int i=0;
			int count = (int)(cmd.length / PRINTER_BUFFER_LEN);
			int end = cmd.length - (count * PRINTER_BUFFER_LEN);
			byte[] tmp = new byte[PRINTER_BUFFER_LEN];
			byte[] last = new byte[end];
			while(count-- > 0) {
				System.arraycopy(cmd, i, tmp, 0, PRINTER_BUFFER_LEN);
				mPrinter.write(tmp, tmp.length);
				if (needDelay) {
					try {
						Thread.sleep(wait);
					} catch (InterruptedException e) {
						e.printStackTrace();
					}
				}
				i+=PRINTER_BUFFER_LEN;
			}
			System.arraycopy(cmd, i, last, 0, end);
			mPrinter.write(last, last.length);
		} else {
			mPrinter.write(cmd, cmd.length);
		}

		if (needDelay) {
			try {
				Thread.sleep(wait);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
	}

	/**
	 * @brief Print buffer and feeds one line
	 *
	 * @return 
	 */
	public void cmdLineFeed() throws PrinterException {
		sendCmd(PrinterCommand.cmdLF());
	}

	/**
	 * @brief Print buffer and feeds n line. ESC2,ESC3 decide the line spacing
	 *
	 * @param n 0-255
	 *
	 * @return 
	 */
	public void cmdLineFeed(int n) throws PrinterException {
		sendCmd(PrinterCommand.cmdESCdn(n));
	}

	/**
	 * @brief Jump to next tab
	 *
	 * @return 
	 */
	public void cmdJumpTab() throws PrinterException {
		sendCmd(PrinterCommand.cmdHT());
	}

	/**
	 * @brief Set the line space to default value(32dots)
	 *
	 * @return 
	 */
	public void cmdSetDefaultLineSpacing() throws PrinterException {
		sendCmd(PrinterCommand.cmdESC2());
	}

	/**
	 * @brief Set the line space to n dots
	 *
	 * @param dots 0-255
	 *
	 * @return 
	 */
	public void cmdSetLineSpacing(int dots) throws PrinterException {
		sendCmd(PrinterCommand.cmdESC3n(dots));
	}

	/**
	 * @brief Set align mode
	 *
	 * @param mode 0:left
	 *             1:middle
	 *             2:right
	 *
	 * @return 
	 */
	public void cmdSetAlignMode(int mode) throws PrinterException {
		sendCmd(PrinterCommand.cmdESCan(mode));
	}

	/**
	 * @brief Specify absolute position
	 *
	 * @param n character counts
	 *
	 * @return 
	 */
	public void cmdSetAbsPosition(int n) throws PrinterException {
		sendCmd(PrinterCommand.cmdESCnLnH(n&0xf, n&0xf0));
	}

	/**
	 * @brief Set print mode for all characters
	 *
	 * @param mode 
	 * <pre>
	 * bit0: 0 restore default
	 * bit1: inverse
	 * bit2: upside down
	 * bit3: emphasized
	 * bit4: double height
	 * bit5: double width
	 * bit6: deleteline(doesn't support)
	 * bit7: underline
	 * </pre>
	 *
	 * @return 
	 */
	public void cmdSetPrintMode(int mode) throws PrinterException {
		if ((mode & FONT_INVERSE) == 2) {
			sendCmd(PrinterCommand.cmdGSBn(1));
		} else {
			sendCmd(PrinterCommand.cmdGSBn(0));
		}
		if ((mode & FONT_UPSIDE_DOWN) == 4) {
			sendCmd(PrinterCommand.cmdESCbracketN(1));
		} else {
			sendCmd(PrinterCommand.cmdESCbracketN(0));
		}
		sendCmd(PrinterCommand.cmdESCexclamationN(mode));
	}

	/**
	 * @brief Set the underline height
	 *
	 * @param n 0:no underline 1: height 1 dots 2: height 2 dots
	 *
	 * @return 
	 */
	public void cmdSetUnderlineHeight(int n) throws PrinterException {
		sendCmd(PrinterCommand.cmdESCminusN(n));
	}

	/* bar code command */

	/**
	 * @brief Set the position of the bar code string
	 *
	 * @param mode  
	 * <pre>
	 *			  0: not printed
	 *            1: above bar code
	 *            2: below bar code
	 *            3: botha below and above bar code
	 * </pre>
	 * @return 
	 */
	public void cmdSetBarCodeStringPosition(int mode) throws PrinterException {
		sendCmd(PrinterCommand.cmdGSHn(mode));
	}

	/**
	 * @brief Set the bar code height
	 *
	 * @param n 1-255 default is 50
	 *
	 * @return 
	 */
	public void cmdSetBarCodeHeight(int n) throws PrinterException {
		sendCmd(PrinterCommand.cmdGShn(n));
	}

	/**
	 * @brief Set the bar code width
	 *
	 * @param n 2-6 default is 2
	 *
	 * @return 
	 */
	public void cmdSetBarCodeWidth(int n) throws PrinterException {
		sendCmd(PrinterCommand.cmdGSwn(n));
	}

	/**
	 * @brief Print bar code
	 *
	 * @param type bar code encoding type
	 * @param string bar code string
	 *
	 * @return 
	 */
	public void cmdBarCodePrint(int type, String string) throws PrinterException {
		if (string == null) {
			throw new PrinterException(PrinterCommon.ERR_PARAM);
		}
		byte[] barCode = string.getBytes();
		sendCmd(PrinterCommand.cmdGSkmnd(type, barCode.length, barCode));
	}

	@Deprecated
	public void cmdBitmapPrint(Bitmap bitmap, int zoom, int left, int top) throws PrinterException {
		cmdBitmapPrint(bitmap, zoom, left, top, 0);
	}

	public void printQRCode(String content, int errorCorrection, int model, int size) throws PrinterException, UnsupportedEncodingException {
		byte[] modelCommand = new byte[] { 0x1D, 0x28, 0x6B, 0x04, 0x00, 0x31, 0x41, (byte) model, 0x00 };
		byte[] sizeCommand = new byte[] { 0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x43, (byte) size };
		byte[] errorCorrectionCommand = new byte[] { 0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x45, (byte )errorCorrection };
		int num = content.length() + 3;
		int pL = num % 256;
		int pH = num / 256;
		byte[] storeCommand = new byte[] { 0x1D, 0x28, 0x6B, (byte) pL, (byte) pH, 0x31, 0x50, 0x30 };
		byte[] printCommand = new byte[] { 0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x51, 0x30 };

		byte[] data = content.getBytes(StandardCharsets.UTF_8);

		mPrinter.write(modelCommand, 0);
		mPrinter.write(sizeCommand, 0);
		mPrinter.write(errorCorrectionCommand, 0);
		mPrinter.write(storeCommand, 0);
		mPrinter.write(data, 0);
		mPrinter.write(printCommand, 0);
	}

	/**
	 * @brief Print bitmap
	 *
	 * @param bitmap android bitmap
	 * @param zoom
	 * <pre>
	 * 0: original size
	 * 1: double width
	 * 2: double height
	 * 3: double width and double height
	 * </pre>
	 * @param x left blank dots
	 * @param y top blank dots
	 * @param delay (ms) for print, serial printer needed
	 *
	 * @return 
	 */
	public void cmdBitmapPrint(Bitmap bitmap, int zoom, int left, int top, int delay) throws PrinterException {
		Log.i("asdasd", " Width: " + String.valueOf(bitmap.getWidth()));
		Log.i("asdasd", "Height: " + String.valueOf(bitmap.getHeight()));
		byte[] result = null;
		if (bitmap == null) {
			throw new PrinterException(PrinterCommon.ERR_PARAM);
		}
		if (((bitmap.getWidth() + left) > dots_per_line[mPaperWidthType]) ) {
			throw new PrinterException(PrinterCommon.ERR_PARAM);
		}
		//limits width
		int lines = bitmap.getHeight() + top;
		int w = bitmap.getWidth();
		int h = bitmap.getHeight();
		result = new byte[lines * bmp_byte_width[mPaperWidthType]];
		for (int y = 0; y < h; y++) {
			for (int x = 0; x < w; x++) {
				int color=bitmap.getPixel(x, y);
				//int alpha=Color.alpha(color);
				int red= Color.red(color);
				int green=Color.green(color);
				int blue=Color.blue(color);
				if (red < 128) {
					int bitX =  x + left;
					int byteX = bitX >> 3;
					int byteY = y + top;
					result[byteY * bmp_byte_width[mPaperWidthType] + byteX] |= (0x80 >> (bitX - (byteX << 3)));
				}
			}
		}
		sendCmd(PrinterCommand.cmdGSv0pwLwHhLhHd(zoom, bmp_byte_width[mPaperWidthType], 0, lines&0xff, (lines>>8)&0xff, result), delay);
	}

	/**
	* @brief Adjust hearting param, some printer support this command
	* <pre>
	* Set max heating dots, heating time, heating interval
	* The more max heting dots, the more peak current will cost
	* when printing, the faster printing speed. The max heating dots is 8*(n1+1)
	* The more heating time, the more density , but the slower printing
	* speed. If heating time is too short, blank page may occur.
	* The more heating interval, the more clear, but the slower printingspeed.
	* </pre>
	*
	* @param dots	0-255 Max printing dots,Unit(8dots),Default:7(64 dots)
	* @param time	Heating time,Unit(10us),Default:80(800us)
	* @param interval	Heating interval,Unit(10us),Default:2(20us)
	*
	* @return 
	*/
	public void cmdSetHeatingParam(int dots, int time, int interval) throws PrinterException {
		sendCmd(PrinterCommand.cmdESC7n1n2n3(dots, time, interval));
	}

	/**
	* @brief Set the print density, some printer support this command
	*
	* @param density 0-31
	* @param delay 0-7
	*
	* @return 
	*/
	public void cmdSetPrintDensity(int density, int delay) throws PrinterException {
		int arg = ((delay<<5)&0x7)|(density&0x1F);
		sendCmd(PrinterCommand.cmdDC2_n(arg));
	}

	/**
	 * @brief Set the international character set
	 *
	 * @param set
	 *
	 * @return 
	 */
	public void cmdSetCharacterSet(int set) throws PrinterException {
		sendCmd(PrinterCommand.cmdESCRn(set));
	}

	/**
	* @brief Set the character code page, some printer support this command
	*
	* @param code
	*
	* @return 
	*/
	public void cmdSetCodePageTable(int code) throws PrinterException {
		if (code == CODE_PAGE_BIG5 || code == CODE_PAGE_GB18030) {
			byte[] cmd = {(byte)0x03,(byte)0xFF,(byte)0x60,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x09,(byte)0x00,(byte)0x95,(byte)0xE3,(byte)0x00,(byte)0x01,(byte)0xC2,(byte)0x00,(byte)0x00,(byte)0x13,(byte)0x12,(byte)0x21,(byte)0x00};
			cmd[11] = code_page[code-98][0];
			cmd[16] = code_page[code-98][1];
			sendCmd(cmd);
		} else {
			//FIXME: need restore CP437 after switch to BIG5 or GB18030
			byte[] tmp = {(byte)0x03,(byte)0xFF,(byte)0x60,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x00,(byte)0x09,(byte)0x00,(byte)0x95,(byte)0xE3,(byte)0x00,(byte)0x01,(byte)0xC2,(byte)0x00,(byte)0x00,(byte)0x13,(byte)0x12,(byte)0x21,(byte)0x00};
			sendCmd(tmp);

			byte[] cmd = {(byte)0x1B,(byte)0x74,(byte)0x0};
			cmd[2] = (byte)code;
			sendCmd(cmd);
		}
	}

	/**
	* @brief Print a test page, some printer support this command
	*
	* @return 
	*/
	public void cmdPrintTest() throws PrinterException {
		sendCmd(PrinterCommand.cmdDC2T());
	}

	/**
	 * @brief Select the cut mode to cut paper
	 *
	 * @param mode
	 *
	 * @return 
	 */
	public void cmdCutPaper(int mode) throws PrinterException {
		sendCmd(PrinterCommand.cmdGSvm(mode));
	}

	/**
	 * @brief Get the dots per line
	 *
	 * @return dots count
	 */
	public int getDotsPerLine() {
		return dots_per_line[mPaperWidthType];
	}

}
