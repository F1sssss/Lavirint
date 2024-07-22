angular
    .module('app')
    .service('stampac', stampac);

stampac.$inject = ['$rootScope', '$window', '$q', '$timeout', 'api'];

function stampac($rootScope, $window, $q, $timeout, api) {
    let container = document.createElement('div');
    $window.document.body.append(container);

    return {
        stampaj: printV2,
        stampajFakturu: stampajFakturu,
        stampajDokument: stampajDokument,
        stampajKarticuKupca: stampajKarticuKupca,
        stampajKnjiznoOdobrenje: stampajKnjiznoOdobrenje
    }

    function stampajFakturu(fakturaId, tipStampe) {
        return printV2('/api/customer/faktura/' + fakturaId + '/stampa/' + tipStampe);
    }

    function stampajDokument(fakturaId) {
        return print('/api/customer/faktura/' + fakturaId + '/dokument/listaj');
    }

    function stampajKarticuKupca(komitentId) {
        return print('/api/customer/frontend/buyer/' + komitentId + '/state');
    }

    function stampajKnjiznoOdobrenje(creditNoteId) {
        return printV2('/api/customer/credit_note/' + creditNoteId + '/document');
    }

    function printV2(src) {
        const deferred = $q.defer();

        container.innerHTML = '';

        const iframe = document.createElement('iframe');
        iframe.src = src;
        iframe.style.position = 'fixed';
        iframe.style.top = '110%';
        iframe.style.left = '110%';
        iframe.onload = function () {
            iframe.contentWindow.matchMedia('print').addEventListener('change', function () {
                // U slučaju mobilnog browser-a event onafterprint se pokreće 2 puta
                // Jednom prije prelaska na aplikaciju za print, a zatim nakon zatvaranja
                // aplikacije za print. Ukoliko se iframe ukloni, u print aplikaciji
                // se prikazuje prazna stranica i zato se ovdje ne smije ukloniti.
                // iframe.remove();

                $rootScope.showLoader = false;
                $rootScope.$apply();
                deferred.resolve();
            });
            iframe.contentWindow.focus();
            iframe.contentWindow.print();
        }

        container.append(iframe);

        return deferred.promise;
    }

    function print(src) {
        const deferred = $q.defer();

        container.innerHTML = '';

        const iframe = document.createElement('iframe');
        iframe.src = src;
        iframe.className = 'd-none';
        iframe.onload = function () {
            iframe.contentWindow.print();
            $timeout(function() {
                $rootScope.showLoader = false;
                $rootScope.$apply();
                deferred.resolve();
            }, 100)
        }

        container.append(iframe);

        return deferred.promise;
    }
}