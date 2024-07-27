angular
    .module('app')
    .config(routesConfig);

routesConfig.$inject = ['$urlRouterProvider', '$stateProvider', 'fisConfigProvider', 'fisInvoiceConfig'];

function routesConfig($urlRouterProvider, $stateProvider, fisConfigProvider, fisInvoiceConfig) {
    $urlRouterProvider.otherwise(fisConfigProvider.service.user.podesavanja_aplikacije.pocetna_stranica);

    $stateProvider.state({
        name: 'artikal-izmijeni',
        url: '/artikal/:id/izmijeni',
        templateUrl: 'app/views/artikal-izmjena/artikal-izmjena.template.html',
        controller: 'ArtikalIzmjenaController',
        controllerAs: 'ctrl',
        resolve: {
            initialData: ['$stateParams', 'api', function($stateParams, api) {
                return api.api__frontend__artikal__po_id__izmijeni($stateParams.id).then(function(data) {
                    return data;
                });
            }]
        }
    });

    $stateProvider.state({
        name: 'artikal-pregled-lista',
        url: '/artikal/pregled?broj_stranice&broj_stavki_po_stranici&pojam_za_pretragu',
        templateUrl: 'app/views/artikal-pregled-lista/artikal-pregled-lista.template.html',
        controller: 'ArtikalPregledListalController',
        controllerAs: 'ctrl',
        resolve: {
            /* @ngInject */
            strana: ['$stateParams', 'api', 'fisConfig', function ($stateParams, api, fisConfig) {
                return api.magacin.poId.zalihe.listaj(fisConfig.user.magacin_id, {
                    pojam_za_pretragu: $stateParams.pojam_za_pretragu,
                    broj_stavki_po_stranici: $stateParams.broj_stavki_po_stranici,
                    broj_stranice: $stateParams.broj_stranice
                });
            }]
        }
    });

    $stateProvider.state({
        name: 'artikal-unos',
        url: '/artikal/unos',
        templateUrl: 'app/views/artikal-unos/artikal-unos.template.html',
        controller: 'ArtikalUnosController',
        controllerAs: 'ctrl',
        resolve: {
            initialData: ['api', function(api) {
                return api.api__frontend__artikal__unos().then(function(data) {
                    return data;
                });
            }],
        }
    });

    $stateProvider.state({
        name: 'credit_note_create',
        url: '/credit_note/new',
        templateUrl: 'app/views/credit-note-create/credit-note-create.template.html',
        controller: 'CreditNoteCreateController',
        controllerAs: 'ctrl',
        resolve: {
            viewData: ['fisCustomerApi', function(fisCustomerApi) {
                return fisCustomerApi.views__credit_note_create__on_load();
            }]
        }
    });

    $stateProvider.state({
        name: 'credit_note_view',
        url: '/knjizno_odobrenje/pregled?broj_stranice&broj_stavki_po_stranici',
        templateUrl: 'app/views/credit-note-view/credit-note-view.template.html',
        controller: 'CreditNoteViewController',
        controllerAs: 'ctrl',
        params: {

        },
        resolve: {
            viewData: ['$stateParams', 'fisCustomerApi', function($stateParams, fisCustomerApi) {
                return fisCustomerApi.views__credit_note_view__on_load({
                    broj_stavki_po_stranici: $stateParams.broj_stavki_po_stranici,
                    broj_stranice: $stateParams.broj_stranice
                }).then(function(data) {
                    return data;
                });
            }]
        }
    });

    $stateProvider.state({
        name: 'depozit',
        url: '/depozit',
        templateUrl: 'app/views/depozit/depozit.template.html',
        controller: 'DepozitController',
        controllerAs: 'ctrl',
        resolve: {
            /* @ngInject */
            initialData: ['api', function (api) {
                return api.api__frontend__deposit().then(function(data) {
                    return data;
                });
            }]
        }
    });

    $stateProvider.state({
        name: 'firma-dospjela-faktura-listaj',
        url: '/firma/dospjela_faktura/pregled',
        templateUrl: 'app/views/dospjela-faktura-pregled/dospjela-faktura-pregled.template.html',
        controller: 'DospjelaFakturaPregledController',
        controllerAs: 'ctrl',
        resolve: {
            /* @ngInject */
            dospjele_fakture: ['$stateParams', 'api', function($stateParams, api) {
                return api.dospjelaFaktura.listaj();
            }]
        }
    });

    $stateProvider.state({
        title: 'Konačni račun',
        showDesktopTitle: true,

        name: 'finalInvoiceInput',
        url: '/final_invoice/create?advance_invoice_id',
        templateUrl: 'app/views/faktura-konacni-racun/faktura-konacni-racun.template.html',
        controller: 'FakturaKonacniRacunController',
        controllerAs: 'ctrl',
        params: {
            invoice_template_id: {type: 'int', value: null, squash: true},
            invoice_type_id: {type: 'int', value: null, squash: true},
            advance_invoice_id: {type: 'int', value: null}
        },
        resolve: {
            /* @ngInject */
            initialData: ['$stateParams', 'api', function($stateParams, api) {
                return api.api__frontend__final_invoice__create($stateParams.advance_invoice_id).then(function (data) {
                    return data;
                });
            }]
        }
    });

    $stateProvider.state({
        name: 'faktura-korekcija',
        url: '/faktura/:id/korekcija',
        templateUrl: 'app/views/faktura-korekcija/faktura-korekcija.template.html',
        controller: 'FakturaKorekcijaController',
        controllerAs: 'ctrl',
        resolve: {
            /* @ngInject */
            faktura: ['$stateParams', 'api', function($stateParams, api) {
                return api.faktura.poId.listaj($stateParams.id);
            }]
        }
    });

    $stateProvider.state({
        title: 'Prodaja po artiklima',
        showDesktopTitle: false,

        name: 'prodaja-racun-unos',
        url: '/prodaja/racun/unos',
        templateUrl: 'app/views/faktura-pos-unos/faktura-pos-unos.template.html',
        controller: 'FakturaPosUnosController',
        controllerAs: 'ctrl'
    });

    $stateProvider.state({
        name: 'faktura_preged_avansa',
        url: '/racun/avans/pregled?broj_stranice&broj_stavki_po_stranici&{ordinal_id}&{client_id}&{payment_type_id}&{total_price_gte}&{total_price_lte}&{fiscalization_date_gte}&{fiscalization_date_lte}',
        templateUrl: 'app/views/faktura-pregled-avansa/faktura-pregled-avansa.template.html',
        controller: 'FakturaPregledAvansaController',
        controllerAs: 'ctrl',
        params: {
            ordinal_id: {type: 'int'},
            client_id: {array: true, type: 'int', value: []},
            payment_type_id: {array: true, type: 'int', value: []},
            total_price_gte: {type: 'int'},
            total_price_lte: {type: 'int'},
            fiscalization_date_gte: {type: 'datetime'},
            fiscalization_date_lte: {type: 'datetime'},
        },
        resolve: {
            /* @ngInject */
            initialData: ['$http', '$stateParams', 'fisInvoiceConfig', function ($http, $stateParams, fisInvoiceConfig) {
                let params = {
                    broj_stavki_po_stranici: $stateParams.broj_stavki_po_stranici || fisInvoiceConfig.itemsPerPage,
                    broj_stranice: $stateParams.broj_stranice || 1,
                    ordinal_id: $stateParams.ordinal_id,
                    total_price_gte: $stateParams.total_price_gte,
                    total_price_lte: $stateParams.total_price_lte,
                    fiscalization_date_gte: $stateParams.fiscalization_date_gte,
                    fiscalization_date_lte: $stateParams.fiscalization_date_lte,
                    payment_type_id: $stateParams.payment_type_id,
                    client_id: $stateParams.client_id
                }

                return $http({
                    method: 'GET',
                    url: '/api/customer/frontend/invoice/advance/all',
                    params: params
                }).then(function (response) {
                    return response.data;
                });
            }]
        }
    });

    $stateProvider.state({
        title: 'Pregled računa',
        showDesktopTitle: true,

        name: 'faktura_pregled_redovnih',
        url: '/racun/redovni/pregled?broj_stranice&broj_stavki_po_stranici&{ordinal_id}&{client_id}&{payment_type_id}&{total_price_gte}&{total_price_lte}&{fiscalization_date_gte}&{fiscalization_date_lte}',
        templateUrl: 'app/views/faktura-pregled-redovnih/faktura-pregled-redovnih.template.html',
        controller: 'FakturaPregledRedovnihController',
        controllerAs: 'ctrl',
        params: {
            broj_stranice: {
                type: 'int',
                value: 1
            },
            broj_stavki_po_stranici: {
                type: 'int',
                value: fisInvoiceConfig.itemsPerPage
            },
            ordinal_id: {
                type: 'int',
                value: undefined
            },
            total_price_gte: {
                type: 'int',
                value: undefined
            },
            total_price_lte: {
                type: 'int',
                value: undefined
            },
            fiscalization_date_gte: {
                type: 'datetime',
                value: undefined
            },
            fiscalization_date_lte: {
                type: 'datetime',
                value: undefined
            },
            client_id: {
                type: 'int',
                array: true
            },
            payment_type_id: {
                type: 'int',
                array: true
            },
        },
        resolve: {
            /* @ngInject */
            initialData: ['api', '$stateParams', function (api, $stateParams) {
                let params = {
                    ordinal_id: $stateParams.ordinal_id,
                    broj_stavki_po_stranici: $stateParams.broj_stavki_po_stranici,
                    broj_stranice: $stateParams.broj_stranice,
                    total_price_gte: $stateParams.total_price_gte,
                    total_price_lte: $stateParams.total_price_lte,
                    fiscalization_date_gte: $stateParams.fiscalization_date_gte,
                    fiscalization_date_lte: $stateParams.fiscalization_date_lte,
                    payment_type_id: $stateParams.payment_type_id,
                    client_id: $stateParams.client_id
                }

                return api.api__frontend__invoice__regular__all(params);
            }]
        }
    });

    $stateProvider.state({
        title: 'Pregled porudžbina',
        showDesktopTitle: true,

        name: 'faktura_pregled_porudzbine',
        url: '/racun/porudzbine/pregled?broj_stranice&broj_stavki_po_stranici&{ordinal_id}&{client_id}&{payment_type_id}&{total_price_gte}&{total_price_lte}&{fiscalization_date_gte}&{fiscalization_date_lte}',
        templateUrl: 'app/views/faktura-pregled-porudzbine/faktura-pregled-porudzbine.template.html',
        controller: 'FakturaPregledPorudzbineController',
        controllerAs: 'ctrl',
        params: {
            broj_stranice: {
                type: 'int',
                value: 1
            },
            broj_stavki_po_stranici: {
                type: 'int',
                value: fisInvoiceConfig.itemsPerPage
            },
            ordinal_id: {
                type: 'int',
                value: undefined
            },
            total_price_gte: {
                type: 'int',
                value: undefined
            },
            total_price_lte: {
                type: 'int',
                value: undefined
            },
            fiscalization_date_gte: {
                type: 'datetime',
                value: undefined
            },
            fiscalization_date_lte: {
                type: 'datetime',
                value: undefined
            },
            client_id: {
                type: 'int',
                array: true
            },
            payment_type_id: {
                type: 'int',
                array: true
            },
        },
        resolve: {
            /* @ngInject */
            initialData: ['api', '$stateParams', function (api, $stateParams) {
                let params = {
                    ordinal_id: $stateParams.ordinal_id,
                    broj_stavki_po_stranici: $stateParams.broj_stavki_po_stranici,
                    broj_stranice: $stateParams.broj_stranice,
                    total_price_gte: $stateParams.total_price_gte,
                    total_price_lte: $stateParams.total_price_lte,
                    fiscalization_date_gte: $stateParams.fiscalization_date_gte,
                    fiscalization_date_lte: $stateParams.fiscalization_date_lte,
                    payment_type_id: $stateParams.payment_type_id,
                    client_id: $stateParams.client_id
                }

                return api.api__frontend__invoice__regular__all(params);
            }]
        }
    });

    $stateProvider.state({
        title: 'Slobodan unos avansa',
        showDesktopTitle: true,

        name: 'advanceInvoiceInput',
        url: '/advance/create',
        templateUrl: 'app/views/faktura-slobodan-unos-avansa/faktura-slobodan-unos-avansa.template.html',
        controller: 'FakturaSlobodanUnosAvansaController',
        controllerAs: 'ctrl',
        params: {
            invoice_template_id: {type: 'int', value: null, squash: true},
            invoice_type_id: {type: 'int', value: null, squash: true}
        },
        resolve: {
            /* @ngInject */
            initialData: ['$stateParams', 'api', function($stateParams, api) {
                return api.api__frontend__invoice__create__type1($stateParams.invoice_template_id).then(function (data) {
                    return data;
                });
            }]
        }
    });

    $stateProvider.state({
        title: 'Slobodan unos korekcije',
        showDesktopTitle: true,

        name: 'corrective-invoice-create',
        url: '/corrective/create',
        templateUrl: 'app/views/faktura-slobodan-unos-korekcije/faktura-slobodan-unos-korekcije.template.html',
        controller: 'FakturaSlobodanUnosKorekcijeController',
        controllerAs: 'ctrl',
        params: {
            invoice_template_id: {type: 'int', value: null, squash: true},
            invoice_type_id: {type: 'int', value: null, squash: true}
        }
    });

    $stateProvider.state({
        title: 'Slobodan unos računa',
        showDesktopTitle: true,

        name: 'regularInvoiceInput',
        url: '/racun/opsti_unos',
        templateUrl: 'app/views/faktura-slobodan-unos-redovnih/faktura-slobodan-unos-redovnih.template.html',
        controller: 'FakturaSlobodanUnosRedovnihController',
        controllerAs: 'ctrl',
        params: {
            invoice_template_id: {type: 'int', value: null, squash: true},
            invoice_type_id: {type: 'int', value: null, squash: true}
        },
        resolve: {
            /* @ngInject */
            initialData: ['$stateParams', 'api', function($stateParams, api) {
                return api.api__frontend__invoice__create__type1($stateParams.invoice_template_id).then(function (data) {
                    return data;
                });
            }]
        }
    });

    $stateProvider.state({
        title: 'Unos po grupama',
        showDesktopTitle: false,

        name: 'faktura-unos-po-grupama',
        url: '/faktura/grupe/unos',
        templateUrl: 'app/views/faktura-unos-po-grupama/faktura-unos-po-grupama.template.html',
        controller: 'FakturaUnosPoGrupamaController',
        controllerAs: 'ctrl',
        resolve: {
            /* @ngInject */
            grupe_artikala: ['$rootScope', 'api', function($rootScope, api) {
                return api.grupaArtikala.listaj().then(function (data) {
                    return data;
                });
            }]
        }
    });

    $stateProvider.state({
        name: 'firma-azuriraj',
        url: '/firma/azuriraj',
        templateUrl: 'app/views/firma-izmjena/firma-izmjena.template.html',
        controller: 'FirmaIzmjenaController',
        controllerAs: 'ctrl'
    });

    $stateProvider.state({
        title: 'Izmjena grupe artikala',
        showDesktopTitle: true,

        name: 'grupa-artikala-izmjena',
        url: '/grupa_artikala/:id/izmjena',
        templateUrl: 'app/views/grupa-artikala-izmjena/grupa-artikala-izmjena.template.html',
        controller: 'GrupaArtikalaIzmjenaController',
        controllerAs: 'ctrl',
        resolve: {
            /* @ngInject */
            grupaArtikala: ['$stateParams', 'api', function($stateParams, api) {
                return api.grupaArtikala.poId.listaj($stateParams.id);
            }]
        }
    });

    $stateProvider.state({
        name: 'grupa-artikala-pregled-lista',
        url: '/grupa_artikala/pregled',
        templateUrl: 'app/views/grupa-artikala-pregled-lista/grupa-artikala-pregled-lista.template.html',
        controller: 'GrupaArtikalaPregledListaController',
        controllerAs: 'ctrl',
        resolve: {
            /* @ngInject */
            grupeArtikala: ['api', function(api) {
                return api.grupaArtikala.listaj().then(function(data) {
                    return data;
                });
            }]
        }
    });

    $stateProvider.state({
        title: 'Nova grupa artikala',
        showDesktopTitle: true,

        name: 'grupa-artikala-unos',
        url: '/grupa_artikala/unos',
        templateUrl: 'app/views/grupa-artikala-unos/grupa-artikala-unos.template.html',
        controller: 'GrupaArtikalaUnosController',
        controllerAs: 'ctrl'
    });

    $stateProvider.state({
        name: 'izvjestaj_dnevni_izvjestaj',
        url: '/izvjestaj/dnevni_izvjestaj',
        templateUrl: 'app/views/izvjestaj-dnevni-forma/izvjestaj-dnevni-forma.template.html',
        controller: 'IzvjestajDnevniFormaController',
        controllerAs: 'ctrl'
    });

    $stateProvider.state({
        name: 'izvjestaj_periodicni_izvjestaj',
        url: '/izvjestaj/periodicni_izvjestaj',
        templateUrl: 'app/views/izvjestaj-periodicni-forma/izvjestaj-periodicni-forma.template.html',
        controller: 'IzvjestajPeriodicniFormaController',
        controllerAs: 'ctrl'
    });

    $stateProvider.state({
        name: 'izvjestaj_po_artiklima',
        url: '/izvjestaj/po_artiklima',
        templateUrl: 'app/views/izvjestaj-po-artiklima-forma/izvjestaj-po-artiklima-forma.template.html',
        controller: 'IzvjestajPoArtiklimaFormaController',
        controllerAs: 'ctrl'
    });

    $stateProvider.state({
        name: 'izvjestaj_po_grupama_artikala',
        url: '/izvjestaj/po_grupama_artikala',
        templateUrl: 'app/views/izvjestaj-po-grupama-artikala-forma/izvjestaj-po-grupama-artikala-forma.template.html',
        controller: 'IzvjestajPoGrupamaArtikalaFormaController',
        controllerAs: 'ctrl'
    });

    $stateProvider.state({
        name: 'izvjestaj_zurnal',
        url: '/izvjestaj/zurnal',
        templateUrl: 'app/views/izvjestaj-zurnal-forma/izvjestaj-zurnal-forma.template.html',
        controller: 'IzvjestajZurnalFormaController',
        controllerAs: 'ctrl'
    });

    $stateProvider.state({
        name: 'komitent-izmjena',
        url: '/komitent/:id/izmjena',
        templateUrl: 'app/views/komitent-izmjena/komitent-izmjena.template.html',
        controller: 'KomitentIzmjenaController',
        controllerAs: 'ctrl',
        resolve: {
            /* @ngInject */
            komitent: ['$stateParams', 'api', function($stateParams, api) {
                return api.komitent.poId.listaj($stateParams.id);
            }]
        }
    });

    $stateProvider.state({
        name: 'komitent-pregled-lista',
        url: '/komitent/pregled?broj_stavki_po_stranici&broj_stranice&upit_za_pretragu',
        templateUrl: 'app/views/komitent-pregled-lista/komitent-pregled-lista.template.html',
        controller: 'KomitentPregledListaController',
        controllerAs: 'ctrl',
        resolve: {
            /* @ngInject */
            strana: ['$stateParams', 'fisCustomerApi', function($stateParams, fisCustomerApi) {
                return fisCustomerApi.views__komitent_pregled_lista__on_load({
                    'query': $stateParams.upit_za_pretragu,
                    'broj_stranice': $stateParams.broj_stranice,
                    'broj_stavki_po_stranici': $stateParams.broj_stavki_po_stranici
                }).then(function(data) {
                    return data.pagedData;
                });
            }]
        }
    });

    $stateProvider.state({
        name: 'komitent-pregled-placanja',
        url: '/komitent/:id/placanja/pregled',
        templateUrl: 'app/views/komitent-pregled-placanja/komitent-pregled-placanja.template.html',
        controller: 'KomitentPregledPlacanjaController',
        controllerAs: 'ctrl',
        resolve: {
            /* @ngInject */
            komitent: ['$stateParams', 'api', function($stateParams, api) {
                return api.komitent.poId.listaj($stateParams.id);
            }]
        }
    });

    $stateProvider.state({
        name: 'komitent-unos',
        url: '/komitent/unos',
        templateUrl: 'app/views/komitent-unos/komitent-unos.template.html',
        controller: 'KomitentUnosController',
        controllerAs: 'ctrl'
    });

    $stateProvider.state({
        name: 'komitent-unos-placanja',
        url: '/komitent/placanja/unos',
        templateUrl: 'app/views/komitent-unos-placanja/komitent-unos-placanja.template.html',
        controller: 'KomitentUnosPlacanjaController',
        controllerAs: 'ctrl',
        resolve: {
            /* @ngInject */
            komitenti: ['$stateParams', 'api', function($stateParams, api) {
                return api.komitent.listaj();
            }]
        }
    });

    $stateProvider.state({
        name: 'prijemnica-pregled-lista',
        url: '/prijemnica/pregled?broj_stranice&broj_stavki_po_stranici',
        templateUrl: 'app/views/prijemnica-pregled-lista/prijemnica-pregled-lista.template.html',
        controller: 'PrijemnicaPregledListaController',
        controllerAs: 'ctrl',
        params: {
            broj_stranice: {
                type: 'int',
                value: 1
            },
            broj_stavki_po_stranici: {
                type: 'int',
                value: 10
            },
        },
        resolve: {
            /* @ngInject */
            stranica: ['$stateParams', 'api', function ($stateParams, api) {
                return api.kalkulacija.listaj({
                    broj_stranice: $stateParams.broj_stranice,
                    broj_stavki_po_stranici: $stateParams.broj_stavki_po_stranici
                });
            }]
        }
    });

    $stateProvider.state({
        name: 'prijemnica-unos',
        url: '/prijemnica/unos',
        templateUrl: 'app/views/prijemnica-unos/prijemnica-unos.template.html',
        controller: 'PrijemnicaUnosController',
        controllerAs: 'ctrl',
        resolve: {
            /* @ngInject */
            magacini: ['api', function (api) {
                return api.magacin.listaj().then(function (data) {
                    return data;
                });
            }],
            /* @ngInject */
            komitenti: ['api', function (api) {
                return api.komitent.listaj().then(function (data) {
                    return data;
                });
            }],
            /* @ngInject */
            artikli: ['api', function (api) {
                return api.artikal.listaj().then(function (data) {
                    return data;
                });
            }],
        }
    });

    $stateProvider.state({
        title: "Pregled predračuna",
        showDesktopTitle: true,

        name: 'profaktura-pregled',
        url: '/profaktura/pregled?broj_stranice&broj_stavki_po_stranici&{ordinal_id}&{client_id}&{payment_type_id}&{total_price_gte}&{total_price_lte}&{fiscalization_date_gte}&{fiscalization_date_lte}',
        templateUrl: 'app/views/profaktura-pregled-redovnih/profaktura-pregled-redovnih.template.html',
        controller: 'ProfakturaPregledRedovnihController',
        controllerAs: 'ctrl',
        params: {
            broj_stranice: { type: 'int', value: 1 },
            broj_stavki_po_stranici: {type: 'int', value: fisInvoiceConfig.itemsPerPage },
            ordinal_id: {type: 'int'},
            client_id: {array: true, type: 'int', value: []},
            payment_type_id: {array: true, type: 'int', value: []},
            total_price_gte: {type: 'int'},
            total_price_lte: {type: 'int'},
            fiscalization_date_gte: {type: 'datetime'},
            fiscalization_date_lte: {type: 'datetime'},
        },
        resolve: {
            /* @ngInject */
            initialData: ['api', '$stateParams', function (api, $stateParams) {
                let params = {
                    ordinal_id: $stateParams.ordinal_id,
                    broj_stavki_po_stranici: $stateParams.broj_stavki_po_stranici,
                    broj_stranice: $stateParams.broj_stranice,
                    total_price_gte: $stateParams.total_price_gte,
                    total_price_lte: $stateParams.total_price_lte,
                    fiscalization_date_gte: $stateParams.fiscalization_date_gte,
                    fiscalization_date_lte: $stateParams.fiscalization_date_lte,
                    payment_type_id: $stateParams.payment_type_id,
                    client_id: $stateParams.client_id
                }

                return api.api__frontend__invoice__template__all(params);
            }]
        }
    });

    $stateProvider.state({
        name: 'stanje',
        url: '/stanje',
        templateUrl: 'app/views/stanje/stanje.template.html',
        controller: 'StanjeController',
        controllerAs: 'ctrl',
        resolve: {
            /* @ngInject */
            stanje: ['api', function (api) {
                return api.stanje.listaj();
            }]
        }
    });

    $stateProvider.state({
        name: 'certificates-list-view',
        url: '/certificates-list-view',
        templateUrl: 'app/views2/certificates-list-view/certificates-list-view.template.html',
        controller: 'CertificatesListViewController',
        controllerAs: 'ctrl',
        resolve: {
            viewData: ['fisCustomerApi', function(fisCustomerApi) {
                return fisCustomerApi.certificatesListViewLoad()
            }]
        }
    });
}
