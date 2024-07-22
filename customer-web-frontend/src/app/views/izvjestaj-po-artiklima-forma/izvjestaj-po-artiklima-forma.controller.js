angular
    .module('app')
    .controller('IzvjestajPoArtiklimaFormaController', IzvjestajPoArtiklimaFormaController);

IzvjestajPoArtiklimaFormaController.$inject = ['$rootScope', '$scope', '$templateRequest', 'fisReportService', 'fisCustomerApi', '$compile'];

function IzvjestajPoArtiklimaFormaController($rootScope, $scope, $templateRequest, fisReportService, fisCustomerApi, $compile) {
    let ctrl = this;

    ctrl.pageFormat = '58mm';

    ctrl.datumOd = fisReportService.getDayRelative(-1);

    let endOfDay = fisReportService.getDayRelative();
    endOfDay.setHours(23, 59, 59, 0);

    ctrl.datumDo = endOfDay;

    ctrl.fetchReport = fetchReport;

    function fetchReport(start, end) {
        $rootScope.showLoader = true;
        return fisCustomerApi.views__izvjestaj_po_artiklima_forma__on_submit({
            start: fisReportService.formatDate(start),
            end: fisReportService.formatDate(end),
            buyerId: ctrl.buyerId,
            pageFormat: ctrl.pageFormat
        }).then(function(data) {
            let templateUrl;
            if (ctrl.pageFormat === '58mm') {
                templateUrl = 'app/views/izvjestaj-po-artiklima-forma/report-58mm.template.html';
            } else if (ctrl.pageFormat === 'A4') {
                templateUrl = 'app/views/izvjestaj-po-artiklima-forma/report-a4.template.html';
            } else {
                throw Error('Invalid page format.');
            }

            $templateRequest(templateUrl).then(function(html) {
                let container = angular.element(html);
                let containerScope = $scope.$new(true);
                containerScope.data = data;
                let compiledElement = $compile(container)(containerScope);

                const iframe = document.createElement('iframe')
                iframe.style.position = 'fixed';
                iframe.style.top = '110%';
                iframe.style.left = '110%';
                iframe.srcdoc = '<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=2.0, maximum-scale=1.0, minimum-scale=1.0"><meta http-equiv="X-UA-Compatible" content="ie=edge"><title>Document</title></head><body></body></html>';
                document.body.appendChild(iframe);
                iframe.onload = function() {
                    const iframeDocument = iframe.contentDocument || iframe.contentWindow.document;

                    const metaElement = document.createElement('meta');
                    metaElement.name = 'viewport';
                    metaElement.content = 'width=device-width, user-scalable=no, initial-scale=2.0, maximum-scale=1.0, minimum-scale=1.0';
                    iframeDocument.head.appendChild(metaElement);

                    const styleElement = document.createElement('style');
                    styleElement.innerHTML = '';

                    iframeDocument.head.appendChild(compiledElement[0]);
                    iframeDocument.body.appendChild(compiledElement[2]);
                    iframe.contentWindow.focus();
                    iframe.contentWindow.print();
                }
            });
        }).finally(function() {
            $rootScope.showLoader = false;
        });
    }
}
