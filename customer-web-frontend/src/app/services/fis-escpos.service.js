angular
    .module('escpos', [])
    .service('fisEscpos', fisEscpos);

fisEscpos.$inject = ['fisConfig'];

function fisEscpos(fisConfig) {
    let service = {};


    service.encoder = new TextEncoder();

    service.CODEPAGE = {};
    service.CODEPAGE._ISO_8859_2 = 36;

    service.LF = 10;
    service.ESC = 27;
    service.GS = 29;

    service.QRModel = {};
    service.QRModel._1 = 48;
    service.QRModel._2 = 49;

    service.QRErrorCorrection = {};
    service.QRErrorCorrection._L = 48; //  7%
    service.QRErrorCorrection._M = 49; // 15%
    service.QRErrorCorrection._Q = 50; // 25%
    service.QRErrorCorrection._H = 51; // 30%

    service.CPI_MODE = {};
    service.CPI_MODE._11 = 48;
    service.CPI_MODE._15 = 49;
    service.CPI_MODE._20 = 50;

    service.FONT = {};
    service.FONT._A = 0;
    service.FONT._B = 48;
    service.FONT._C = 49;
    service.FONT._D = 50;

    service.WEIGHT = {};
    service.WEIGHT._NORMAL = 0;
    service.WEIGHT._BOLD = 1;

    service.WIDTH = {};
    service.WIDTH._1 = 0;
    service.WIDTH._2 = 1;
    service.WIDTH._3 = 2;
    service.WIDTH._4 = 3;
    service.WIDTH._5 = 4;
    service.WIDTH._6 = 5;
    service.WIDTH._7 = 6;

    service.HEIGHT = {};
    service.HEIGHT._1 = 0;
    service.HEIGHT._2 = 1;
    service.HEIGHT._3 = 2;
    service.HEIGHT._4 = 3;
    service.HEIGHT._5 = 4;
    service.HEIGHT._6 = 5;
    service.HEIGHT._7 = 6;

    service.UNDERLINE = {};
    service.UNDERLINE._NONE = 48;
    service.UNDERLINE._ONE_DOT_THICK = 49;
    service.UNDERLINE._TWO_DOT_THICK = 50;

    service.JUSTIFICATION = {};
    service.JUSTIFICATION._LEFT = 48;
    service.JUSTIFICATION._CENTER = 49;
    service.JUSTIFICATION._RIGHT = 50;

    service.COLOR_MODE = {};
    service.COLOR_MODE._BLACK_ON_WHITE = 0;
    service.COLOR_MODE._WHITE_ON_BLACK = 1;


    service.setCodepage = setCodepage;

    service.selectFontA = selectFontA;
    service.selectFontC = selectFontC;
    service.selectFontD = selectFontD;

    service.initialize = initialize;
    service.setCPIMode = setCPIMode;
    service.setFont = setFont;
    service.setWeight = setWeight;
    service.setFontSize = setFontSize;
    service.setUnderline = setUnderline;
    service.setJustification = setJustification;
    service.setDefaultLineSpacing = setDefaultLineSpacing;
    service.setLineSpacing = setLineSpacing;
    service.setColorMode = setColorMode;
    service.feed = feed;
    service.write = write;
    service.writeLF = writeLF;

    service.wrapWords = wrapWords;
    service.lines = lines;

    service.qrcode = qrcode;


    service.printInvoice = printInvoice;
    service.sendToPrinter = sendToPrinter;

    return service

    function setCodepage(buffer, pageNumber) {
        buffer.push(service.ESC);
        buffer.push(116); // t
        buffer.push(pageNumber);
    }

    function selectFontA(buffer) {
        // PIPO: Selects smaller font.
        buffer.push(service.ESC, 80);
    }

    function selectFontC(buffer) {
        // PIPO: Selects bigger font.
        buffer.push(service.ESC, 84);
    }

    function selectFontD(buffer) {
        // PIPO: Selects smaller font.
        buffer.push(service.ESC, 85);
    }

    function initialize(buffer) {
        buffer.push(service.ESC, 64);
    }

    function setCPIMode(buffer, cpiMode) {
        if (Object.values(service.CPI_MODE).indexOf(cpiMode) < 0) {
            throw Error('Invalid font name value.');
        }

        buffer.push(service.ESC, 193, cpiMode);
    }

    function setFont(buffer, font) {
        if (Object.values(service.FONT).indexOf(font) < 0) {
            throw Error('Invalid font name value.');
        }

        buffer.push(service.ESC, 77, font);
    }

    function setWeight(buffer, weight) {
        if (Object.values(service.WEIGHT).indexOf(weight) < 0) {
            throw Error('Invalid font weight value.');
        }

        buffer.push(service.ESC, 69, weight);
    }


    function setFontSize(buffer, width, height) {
        if (Object.values(service.WIDTH).indexOf(width) < 0) {
            throw Error('Invalid font width value.');
        }

        if (Object.values(service.HEIGHT).indexOf(height) < 0) {
            throw Error('Invalid font height value.');
        }

        // GS ! n
        buffer.push(service.GS, 33, width << 4 | height);
    }

    function setUnderline(buffer, underline) {
        if (Object.values(service.UNDERLINE).indexOf(underline) < 0) {
            throw Error('Invalid underline value.');
        }

        buffer.push(service.ESC, 45, underline);
    }

    function setJustification(buffer, justification) {
        if (Object.values(service.JUSTIFICATION).indexOf(justification) < 0) {
            throw Error('Invalid justification value.');
        }

        buffer.push(service.ESC, 97, justification);
    }

    function setDefaultLineSpacing(buffer) {
        buffer.push(service.ESC, 50);
    }

    function setLineSpacing(buffer, lineSpacing) {
        if (lineSpacing < 0 || lineSpacing > 255) {
            throw Error('lineSpacing must be between 0 and 255');
        }

        buffer.push(service.ESC, 51, lineSpacing);
    }

    function setColorMode(buffer, colorMode) {
        if (Object.values(service.COLOR_MODE).indexOf(colorMode) < 0) {
            throw Error('Invalid justification value.');
        }

        buffer.push(service.GS, 66, colorMode);
    }

    function feed(buffer, nLines) {
        nLines = nLines === undefined ? 1 : nLines;

        if (nLines < 1 || nLines > 255) {
            throw Error('nLines must be between 1 and 255');
        }

        for (let ii = 0; ii < nLines; ii++) {
            buffer.push(service.LF);
        }
    }

    function write(buffer, text) {
        let bytes = service.encoder.encode(text);

        for (let ii = 0; ii < bytes.length; ii++) {
            buffer.push(bytes[ii]);
        }
    }

    function writeLF(buffer, text, nLines) {
        service.write(buffer, text);
        service.feed(buffer, nLines);
    }

    function wrapWords(text, maxLength) {
        if (!text || text.length <= maxLength) {
            return text;
        }

        let wrappedText = '';
        let currentLine = '';

        const words = text.split(' ');

        for (let i = 0; i < words.length; i++) {
            let word = words[i];

            if (word.length > maxLength) {
                wrappedText += currentLine.trim() + '\n';
                while(word.length > maxLength) {
                    wrappedText += word.substring(0, 32) + '\n';
                    word = word.substring(32, word.length);
                }
                currentLine = '';
                word = '-' + word;
            }

            if (currentLine.length + word.length > maxLength) {
                wrappedText += currentLine.trim() + '\n';
                currentLine = '';
            }

            currentLine += word + ' ';
        }

        return wrappedText + currentLine.trim();
    }

    function lines(buffer, text, maxLength) {
        let lines = wrapWords(text, maxLength).split('\n');

        for (let ii = 0; ii < lines.length; ii++) {
            service.write(buffer, lines[ii]);
            service.feed(buffer);
        }
    }

    function qrcode(buffer, data, model, size, errorCorrectionLevel) {
        // Function 065
        buffer.push(
            service.GS,
            40, // (
            107, // k
            4, // pL size of bytes
            0, // pH size of bytes
            49, // cn
            65, // fn
            model, // n1
            0 // n2
        )

        // Function 067
        buffer.push(
            service.GS,
            40, // (
            107, // k
            3, // pL size of bytes
            0, // pH size of bytes
            49, // cn
            67, // fn
            size // n
        );

        // Function 069
        buffer.push(
            service.GS,
            40, // (
            107, // k
            3, // pL size of bytes
            0, // pH size of bytes
            49, // cn
            69, // fn
            errorCorrectionLevel // n
        );

        let bytes = service.encoder.encode(data);

        // Function 080
        let numberOfBytes = bytes.length + 3;
        let pL = numberOfBytes % 256;
        let pH = Math.floor(numberOfBytes / 256);

        buffer.push(
            service.GS,
            40, // (
            107, // k
            pL, // pL size of bytes
            pH, // pH size of bytes
            49, // cn
            80, // fn
            48 // m
        );

        for (let ii = 0; ii < bytes.length; ii++) {
            buffer.push(bytes[ii]);
        }

        // Function 081
        buffer.push(
            service.GS,
            40, // (
            107, // k
            3, // pL size of bytes
            0, // pH size of bytes
            49, // cn
            81, // fn
            48 // m
        );
    }

    function printInvoice(invoice) {
        let buffer = [];

        service.initialize(buffer);
        service.setCodepage(buffer, service.CODEPAGE._ISO_8859_2);
        service.setFontSize(buffer, service.WIDTH._1, service.HEIGHT._1);
        service.setDefaultLineSpacing(buffer);

        service.setJustification(buffer, service.JUSTIFICATION._CENTER);
        service.writeLF(buffer, '--------------------------------');
        service.writeLF(buffer, fisConfig.user.firma.naziv);
        service.writeLF(buffer, 'PIB: ' + fisConfig.user.firma.pib);
        service.writeLF(buffer, fisConfig.user.firma.adresa);
        service.writeLF(buffer, fisConfig.user.firma.grad);
        service.writeLF(buffer, '--------------------------------');


        service.setJustification(buffer, service.JUSTIFICATION._LEFT);
        service.setFont(buffer, service.FONT._B);
        service.writeLF(buffer, 'Redni broj računa: ' + invoice.efi_ordinal_number);
        service.writeLF(buffer, 'Broj računa: ' + invoice.efi_broj_fakture);
        service.writeLF(buffer, 'Operater: ' + invoice.operater.ime);
        service.writeLF(buffer, 'Kod operatera: ' + invoice.operater.kodoperatera);

        for (let ii = 0; ii < invoice.payment_methods.length; ii++) {
            service.writeLF(buffer, 'Način plaćanja #' + ii + 1 + ': ' + invoice.payment_methods[ii].payment_method_type.description);
        }

        service.writeLF(buffer, 'IKOF: ' + invoice.ikof);
        service.writeLF(buffer, 'JIKR: ' + invoice.jikr);

        service.setFont(buffer, service.FONT._A);
        service.writeLF(buffer, '--------------------------------');
        service.setJustification(buffer, service.JUSTIFICATION._CENTER);
        service.writeLF(buffer, 'Kupac');
        service.setJustification(buffer, service.JUSTIFICATION._LEFT);
        service.writeLF(buffer, '--------------------------------')
        service.writeLF(buffer, 'Naziv/ime: ' + invoice.komitent.naziv);
        service.writeLF(buffer, invoice.komitent.tip_identifikacione_oznake.naziv + ': ' + invoice.komitent.naziv);
        service.writeLF(buffer, 'Adresa: ' + invoice.komitent.adresa + ', ' + invoice.komitent.grad);
        service.writeLF(buffer, 'Naziv/ime: ' + invoice.komitent.naziv);
        service.writeLF(buffer, '--------------------------------');

        let items_print = [];
        let item_padding = 4;
        let c1_max_length = 0;
        let c2_max_length = 0;
        let c3_max_length = 0;
        let c4_max_length = 0;
        for (let ii = 0; ii < invoice.stavke.length; ii++) {
            let item = invoice.stavke[ii];

            let obj = {};
            obj.naziv = item.naziv;

            obj.c1 = item.kolicina.toString();
            obj.c1_length = obj.c1.length;
            c1_max_length = Math.max(c1_max_length, obj.c1_length);

            obj.c2 = item.jedinicna_cijena_prodajna.toString();
            obj.c2_length = obj.c2.length;
            c2_max_length = Math.max(c2_max_length, obj.c2_length);

            obj.c3 = item.porez_procenat.toString();
            obj.c3_length = obj.c3.length;
            c3_max_length = Math.max(c3_max_length, obj.c3_length);

            obj.c4 = item.ukupna_cijena_prodajna.toString();
            obj.c4_length = obj.c4.length;
            c4_max_length = Math.max(c4_max_length, obj.c4_length);

            items_print.push(obj);
        }

        for (let ii = 0; ii < items_print.length; ii++) {
            let item = items_print[ii];

            if (ii > 0) {
                service.setLineSpacing(buffer,40);
            }
            service.writeLF(buffer, item.naziv);

            let left = item.c1 + ' x ' + item.c2 + ' (' + item.c3 + '%)';

            let lines = service.wrapWords(left, 32 - c4_max_length).split('\n');

            lines[0] = lines[0].padEnd(32 - c4_max_length, ' ') + item.c4.padStart(c4_max_length, ' ');
            for (let jj = 1; jj < lines.length; jj++) {
                lines[jj] = lines[jj].padEnd(32 - c4_max_length + item_padding, ' ');
            }

            let lastLine = lines.pop();

            for (let jj = 0; jj < lines.length; jj++) {
                buffer.writeLF(buffer, lines[jj]);
            }

            service.setDefaultLineSpacing(buffer);
            service.writeLF(buffer, lastLine);
        }

        service.writeLF(buffer, '--------------------------------');
        for (let ii = 0; ii < invoice.grupe_poreza.length; ii++) {
            let tax_group = invoice.grupe_poreza[ii];
            service.writeLF(buffer, ('Stopa ' + tax_group.porez_procenat + '%, osnovica').padEnd(19, ' ') + tax_group.ukupna_cijena_rabatisana.toString().padStart(13, ' '));
            service.writeLF(buffer, ('Stopa ' + tax_group.porez_procenat + '%, porez').padEnd(16, ' ') + tax_group.porez_iznos.toString().padStart(16, ' '));
            service.writeLF(buffer, '--------------------------------');
        }

        service.writeLF(buffer, 'Ukupna osnovica: ' + invoice.ukupna_cijena_rabatisana.toString().padStart(15, ' '))
        service.writeLF(buffer, 'Ukupan porez: ' + invoice.porez_iznos.toString().padStart(18, ' '))
        service.writeLF(buffer, '--------------------------------');
        service.writeLF(buffer, 'Puna cijena: ' + invoice.ukupna_cijena_puna.toString().padStart(19, ' '));
        service.writeLF(buffer, 'Popust: ' + invoice.rabat_iznos_prodajni.toString().padStart(24, ' '));
        service.setFontSize(buffer, service.WIDTH._2, service. HEIGHT._2);
        service.setWeight(buffer, service.WEIGHT._BOLD);
        service.writeLF(buffer, 'UKUPNO: ' + invoice.ukupna_cijena_prodajna.toString().padStart(8, ' '));
        service.setFontSize(buffer, service.WIDTH._1, service. HEIGHT._1);
        service.writeLF(buffer, '--------------------------------');
        service.setJustification(buffer, service.JUSTIFICATION._CENTER);
        service.qrcode(buffer, invoice.efi_verify_url, service.QRModel._1, 6, service.QRErrorCorrection._Q)
        service.writeLF(buffer, '--------------------------------');

        service.feed(buffer, 6);
        service.sendToPrinter(buffer);
    }

    function sendToPrinter(buffer) {
        let a = document.createElement('a');
        a.href = 'pipoprint:' + btoa(buffer.join(","));
        a.style = 'position: absolute; top: 110%; right: 100%;';
        document.body.append(a);
        a.click();
    }
}