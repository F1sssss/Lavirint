angular
    .module('app')
    .service('fisReportService', fisReportService);

fisReportService.$inject = ['$rootScope', 'api', 'stampac'];

function fisReportService($rootScope, api, stampac) {
    return {
        getDayRelative: getDayRelative,
        getMonthStartRelative: getMonthStartRelative,
        getMonthEndRelative: getMonthEndRelative,
        presjekStanja: presjekStanja,
        dnevniIzvjestaj: dnevniIzvjestaj,
        periodicniIzvjestaj: periodicniIzvjestaj,
        zurnal: zurnal,
        poGrupamaArtikala: poGrupamaArtikala,
        poArtiklima: poArtiklima,
        formatDate: formatDate
    }

    function formatDate(date) {
        return new Date(date.getTime() - (date.getTimezoneOffset() * 60000))
            .toISOString()
    }


    function getMonthStartRelative(offset) {
        if (offset === undefined) {
            offset = 0;
        }

        const date = new Date();
        const month = date.getMonth() + offset;
        const year = date.getFullYear();
        return new Date(year, month, 1);
    }

    function getMonthEndRelative(offset) {
        if (offset === undefined) {
            offset = 0;
        }

        const currentDate = new Date();
        const month = currentDate.getMonth() + offset;
        const year = currentDate.getFullYear();

        let date = new Date(year, month + 1, 0)
        date.setHours(23, 59, 59, 0);
        return date;
    }

    function getDayRelative(offset) {
        if (offset === undefined) {
            offset = 0;
        }

        let date = new Date();
        date.setDate(date.getDate() + offset);
        date.setHours(0, 0, 0, 0);
        return date;
    }

    function presjekStanja() {
        $rootScope.showLoader = true;
        $rootScope.showSidebar = false;
        return stampac.stampaj('/api/customer/izvjestaj/presjek_stanja')
            .finally(function() {
                $rootScope.showLoader = false;
            });
    }

    function dnevniIzvjestaj(datum) {
        $rootScope.showLoader = true;
        return stampac.stampaj('/api/customer/izvjestaj/dnevni/' + formatDate(datum))
            .finally(function() {
                $rootScope.showLoader = false;
            });
    }

    function periodicniIzvjestaj(datumOd, datumDo) {
        $rootScope.showLoader = true;
        return stampac.stampaj('/api/customer/izvjestaj/periodicni/' + formatDate(datumOd) + '/' + formatDate(datumDo))
            .finally(function() {
                $rootScope.showLoader = false;
            });
    }

    function zurnal(datumOd, datumDo) {
        $rootScope.showLoader = true;
        return stampac.stampaj('/api/customer/izvjestaj/zurnal/' + formatDate(datumOd) + '/' + formatDate(datumDo))
            .finally(function() {
                $rootScope.showLoader = false;
            });
    }

    function poGrupamaArtikala(datumOd, datumDo) {
        $rootScope.showLoader = true;
        return stampac.stampaj('/api/customer/izvjestaj/po-grupama-artikala/' + formatDate(datumOd) + '/' + formatDate(datumDo))
            .finally(function() {
                $rootScope.showLoader = false;
            });
    }

    function poArtiklima(datumOd, datumDo) {
        $rootScope.showLoader = true;
        return stampac.stampaj('/api/customer/izvjestaj/po-artiklima/' + formatDate(datumOd) + '/' + formatDate(datumDo))
            .finally(function() {
                $rootScope.showLoader = false;
            });
    }
}