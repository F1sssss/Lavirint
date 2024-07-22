package com.elavirint.pipoprint;

import android.content.Intent;
import android.os.Handler;
import android.os.ParcelFileDescriptor;
import android.print.PrintAttributes;
import android.print.PrinterCapabilitiesInfo;
import android.print.PrinterId;
import android.print.PrinterInfo;
import android.printservice.PrintJob;
import android.printservice.PrintService;
import android.printservice.PrinterDiscoverySession;
import android.util.Base64;
import android.util.Log;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.aill.androidserialport.SerialPort;
import com.elavirint.pipoprint.printer.PrinterManager;
import com.elavirint.pipoprint.printer.SerialPortPrinterNew;
import com.itextpdf.text.pdf.PdfReader;
import com.itextpdf.text.pdf.parser.PdfTextExtractor;

import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;

import com.github.anastaciocintra.escpos.EscPos;


public class PipoPrintService extends PrintService {

    public final String LOG_TAG = "PipoPrintService";

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.e("Test", "onStartCommand called");

        if ("PRINT_FROM_BASE64_COMMANDS".equals(intent.getAction())) {
            if (intent.getData() == null) {
                processCommands("");
            } else {
                processCommands(intent.getData().toString());
            }
        }

        return super.onStartCommand(intent, flags, startId);
    }

    @Nullable
    @Override
    protected PrinterDiscoverySession onCreatePrinterDiscoverySession() {
        return new PipoPrinterDiscoverySession();
    }

    @Override
    protected void onRequestCancelPrintJob(PrintJob printJob) {

    }

    public void processCommands(String data) {
        String base64EncodedString = data.split(":")[1];

        try {
            SerialPort serialPort = new SerialPort(new File("/dev/ttyS3"), 9600, 0);
            OutputStream outputStream = serialPort.getOutputStream();
            EscPos escpos = new EscPos(outputStream);
            escpos.initializePrinter();
            escpos.setCharacterCodeTable(EscPos.CharacterCodeTable.ISO8859_2_Latin2);

            String[] decodedData = new String(Base64.decode(base64EncodedString, Base64.NO_WRAP)).split(",");
            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            for (String decodedDatum : decodedData) {
                byteArrayOutputStream.write(Integer.parseInt(decodedDatum));
            }
            byte[] bytes = byteArrayOutputStream.toByteArray();
            escpos.write(bytes, 0, bytes.length);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void onPrintJobQueued(PrintJob printJob) {
        if (printJob == null) {
            return;
        }

        if (printJob.isQueued()) {
            printJob.start();
        }

        try {
            ParcelFileDescriptor original = printJob.getDocument().getData();
            File copy = null;
            try {
                copy = File.createTempFile("tmp", ".pdf", getFilesDir());
                Log.i(LOG_TAG, "File is " + copy);

            } catch (IOException e) {
                e.printStackTrace();
            }

            try (FileInputStream in = new FileInputStream(original.getFileDescriptor());
                 FileOutputStream out = new FileOutputStream(copy)) {
                byte[] buffer = new byte[1024];
                while (true) {
                    int numRead = in.read(buffer);
                    if (numRead == -1) {
                        break;
                    }
                    out.write(buffer, 0, numRead);
                }
            } catch (Exception e) {
                e.printStackTrace();
            }

            StringBuilder parsedText = new StringBuilder();
            try {
                PdfReader reader = new PdfReader(copy.getAbsolutePath());
                for (int i = 0; i < reader.getNumberOfPages(); i++) {
                    parsedText.append(PdfTextExtractor.getTextFromPage(reader, i + 1).trim()).append("\n");
                }
                reader.close();
            } catch (Exception e) {
                e.printStackTrace();
                System.out.println(e);
            }

            SerialPortPrinterNew mSerialPrinter = new SerialPortPrinterNew();
            PrinterManager mSerialPrinterManager = new PrinterManager(mSerialPrinter, PrinterManager.TYPE_PAPER_WIDTH_58MM);

            mSerialPrinterManager.setStringEncoding("ISO-8859-2");
            mSerialPrinter.selectPrinter("/dev/ttyS3", 9600);
            mSerialPrinterManager.connect();

            mSerialPrinterManager.sendCmd(new byte[] { 27, 64 });
            mSerialPrinterManager.cmdSetAlignMode(PrinterManager.ALIGN_MIDDLE);
            mSerialPrinterManager.cmdSetCodePageTable(PrinterManager.CODE_PAGE_ISO_8859_2);

            String[] racun = parsedText.toString().split("\n");

            mSerialPrinterManager.sendData("================================");
            for (String linija_racuna : racun) {
                if(linija_racuna.contains("Poreski")) {
                    mSerialPrinterManager.cmdSetAlignMode(PrinterManager.ALIGN_LEFT);
                    mSerialPrinterManager.sendData("--------------------------------");
                    mSerialPrinterManager.sendData(linija_racuna);
                    mSerialPrinterManager.cmdLineFeed();
                    mSerialPrinterManager.sendData("--------------------------------");
                    mSerialPrinterManager.cmdLineFeed();
                    continue;
                }
                if(linija_racuna.contains("Redni broj")) {
                    mSerialPrinterManager.sendData("--------------------------------");
                    mSerialPrinterManager.sendData(linija_racuna);
                    mSerialPrinterManager.cmdLineFeed();
                    mSerialPrinterManager.sendData("--------------------------------");
                    mSerialPrinterManager.cmdLineFeed();
                    continue;
                }
                if(linija_racuna.contains("Kupac")) {
                    mSerialPrinterManager.sendData("--------------------------------");
                    mSerialPrinterManager.sendData(linija_racuna);
                    mSerialPrinterManager.cmdLineFeed();
                    mSerialPrinterManager.sendData("-------------------------------");
                    mSerialPrinterManager.cmdLineFeed();
                    continue;
                }
                if (linija_racuna.contains("Artikal")) {
                    mSerialPrinterManager.sendData("--------------------------------");
                    mSerialPrinterManager.sendData(linija_racuna);
                    mSerialPrinterManager.cmdLineFeed();
                    mSerialPrinterManager.sendData("--------------------------------");
                    mSerialPrinterManager.cmdLineFeed();
                    continue;
                }
                if (linija_racuna.contains("Struktura cijene")) {
                    mSerialPrinterManager.sendData("--------------------------------");
                    mSerialPrinterManager.sendData(linija_racuna);
                    mSerialPrinterManager.cmdLineFeed();
                    mSerialPrinterManager.sendData("--------------------------------");
                    mSerialPrinterManager.cmdLineFeed();
                    continue;
                }
                if (linija_racuna.contains("Ukupna osnovica")) {
                    mSerialPrinterManager.sendData("--------------------------------");
                    mSerialPrinterManager.cmdLineFeed();
                    mSerialPrinterManager.sendData(linija_racuna);
                    mSerialPrinterManager.cmdLineFeed();
                    continue;
                }
                if (linija_racuna.contains("Ukupan porez")) {
                    mSerialPrinterManager.sendData(linija_racuna);
                    mSerialPrinterManager.cmdLineFeed();
                    mSerialPrinterManager.sendData("--------------------------------");
                    mSerialPrinterManager.cmdLineFeed();
                    continue;
                }
                if(linija_racuna.contains("EFIKOD")) {
                    mSerialPrinterManager.sendData("================================");
                    mSerialPrinterManager.cmdLineFeed();
                    break;
                }

                mSerialPrinterManager.sendData(linija_racuna);
                mSerialPrinterManager.cmdLineFeed();
            }

			String link = racun[racun.length - 3] + racun[racun.length - 2] + racun[racun.length - 1];

            mSerialPrinterManager.cmdSetAlignMode(PrinterManager.ALIGN_MIDDLE);
            mSerialPrinterManager.printQRCode(link, 48, 49, 4);
            mSerialPrinterManager.sendData("================================");

            mSerialPrinterManager.cmdLineFeed();
            mSerialPrinterManager.cmdLineFeed();
            mSerialPrinterManager.cmdLineFeed();
            mSerialPrinterManager.cmdLineFeed();
            mSerialPrinter.mOutputStream.flush();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            printJob.complete();
        }
    }

    public final class PipoPrinterDiscoverySession extends PrinterDiscoverySession {

        private final Handler mSesionHandler = new Handler(getMainLooper());

        private final List<PrinterInfo> mPrinters = new ArrayList<>();

        public PipoPrinterDiscoverySession() {
            PrinterInfo printerInfo = new PrinterInfo
                    .Builder(generatePrinterId("Pipo Printer"), "Pipo Printer", PrinterInfo.STATUS_IDLE)
                    .build();

            mPrinters.add(printerInfo);
            addPrinters(mPrinters);
        }

        @Override
        public void onStartPrinterDiscovery(@NonNull List<PrinterId> priorityList) {
            System.out.print("Funkcija: onStartPrinterDiscovery");
        }

        @Override
        public void onStopPrinterDiscovery() {
            System.out.print("Funkcija: onStartPrinterDiscovery");
        }

        @Override
        public void onValidatePrinters(@NonNull List<PrinterId> printerIds) {
            System.out.print("Funkcija: onStartPrinterDiscovery");
        }

        private PrinterInfo findPrinterInfo(PrinterId printerId) {
            List<PrinterInfo> printers = getPrinters();
            final int printerCount = getPrinters().size();
            for (int i = 0; i < printerCount; i++) {
                PrinterInfo printer = printers.get(i);
                if (printer.getId().equals(printerId)) {
                    return printer;
                }
            }
            return null;
        }

        @Override
        public void onStartPrinterStateTracking(@NonNull PrinterId printerId) {
            System.out.print("Funkcija: onStartPrinterDiscovery");
            Log.i(LOG_TAG, "FakePrinterDiscoverySession#onStartPrinterStateTracking()");
            PrinterInfo printer = findPrinterInfo(printerId);
            if (printer != null) {
                PrinterCapabilitiesInfo.Builder builder = new PrinterCapabilitiesInfo.Builder(printerId);
                builder.setMinMargins(new PrintAttributes.Margins(0, 0, 0, 0));
                builder.addMediaSize(new PrintAttributes.MediaSize("58mm", "58mm", 2283, 2283 * 4), true);
                builder.addResolution(new PrintAttributes.Resolution("58mm", "58mm", 182, 182), true);
                builder.setColorModes(PrintAttributes.COLOR_MODE_MONOCHROME, PrintAttributes.COLOR_MODE_MONOCHROME);
                printer = new PrinterInfo.Builder(printer)
                        .setCapabilities(builder.build())
                        .build();

                List<PrinterInfo> printers = new ArrayList<>();
                printers.add(printer);
                addPrinters(printers);
            }
        }

        @Override
        public void onStopPrinterStateTracking(@NonNull PrinterId printerId) {
            System.out.print("Funkcija: onStartPrinterDiscovery");
        }

        @Override
        public void onDestroy() {
            System.out.print("Funkcija: onStartPrinterDiscovery");
        }
    }
}

