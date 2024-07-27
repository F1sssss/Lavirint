angular
    .module('app')
    .run(run);

run.$inject = [
    '$rootScope', '$transitions', '$q', '$timeout', '$window', '$state', 'api', 'fisGui', 'breakpointsService',
    'fisReportService', 'fisModal', 'fisConfig', 'fisInvoiceConfig', 'fisCustomerApi'
];

function run(
    $rootScope, $transitions, $q, $timeout, $window, $state, api, fisGui, breakpointsService,
    fisReportService, fisModal, fisConfig, fisInvoiceConfig, fisCustomerApi
) {

    $rootScope.currency = 'EUR';  // All price input is in domestic currency

    $rootScope.showLoader = false;

    $rootScope.fisConfig = fisConfig;

    $rootScope.fisModal = fisModal;
    $rootScope.fisReportService = fisReportService;

    $rootScope.math = Math;

    $rootScope.breakpoints = breakpointsService;

    $rootScope.isCompanyCollapsed = true;
    $rootScope.isRacuniCollapsed = true;
    $rootScope.isCreditNoteCollapsed = true;
    $rootScope.isArtikliCollapsed = true;
    $rootScope.isPartneriCollapsed = true;
    $rootScope.isReportCollapsed = true;
    $rootScope.selectedOrders = {};

    $rootScope.goToHomepage = goToHomepage;

    $rootScope.logout = logout;

    $transitions.onStart({}, transitionsOnStart);

    $transitions.onBefore({ to: 'prodaja-racun-unos' }, onBeforeRequireDeposit);
    $transitions.onFinish({}, onTransitionFinishCheckDuePayments);

    $transitions.onFinish({}, transitionsOnFinish);

    angular.element($window).on('resize', onResize);

    $rootScope.$watch('showSidebar', onShowSidebar);

    $rootScope.setCertificateExpirationDate = setCertificateExpirationDate;

    setCertificateExpirationDate(fisConfig.certificate_expiration_date);

    function setCertificateExpirationDate(value) {
        $rootScope.certificate_expiration_date = value;
        $rootScope.certificate_status = 'valid';
        if ($rootScope.certificate_expiration_date === null) {
            $rootScope.certificate_status = 'no-certificate';
        } else {
            const diff = new Date($rootScope.certificate_expiration_date).getTime() - new Date().getTime();
            if (diff <= 0) {
                $rootScope.certificate_status = 'invalid';
            } else if (diff < 604800000) {
                $rootScope.certificate_status = 'expires-soon';
            } else if (diff < 2592000000) {
                $rootScope.certificate_status = 'expires-warning';
            } else {
                $rootScope.certificate_status = 'valid';
            }
        }
    }

    function goToHomepage() {
        if (fisConfig.user.podesavanja_aplikacije.pocetna_stranica === '/prodaja/racun/unos') {
            $state.go('prodaja-racun-unos', null, { reload: true });
        } else if (fisConfig.user.podesavanja_aplikacije.pocetna_stranica === '/racun/opsti_unos') {
            $state.go('regularInvoiceInput', null, { reload: true });
        } else if (fisConfig.user.podesavanja_aplikacije.pocetna_stranica === '/faktura/grupe/unos') {
            $state.go('faktura-unos-po-grupama', null, { reload: true });
        }
    }

    function transitionsOnStart(transition) {
        return $q.all([
            fisGui.showLoader(),
            fisGui.hideSidebar(),
            $timeout(function() {
                $window.document.body.scrollTop = document.documentElement.scrollTop = 0;
            }, 150)
        ]).finally(function() {
            return transition;
        });
    }

    function transitionsOnFinish(transition) {
        let to = transition.to();
        $rootScope.showDesktopTitle = to.showDesktopTitle !== undefined ? to.showDesktopTitle : false;
        $rootScope.title = to.title ? to.title : '';
        return fisGui.hideLoader();
    }

    function onBeforeRequireDeposit(transition) {
        let to = transition.to();
        let from = transition.from();

        fisGui.hideSidebar();
        return fisGui.wrapInLoader(function() {
            return api.stanje.listaj().then(function (data) {
                return data;
            });
        }).then(function(data) {
            if (!data.danasnji_depozit || data.danasnji_depozit.status !== 2) {
                return fisModal.depositNeededModal().then(function (result) {
                    if (result.isConfirmed) {
                        return transition.router.stateService.target('depozit', {'#': 'depozit-iznos'});
                    }

                    if (from.url === '^' && fisConfig.user.podesavanja_aplikacije.pocetna_stranica === to.url) {
                        return transition.router.stateService.target('faktura_pregled_redovnih', {
                            broj_stavki_po_stranici: fisInvoiceConfig.itemsPerPage,
                            broj_stranice: 1
                        });
                    }

                    return false;
                });
            } else {
                return transition;
            }
        });
    }

    function logout() {
        fisModal.confirmOrCancel({
            headerText: 'Odjava',
            bodyText: "Da li ste sigurni da želite da se odjavite?",
            confirmButtonText: 'Odjavi me',
            cancelButtonText: 'Odustani'
        }).then((result) => {
            if (result.isConfirmed) {
                api.korisnik.odjavi().then(function () {
                    if (result.isConfirmed) {
                        window.location.href = "./login.html"
                    }
                });
            }
        });
    }

    function onTransitionFinishCheckDuePayments() {
        return api.dospjelaFaktura.notifikacija.listaj().then(function(data) {
            return;

            if (data.notifications.length === 0) {
                return;
            }

            return fisModal.duePaymentNotificationModal(data).then(function() {
                let notificationIds = data.notifications.map(function(notification) {
                    return notification.id;
                });

                fisCustomerApi.on_transition_finish_check_due_payments__turn_off_notifications({
                    notificationIds: notificationIds
                });
            });
        });
    }

    function onResize() {
        const windowEl = angular.element($window);
        if (windowEl.width() >= 992 && $rootScope.showSidebar) {
            $rootScope.showSidebar = false;
            $rootScope.$apply();
        }
    }

    function onShowSidebar(newVal) {
        if (newVal === false) {
            $rootScope.isCompanyCollapsed = true;
            $rootScope.isRacuniCollapsed = true;
            $rootScope.isCreditNoteCollapsed = true;
            $rootScope.isArtikliCollapsed = true;
            $rootScope.isPartneriCollapsed = true;
            $rootScope.isReportCollapsed = true;
        }
    }
}
