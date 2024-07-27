angular
    .module('app')
    .controller('FakturaUnosPoGrupamaController', FakturaUnosPoGrupamaController);

FakturaUnosPoGrupamaController.$inject = [
    '$rootScope', '$scope', '$state', '$uibModal', '$timeout', '$window', 'api', 'stampac', 'grupe_artikala',
    'invoiceFactory', 'fisConfig', 'fisGui', 'fisModal', 'breakpointsService',
    '$cookies'
];

function FakturaUnosPoGrupamaController(
    $rootScope, $scope, $state, $uibModal, $timeout, $window, api, stampac, grupe_artikala,
    invoiceFactory, fisConfig, fisGui, fisModal, breakpointsService,
    $cookies
) {
    const ctrl = this;

    ctrl.invoiceTab = 'items';

    ctrl.grupe_artikala = grupe_artikala;
    ctrl.zalihe = undefined;
    ctrl.odabrana_grupa = undefined;

    ctrl.grupaArtikalaGrid = createGrid(
        grupe_artikala,
        6,
        4,
        'unosPoGrupama.grupaArtikalaGrid',
        1

    );

    ctrl.artikalGrid = createGrid(
        [],
        3,
        3,
        'unosPoGrupama.artikalGrid'
    );

    ctrl.selectItemGroup = selectItemGroup;
    ctrl.deselectItemTemplateGroup = deselectItemTemplateGroup;
    ctrl.nextPage = nextPage;
    ctrl.prevPage = prevPage;
    ctrl.editQuantityInNumericModal = editQuantityInNumericModal;
    ctrl.odaberiZalihuTablet = odaberiZalihuTablet;
    ctrl.incrementQuantity = incrementQuantity;
    ctrl.decrementQuantity = decrementQuantity;
    ctrl.azurirajStavku = azurirajStavku;
    ctrl.onBuyerSelect = onBuyerSelect;
    ctrl.showBuyerUpdateModal = showBuyerUpdateModal;
    ctrl.upis = upis;
    ctrl.upisSaKupcem = upisSaKupcem;
    ctrl.porudzbina = porudzbina;
    ctrl.updateGridLayout = updateGridLayout;

    // -----------------------------------------------------------------------------------------------------------------

    ctrl.racun = invoiceFactory.create();

    // -----------------------------------------------------------------------------------------------------------------

    function updateOrCreateItemFromItemTempate(itemTemplate, quantity) {
        if (itemTemplate.invoiceItem === null) {
            itemTemplate.invoiceItem = invoiceFactory.addItemFromItemTemplate(ctrl.racun, itemTemplate);
        }
        itemTemplate.invoiceItem.kolicina = quantity;
        invoiceFactory.recalculateItem(ctrl.racun, itemTemplate.invoiceItem);

        if (breakpointsService.ls(breakpointsService.keys.md)) {
            ctrl.invoiceTab = 'product_list';
        } else {
            ctrl.invoiceTab = 'items';
        }
    }

    function removeItemFromInvoice(itemTemplate) {
        let index = null;
        for (let ii = 0; ii < ctrl.racun.stavke.length; ii++) {
            if (itemTemplate.artikal_id === ctrl.racun.stavke[ii].magacin_zaliha.artikal_id) {
                index = ii;
                break;
            }
        }

        itemTemplate.invoiceItem.kolicina = 0;
        itemTemplate.invoiceItem = null;
        ctrl.racun.stavke.splice(index, 1);
    }

    function selectItemGroup(grupa_artikala) {
        fisGui.wrapInLoader(function() {
            return api.grupaArtikala.poId.zaliha.listaj(grupa_artikala.id).then(function(data) {
                ctrl.odabrana_grupa = grupa_artikala;
                ctrl.zalihe = data;

                updateGridSource(ctrl.artikalGrid, data);
                updateGridPage(ctrl.artikalGrid, 1);

                for (let ii = 0; ii < ctrl.zalihe.length; ii++) {
                    ctrl.zalihe[ii].invoiceItem = null;
                    for (let jj = 0; jj < ctrl.racun.stavke.length; jj++) {
                        if (ctrl.zalihe[ii].artikal_id === ctrl.racun.stavke[jj].magacin_zaliha.artikal.id) {
                            ctrl.zalihe[ii].invoiceQuantity = ctrl.racun.stavke[jj].kolicina;
                            ctrl.zalihe[ii].invoiceItem = ctrl.racun.stavke[jj];
                        }
                    }
                }
            });
        });
    }

    function deselectItemTemplateGroup() {
        ctrl.odabrana_grupa = undefined;
        ctrl.zalihe = undefined;
    }


    function nextPage(grid, cycle) {
        cycle = cycle === undefined ? true : cycle;

        let newPage = grid.currentPage + 1;
        if (grid.currentPage === grid.totalPages) {
            if (cycle) {
                newPage = 1;
            } else {
                return;
            }
        }

        ctrl.grid = updateGridPage(grid, newPage, cycle);
    }
    function prevPage(grid, cycle) {
        cycle = cycle === undefined ? true : cycle;

        let newPage = grid.currentPage - 1;
        if (grid.currentPage === 1) {
            if (cycle) {
                newPage = grid.totalPages;
            } else {
                return;
            }
        }

        ctrl.grid = updateGridPage(grid, newPage, cycle);
    }

    function createGrid(dataSource, defaultRowNum, defaultColNum, cookieKey, currentPage) {
        let grid = {};

        let cookieRowNum = $cookies.get(cookieKey + '.rowNum');
        if (cookieRowNum === undefined) {
            grid.rowNum = defaultRowNum;
            $cookies.put('unosPoGrupama.grupaArtikalaGrid.rowNum', defaultRowNum);
        } else {
            grid.rowNum = parseInt(cookieRowNum);
        }

        let cookieColNum = $cookies.get(cookieKey + '.colNum');
        if (cookieColNum === undefined) {
            grid.colNum = defaultColNum;
            $cookies.put('unosPoGrupama.grupaArtikalaGrid.colNum', defaultColNum);
        } else {
            grid.colNum = parseInt(cookieColNum);
        }

        if ($cookies.get(cookieKey + '.colNum') === undefined) {
            $cookies.put('unosPoGrupama.grupaArtikalaGrid.colNum', 4);
        }

        grid.currentPage = currentPage ? currentPage : 1;
        grid.itemsPerPage = grid.rowNum * grid.colNum;
        grid.cookieKey = cookieKey;

        updateGridSource(grid, dataSource);
        updateGridPage(grid, grid.currentPage);

        return grid;
    }

    function updateGridSource(grid, dataSource) {
        grid.totalPages = Math.ceil(dataSource.length / grid.itemsPerPage);
        if (grid.totalPages === 0) {
            grid.totalPages = 1;
        }
        grid.dataSource = dataSource;
    }

    function updateGridLayout(grid, colNum, rowNum) {
        grid.colNum = colNum;
        $cookies.put(grid.cookieKey + '.colNum', colNum);
        grid.rowNum = rowNum;
        $cookies.put(grid.cookieKey + '.rowNum', rowNum);
        grid.itemsPerPage = colNum * rowNum;
        grid.totalPages = Math.ceil(grid.dataSource.length / grid.itemsPerPage);
        updateGridPage(grid, 1);
    }

    function updateGridPage(grid, page) {
        grid.currentPage = page;
        grid.currentPageIndex = page - 1;
        grid.rows = [];

        for (let ii = 0; ii < grid.rowNum; ii++) {
            let start = grid.currentPageIndex * grid.itemsPerPage + (ii * grid.colNum);
            let end = grid.currentPageIndex * grid.itemsPerPage + ((ii * grid.colNum) + grid.colNum);

            let arr = [];
            for (let jj = start; jj < end; jj++) {
                if (jj < grid.dataSource.length) {
                    arr.push(grid.dataSource[jj]);
                } else {
                    arr.push(null);
                }
            }
            grid.rows.push(arr);
        }

        if (grid.rows.length < grid.rowNum) {
            for (let ii = 0; ii < grid.rowNum; ii++) {
                grid.rows.push([]);
            }
        }

        for (let ii = 0; ii < grid.rows.length; ii++) {
            let lll = grid.colNum - grid.rows[ii].length;
            if (lll > 0) {
                for (let jj = 0; jj < lll; jj++) {
                    grid.rows[ii].push(null);
                }
            }
        }

        return grid;
    }

    function editQuantityInNumericModal(itemTemplate) {
        fisModal.numericInput({ value: itemTemplate.invoiceQuantity }).then(function(result) {
            if (result.isConfirmed) {
                updateOrCreateItemFromItemTempate(itemTemplate, result.value);
            }
        });
    }

    function odaberiZalihuTablet(zaliha) {
        if (zaliha.artikal.jedinica_mjere.naziv === 'kom') {
            incrementQuantity(zaliha);
        } else {
            editQuantityInNumericModal(zaliha);
        }
    }

    function incrementQuantity(itemTemplate) {
        let quantity = 1;
        if (itemTemplate.invoiceItem !== null) {
            quantity = itemTemplate.invoiceItem.kolicina + 1
        }

        updateOrCreateItemFromItemTempate(itemTemplate, quantity);
    }

    function decrementQuantity(itemTemplate) {
        let quantity = Math.max(0, itemTemplate.invoiceItem.kolicina - 1);
        if (itemTemplate.invoiceItem !== null) {
            if (quantity === 0) {
                removeItemFromInvoice(itemTemplate);
            } else {
                updateOrCreateItemFromItemTempate(itemTemplate, quantity);
            }
        }
    }

    function azurirajStavku(index) {
        let cachedInvoiceTemplateId = ctrl.racun.stavke[index].magacin_zaliha.artikal_id;
        fisModal.invoiceItemEdit(ctrl.racun, index).then(function(result) {
            if (!result.isConfirmed) {
                return;
            }

            let zaliha = ctrl.artikalGrid.dataSource.find(function(zaliha) {
                return zaliha.artikal_id === cachedInvoiceTemplateId;
            });

            if (result.action === 'delete') {
                zaliha.invoiceItem = null;
                return;
            }

            if (result.action === 'save') {
                zaliha.invoiceItem = ctrl.racun.stavke[index];
            }
        });
    }

    function onBuyerSelect($model) {
        ctrl.komitent = $model;
        ctrl.racun.komitent_id = $model.id;
    }

    function showBuyerUpdateModal() {
        fisModal.buyerUpdateModal(ctrl.racun.komitent_id).then(function(result) {
            if (result.isConfirmed) {
                ctrl.komitent = result.komitent;
                ctrl.komitent_id = result.komitent.id;
            }
        });
    }

    function upisSaKupcem(paymentMethodTypeId) {
        if (ctrl.racun.stavke.length === 0) {
            fisModal.confirm({
                headeText: 'Račun je prazan',
                headerIcon: 'fa fa-exclamation-triangle text-danger',
                bodyText: 'Dodajte stavke pa probajte ponovo.'
            });
            return;
        }

        if (paymentMethodTypeId === 8 && !ctrl.racun.komitent_id) {
            fisModal.invoiceBuyerSelectModal(ctrl.racun).then(function(result) {
                if (result.isConfirmed) {
                    sendData(paymentMethodTypeId);
                }
            });
        }
    }

    function upis(paymentMethodTypeId) {
        if (ctrl.racun.stavke.length === 0) {
            fisModal.confirm({
                headeText: 'Račun je prazan',
                headerIcon: 'fa fa-exclamation-triangle text-danger',
                bodyText: 'Dodajte stavke pa probajte ponovo.'
            });
            return;
        }

        sendData(paymentMethodTypeId);
    }

    function sendData(paymentMethodTypeId) {
        let podaci = angular.copy(ctrl.racun);

        podaci.is_cash = fisConfig.getPaymentMethodById(paymentMethodTypeId).is_cash;
        podaci.payment_methods = [invoiceFactory.createPaymentMethod(paymentMethodTypeId)];

        let currentTime = new Date();

        podaci.poreski_period = angular.copy(currentTime);
        podaci.poreski_period.setDate(1);
        podaci.poreski_period.setHours(0, 0, 0, 0);
        podaci.poreski_period = moment(podaci.poreski_period).format()

        podaci.datumfakture = moment(podaci.datumfakture).format()

        podaci.datumvalute = angular.copy(currentTime);
        podaci.datumvalute = moment(podaci.datumvalute).format()


        $rootScope.showLoader = true;
        fisGui.wrapInLoader(function() {
            return api.api__faktura__dodaj(podaci).then(function (data) {
                return data;
            });
        }).then(function(data) {
            if (data.result.is_success) {
                return stampac.stampajFakturu(
                    data.invoice.id,
                    fisConfig.user.podesavanja_aplikacije.podrazumijevani_tip_stampe
                ).then(function() {
                    $state.reload();
                });
            } else {
                return fisModal.confirm({
                    headerIcon: 'fa fa-exclamation-circle text-danger',
                    headerText: 'Grеška',
                    bodyText: data.result.message
                });
            }
        });
    }

    function porudzbina(){
        if (ctrl.racun.stavke.length === 0) {
            fisModal.confirm({
                headeText: 'Račun je prazan',
                headerIcon: 'fa fa-exclamation-triangle text-danger',
                bodyText: 'Dodajte stavke pa probajte ponovo.'
            });
            return;
        }

        sendData();
    }

    function sendData() {
        let podaci = angular.copy(ctrl.racun);

        podaci.is_cash = false;

        let currentTime = new Date();

        podaci.poreski_period = angular.copy(currentTime);
        podaci.poreski_period.setDate(1);
        podaci.poreski_period.setHours(0, 0, 0, 0);
        podaci.poreski_period = moment(podaci.poreski_period).format()

        podaci.datumfakture = moment(podaci.datumfakture).format()

        podaci.datumvalute = angular.copy(currentTime);
        podaci.datumvalute = moment(podaci.datumvalute).format()


        $rootScope.showLoader = true;
        fisGui.wrapInLoader(function() {
            return api.api__order__create(podaci).then(function (data) {
                return data;
            });
        }).then(function(data) {
            if (data.result.is_success) {
                return stampac.stampajFakturu(
                    data.invoice.id,
                    fisConfig.user.podesavanja_aplikacije.podrazumijevani_tip_stampe
                ).then(function() {
                    $state.reload();
                });
            } else {
                return fisModal.confirm({
                    headerIcon: 'fa fa-exclamation-circle text-danger',
                    headerText: 'Grеška',
                    bodyText: data.result.message
                });
            }
        });
    }
}