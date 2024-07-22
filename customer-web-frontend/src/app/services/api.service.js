angular
    .module('app')
    .service('api', ApiService);

ApiService.$inject = ['$http', '$q', 'invoiceFactory']

function ApiService($http, $q, invoiceFactory) {
    let api = {};

    api.korisnik = {};
    api.korisnik.listaj = apiKorisnikListaj;
    api.korisnik.odjavi = apiKorisnikOdjavi;
    api.korisnik.poId = {};
    api.korisnik.poId.izmijeni = api__korisnik__izmijeni;

    api.organizacionaJedinica = {};
    api.organizacionaJedinica.poId = {};
    api.organizacionaJedinica.poId.izmijeni = api__organizaciona_jedinica__po_id__izmijeni;

    api.api__frontend__initial = api__frontend__initial;
    api.api__frontend__artikal__unos = api__frontend__artikal__unos;
    api.api__frontend__artikal__po_id__izmijeni = api__frontend__artikal__po_id__izmijeni;
    api.api__frontend__invoice__create__type1 = api__frontend__invoice__create__type1;
    api.api__frontend__final_invoice__create = api__frontend__final_invoice__create;
    api.api__frontend__invoice__regular__all = api__frontend__invoice__regular__all;
    api.api__frontend__invoice__advance__all = api__frontend__invoice__advance__all;
    api.api__frontend__invoice__template__all = api__frontend__invoice__template__all;
    api.api__frontend__deposit = api__frontend__deposit;
    api.api__final_invoice__create = api__final_invoice__create;

    api.faktura = {};
    api.faktura.listaj = apiFakturaListaj;
    api.api__faktura__dodaj = api__faktura__dodaj;
    api.api__advance__create = api__advance__create;
    api.faktura.storniraj = apiFakturaStorniraj;
    api.faktura.poId = {};
    api.faktura.poId.listaj = apiFakturaPoIdListaj;
    api.api__faktura__po_id__koriguj = api__faktura__po_id__koriguj;
    api.faktura.poId.mail = apiFakturaPoIdMail;
    api.faktura.poId.dokument = {};
    api.faktura.poId.dokument.upload = apiFakturaPoIdDokumentUpload;
    api.faktura.poId.invoice_schedule = {};
    api.faktura.poId.invoice_schedule.add = api__faktura__pd_id__invoice_schedule__add;

    api.profaktura = {};
    api.profaktura.listaj = apiProfakturaListaj;
    api.profaktura.dodaj = apiProfakturaDodaj;
    api.profaktura.poId = {};
    api.profaktura.poId.listaj = apiProfakturaPoIdListaj;

    api.komitent = {};
    api.komitent.listaj = apiKomitentListaj;
    api.komitent.dodaj = apiKomitentDodaj;
    api.komitent.poId = {};
    api.komitent.poId.listaj = apiKomitentPoIdListaj;
    api.komitent.poId.izmijeni = apiKomitentPoIdIzmijeni;
    api.komitent.placanje = {};
    api.komitent.placanje.dodaj_bulk = apiKomitentPoIdPlacanjeDodajBulk;
    api.komitent.placanje.poId = {};
    api.komitent.placanje.poId.obrisi = apiKomitentPoIdPlacanjePoIdObrisi;

    api.vrstaPlacanja = {};
    api.vrstaPlacanja.listaj = apiVrstaPlacanjaListaj;

    api.artikal = {};
    api.artikal.listaj = apiArtikalListaj;
    api.artikal.dodaj = apiArtikalDodaj;
    api.artikal.izmijeni = apiArtikalIzmijeni;
    api.artikal.trazi = apiArtikalTrazi;
    api.artikal.poId = {};
    api.artikal.poId.listaj = apiArtikalPoIdListaj;
    api.artikal__poId__obrisi = artikal__poId__obrisi;

    api.grupaArtikala = {};
    api.grupaArtikala.listaj = apiGrupaArtikalaListaj;
    api.grupaArtikala.dodaj = apiGrupaArtikalaDodaj;
    api.grupaArtikala.poId = {};
    api.grupaArtikala.poId.listaj = apiGrupaArtikalaPoIdListaj;
    api.grupaArtikala.poId.izmijeni = apiGrupaArtikalaPoIdIzmijeni;
    api.grupaArtikala.poId.zaliha = {};
    api.grupaArtikala.poId.zaliha.listaj = apiGrupaArtikalaPoIdZalihaListaj;

    api.jedinicaMjere = {};
    api.jedinicaMjere.listaj = apiJedinicaMjereListaj;

    api.poreskaStopa = {};
    api.poreskaStopa.listaj = apiPoreskaStopaListaj;

    api.magacin = {};
    api.magacin.listaj = apiMagacinListaj;
    api.magacin.poId = {};
    api.magacin.poId.zalihe = {};
    api.magacin.poId.zalihe.listaj = apiMagacinPoIdZaliheListaj;

    api.kalkulacija = {};
    api.kalkulacija.listaj = apiKalkulacijaListaj;
    api.kalkulacija.dodaj = apiKalkulacijaDodaj;

    api.stanje = {};
    api.stanje.listaj = apiStanjeListaj;

    api.depozit = {};
    api.depozit.polozi = apiDepozitPolozi;
    api.depozit.podigni = apiDepozitPodigni;

    api.izvjestaj = {}
    api.izvjestaj.stanje = apiIzvjestajStanje;

    api.tipIdentifikacioneOznake = {};
    api.tipIdentifikacioneOznake.listaj = apiTipIdentifikacioneOznakeListaj;

    api.firma = {};
    api.firma.listaj = apiFirmaListaj;
    api.firma.logo = {};
    api.firma.logo.izmijeni = apiFirmaLogoIzmijeni;
    api.firma.izmijeni = apiFirmaIzmijeni;
    api.firma.podesavanja = {};
    api.firma.podesavanja.smtp = {};
    api.firma.podesavanja.smtp.izmijeni = apiFirmaPodesavanjaSMTPIzmijeni;

    api.dospjelaFaktura = {};
    api.dospjelaFaktura.listaj = apiDospjelaFakturaListaj;
    api.dospjelaFaktura.notifikacija = {};
    api.dospjelaFaktura.notifikacija.listaj = apiDospjelaFakturaNotifikacijaListaj;
    api.dospjelaFaktura.poId = {};
    api.dospjelaFaktura.poId.dokument = {};
    api.dospjelaFaktura.poId.dokument.listaj = apiDospjelaFakturaPoIdDokumentListaj;

    return api;

    //------------------------------------------------------------------------------------------------------------------

    function _getRequest(requestObject) {
        let canceler = $q.defer();
        requestObject.timeout = canceler.promise;

        let httpPromise = $http(requestObject).then(function(response) {
            return response.data;
        });

        httpPromise.cancel = function() {
            canceler.resolve();
        }

        return httpPromise;
    }

    function apiKorisnikListaj() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/korisnik/listaj'
        });
    }

    function apiKorisnikOdjavi() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/korisnik/odjavi'
        });
    }

    function api__organizaciona_jedinica__po_id__izmijeni(organizacionaJedinicaId, data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/organizaciona_jedinica/' + organizacionaJedinicaId + '/izmijeni',
            data: data
        });
    }

    function api__frontend__initial() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/frontend/initial'
        });
    }

    function api__frontend__artikal__unos() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/frontend/artikal/unos'
        });
    }

    function api__frontend__artikal__po_id__izmijeni(artikalId) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/frontend/artikal/' + artikalId + '/izmijeni'
        });
    }

    function api__frontend__invoice__create__type1(invoice_template_id) {
        let url = new URL('/api/customer/frontend/invoice/create/type1', document.location.origin)
        if (invoice_template_id !== null) {
            url.searchParams.append('invoice_template_id', invoice_template_id);
        }

        return _getRequest({
            method: 'GET',
            url: url.toString()
        });
    }

    function api__frontend__final_invoice__create(advance_invoice_id) {
        let url = new URL('/api/customer/frontend/final_invoice/create', document.location.origin)
        url.searchParams.append('advance_invoice_id', advance_invoice_id);

        return _getRequest({
            method: 'GET',
            url: url.toString()
        });
    }

    function api__frontend__invoice__regular__all(params) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/frontend/invoice/regular/all',
            params: params
        });
    }

    function api__frontend__invoice__advance__all(params) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/frontend/invoice/advance/all',
            params: params
        });
    }

    function api__frontend__invoice__template__all(params) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/frontend/invoice/template/all',
            params: params
        });
    }

    function api__frontend__deposit() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/frontend/deposit'
        });
    }

    function api__final_invoice__create(final_invoice, corrected_advance_invoice, corrective_for_advance_invoice) {
        // corrective_for_advance_invoice['payment_methods'] = [{
        //     amount: corrective_for_advance_invoice.ukupna_cijena_prodajna,
        //     payment_method_type_id: PAYMENT_METHOD_TYPE_ACCOUNT,
        //     payment_method_type: invoiceFactory.createPaymentMethod(7),
        //     advance_invoice_id: corrected_advance_invoice.id,
        //     advance_invoice: {
        //         id: corrected_advance_invoice.id
        //     }
        // }];

        corrective_for_advance_invoice['payment_methods'] = [{
            amount: corrective_for_advance_invoice.ukupna_cijena_prodajna,
            payment_method_type_id: PAYMENT_METHOD_TYPE_ACCOUNT,
            payment_method_type: invoiceFactory.createPaymentMethod(7)
        }];

        return _getRequest({
            method: 'POST',
            url: '/api/customer/final_invoice/create',
            data: {
                final_invoice: final_invoice,
                advance_invoice: corrected_advance_invoice,
                corrective_invoice: corrective_for_advance_invoice
            }
        });
    }

    function apiFakturaListaj(params) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/faktura/listaj',
            params: params
        });
    }

    function api__faktura__dodaj(podaciRacuna) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/faktura/dodaj',
            data: podaciRacuna
        });
    }

    function api__advance__create(data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/advance/create',
            data: data
        });
    }

    function apiFakturaStorniraj(fakturaId) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/faktura/' + fakturaId + '/storniraj'
        });
    }

    function apiFakturaPoIdListaj(fakturaId) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/faktura/' + fakturaId + '/listaj'
        });
    }

    function api__faktura__po_id__koriguj(fakturaId, corrected_invoice, corrective_invoice) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/faktura/' + fakturaId + '/koriguj',
            data: {
                corrected_invoice: corrected_invoice,
                corrective_invoice: corrective_invoice
            }
        });
    }

    function apiFakturaPoIdMail(fakturaId) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/faktura/' + fakturaId + '/mail'
        });
    }

    function apiFakturaPoIdDokumentUpload(fakturaId, datoteka) {
        let formData = new FormData();
        formData.append('dokument', datoteka);

        return _getRequest({
            method: 'POST',
            url: '/api/customer/faktura/' + fakturaId + '/dokument/upload',
            headers: {
                'Content-Type': undefined
            },
            data: formData,
            transformRequest: angular.identity
        });
    }

    function api__faktura__pd_id__invoice_schedule__add(invoiceId, data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/faktura/' + invoiceId + '/invoice_schedule/add',
            data: data
        });
    }

    function apiProfakturaDodaj(data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/profaktura/dodaj',
            data: data
        });
    }

    function apiProfakturaListaj() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/profaktura/listaj'
        });
    }

    function apiProfakturaPoIdListaj(profakturaId) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/profaktura/' + profakturaId + '/listaj'
        });
    }

    function apiKomitentListaj(upitZaPretragu, brojStranice, brojStavkiPoStranici) {
        if (upitZaPretragu) {
            upitZaPretragu = upitZaPretragu.replaceAll('ć', 'c');
            upitZaPretragu = upitZaPretragu.replaceAll('Ć', 'C');
            upitZaPretragu = upitZaPretragu.replaceAll('č', 'c');
            upitZaPretragu = upitZaPretragu.replaceAll('Č', 'C');
            upitZaPretragu = upitZaPretragu.replaceAll('ž', 'z');
            upitZaPretragu = upitZaPretragu.replaceAll('Ž', 'z');
            upitZaPretragu = upitZaPretragu.replaceAll('đ', 'd');
            upitZaPretragu = upitZaPretragu.replaceAll('Đ', 'D');
            upitZaPretragu = upitZaPretragu.replaceAll('š', 's');
            upitZaPretragu = upitZaPretragu.replaceAll('Š', 'S');
        }

        return _getRequest({
            method: 'GET',
            url: '/api/customer/komitent/listaj',
            params: {
                upit_za_pretragu: upitZaPretragu,
                broj_stavki_po_stranici: brojStavkiPoStranici,
                broj_stranice: brojStranice
            }
        });
    }

    function apiKomitentDodaj(data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/komitent/dodaj',
            data: data
        });
    }

    function apiKomitentPoIdListaj(komitentId) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/komitent/' + komitentId + '/listaj'
        });
    }

    function apiKomitentPoIdIzmijeni(komitentId, data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/komitent/' + komitentId + '/izmijeni',
            data: data
        });
    }

    function apiKomitentPoIdPlacanjeDodajBulk(data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/komitent/placanje/dodaj_bulk',
            data: data
        });
    }

    function apiKomitentPoIdPlacanjePoIdObrisi(placanjeId) {
        return _getRequest({
            method: 'DELETE',
            url: '/api/customer/komitent/placanje/' + placanjeId + '/obrisi'
        });
    }

    function apiVrstaPlacanjaListaj(params) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/vrsta_placanja/listaj',
            params: params
        });
    }

    function apiArtikalListaj() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/artikal/listaj'
        });
    }

    function apiArtikalDodaj(data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/artikal/dodaj',
            data: data
        });
    }

    function apiArtikalIzmijeni(artikalId, data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/artikal/' + artikalId + '/izmijeni',
            data: data
        });
    }

    function apiArtikalTrazi(pojam) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/artikal/trazi',
            data: {
                pojam: pojam
            }
        });
    }

    function apiArtikalPoIdListaj(artikalId) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/artikal/' + artikalId + '/listaj'
        });
    }

    function artikal__poId__obrisi(artikalId) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/artikal/' + artikalId + '/obrisi'
        });
    }

    function apiGrupaArtikalaListaj() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/grupa_artikala/listaj'
        });
    }

    function apiGrupaArtikalaDodaj(data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/grupa_artikala/dodaj',
            data: data
        });
    }

    function apiGrupaArtikalaPoIdListaj(grupa_artikala_id) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/grupa_artikala/' + grupa_artikala_id + '/listaj'
        });
    }

    function apiGrupaArtikalaPoIdIzmijeni(grupa_artikala_id, data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/grupa_artikala/' + grupa_artikala_id + '/izmijeni',
            data: data
        });
    }

    function apiGrupaArtikalaPoIdZalihaListaj(grupa_artikala_id) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/firma/grupa_artikala/' + grupa_artikala_id + '/zaliha/listaj'
        });
    }

    function apiJedinicaMjereListaj() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/jedinica_mjere/listaj'
        });
    }

    function apiPoreskaStopaListaj() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/poreska_stopa/listaj'
        });
    }

    function apiDrzavaListaj() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/drzava/listaj'
        });
    }

    function apiMagacinListaj() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/magacin/listaj'
        });
    }

    function apiMagacinPoIdZaliheListaj(magacinId, queryParams) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/magacin/' + magacinId + '/lager/listaj',
            params: queryParams
        });
    }

    function apiKalkulacijaListaj(params) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/kalkulacija/listaj',
            params: params
        });
    }

    function apiKalkulacijaDodaj(data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/kalkulacija/dodaj',
            data: data
        });
    }

    function apiStanjeListaj() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/stanje/listaj'
        });
    }

    function apiDepozitPolozi(data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/depozit/polozi',
            data: data
        });
    }

    function apiDepozitPodigni(data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/depozit/podigni',
            data: data
        });
    }

    function apiIzvjestajStanje(datumOd, datumDo) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/izvjestaj/stanje/' + datumOd + '/' + datumDo
        });
    }

    function apiTipIdentifikacioneOznakeListaj() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/tip_identifikacione_oznake/listaj'
        });
    }

    function apiFirmaListaj() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/firma/listaj'
        });
    }

    function apiFirmaLogoIzmijeni(data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/firma/logo/izmijeni',
            data: data,
            headers: {
                'Content-Type': undefined
            },
            transformRequest: angular.identity
        });
    }

    function apiFirmaIzmijeni(data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/firma/izmijeni',
            data: data
        });
    }

    function apiFirmaPodesavanjaSMTPIzmijeni(data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/firma/podesavanja/smtp/izmijeni',
            data: data
        });
    }

    function api__korisnik__izmijeni(data) {
        return _getRequest({
            method: 'POST',
            url: '/api/customer/korisnik/izmijeni',
            data: data
        });
    }

    function apiDospjelaFakturaListaj() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/firma/dospjela_faktura/listaj'
        });
    }

    function apiDospjelaFakturaNotifikacijaListaj() {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/firma/dospjela_faktura/notifikacija/listaj'
        });
    }

    function apiDospjelaFakturaPoIdDokumentListaj(dospjelaFakturaId) {
        return _getRequest({
            method: 'GET',
            url: '/api/customer/firma/dospjela_faktura/' + dospjelaFakturaId + '/dokument/listaj'
        });
    }
}