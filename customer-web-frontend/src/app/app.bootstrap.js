(function () {
  let $http = angular.injector(["ng"]).get("$http");

  $http({ method: "GET", url: "/api/customer/frontend/initial" })
    .then(bootstrap)
    .catch(redirect);

  function bootstrap(response) {
    angular.module("fiscalisation.config", []).provider("fisConfig", fisConfig);

    fisConfig.$inject = [];

    function fisConfig() {
      let service = {};
      updateFromResponse(response.data);

      this.service = service;

      service.payment_method_type_banknote = {
        id: 1,
        description: "Novčanice i kovanice",
        description_lowercase: "novcanice i kovanice",
        is_cash: true,
        sort_weight: 1,
        is_active: 1,
        is_noncash: false,
      };
      service.payment_method_type_card = {
        id: 2,
        description: "Kreditna i debitna kartica banke izdata fizičkom licu",
        description_lowercase:
          "kreditna i debitna kartica banke izdata fizickom licu",
        is_cash: true,
        sort_weight: 2,
        is_active: 1,
        is_noncash: false,
      };
      service.payment_method_type_check = {
        id: 3,
        description: "Bankovni ček",
        description_lowercase: "bankovni cek",
        is_cash: true,
        sort_weight: 6,
        is_active: 0,
        is_noncash: false,
      };
      service.payment_method_type_svoucher = {
        id: 4,
        description: "Jednokratni vaučer",
        description_lowercase: "jednokratni vaucer",
        is_cash: false,
        sort_weight: 7,
        is_active: 1,
        is_noncash: true,
      };
      service.payment_method_type_company = {
        id: 5,
        description: "Kartice preduzeća prodavca i slično",
        description_lowercase: "kartice preduzeca prodavca i slicno",
        is_cash: false,
        sort_weight: 8,
        is_active: 1,
        is_noncash: true,
      };
      service.payment_method_type_order = {
        id: 6,
        description: "Račun još nije plaćen, biće plaćen zbirnim računom",
        description_lowercase:
          "racun jos nije placen, bice placen zbirnim racunom",
        is_cash: true,
        sort_weight: 9,
        is_active: 1,
        is_noncash: true,
      };
      service.payment_method_type_advance = {
        id: 7,
        description: "Plaćanje avansom",
        description_lowercase: "placanje avansom",
        is_cash: false,
        sort_weight: 5,
        is_active: 1,
        is_noncash: true,
      };
      service.payment_method_type_account = {
        id: 8,
        description: "Transakcioni račun",
        description_lowercase: "transakcioni racun",
        is_cash: false,
        sort_weight: 3,
        is_active: 1,
        is_noncash: true,
      };
      service.payment_method_type_factoring = {
        id: 9,
        description: "Faktoring",
        description_lowercase: "faktoring",
        is_cash: false,
        sort_weight: 10,
        is_active: 1,
        is_noncash: true,
      };
      service.payment_method_type_compensation = {
        id: 10,
        description: "Naknada",
        description_lowercase: "naknada",
        is_cash: false,
        sort_weight: 11,
        is_active: 0,
        is_noncash: true,
      };
      service.payment_method_type_transfer = {
        id: 11,
        description: "Prenos prava ili dugovanja",
        description_lowercase: "prenos prava ili dugovanja",
        is_cash: false,
        sort_weight: 12,
        is_active: 0,
        is_noncash: true,
      };
      service.payment_method_type_waiver = {
        id: 12,
        description: "Odricanje od dugova",
        description_lowercase: "odricanje od dugova",
        is_cash: false,
        sort_weight: 13,
        is_active: 0,
        is_noncash: true,
      };
      service.payment_method_type_kind = {
        id: 13,
        description: "Plaćanje u naturi (kliring)",
        description_lowercase: "placanje u naturi (kliring)",
        is_cash: false,
        sort_weight: 14,
        is_active: 0,
        is_noncash: true,
      };
      service.payment_method_type_other = {
        id: 14,
        description: "Ostala bezgotovinska plaćanja",
        description_lowercase: "ostala bezgotovinska placanja",
        is_cash: false,
        sort_weight: 15,
        is_active: 1,
        is_noncash: true,
      };
      service.payment_method_type_businesscard = {
        id: 15,
        description:
          "Kreditna i debitna kartica banke izdata poreskom obvezniku",
        description_lowercase:
          "kreditna i debitna kartica banke izdata poreskom obvezniku",
        is_cash: false,
        sort_weight: 4,
        is_active: 1,
        is_noncash: true,
      };
      service.payment_method_type_other_cash = {
        id: 16,
        description: "Ostala gotovinska plaćanja",
        description_lowercase: "ostala gotovinska placanja",
        is_cash: true,
        sort_weight: 16,
        is_active: 1,
        is_noncash: false,
      };

      service.payment_method_types_all = [
        service.payment_method_type_banknote,
        service.payment_method_type_card,
        service.payment_method_type_check,
        service.payment_method_type_svoucher,
        service.payment_method_type_company,
        service.payment_method_type_order,
        service.payment_method_type_advance,
        service.payment_method_type_account,
        service.payment_method_type_factoring,
        service.payment_method_type_compensation,
        service.payment_method_type_transfer,
        service.payment_method_type_waiver,
        service.payment_method_type_kind,
        service.payment_method_type_other,
        service.payment_method_type_businesscard,
        service.payment_method_type_other_cash,
      ];

      service.payment_method_types_active = [
        service.payment_method_type_banknote,
        service.payment_method_type_card,
        service.payment_method_type_account,
        service.payment_method_type_businesscard,
        service.payment_method_type_advance,
        service.payment_method_type_svoucher,
        service.payment_method_type_company,
        service.payment_method_type_order,
        service.payment_method_type_factoring,
        service.payment_method_type_other,
        service.payment_method_type_other_cash,
      ];

      service.payment_method_types_active_cash = [
        service.payment_method_type_banknote,
        service.payment_method_type_card,
        service.payment_method_type_order,
        service.payment_method_type_other_cash,
      ];

      service.payment_method_types_active_noncash = [
        service.payment_method_type_account,
        service.payment_method_type_businesscard,
        service.payment_method_type_advance,
        service.payment_method_type_svoucher,
        service.payment_method_type_company,
        service.payment_method_type_factoring,
        service.payment_method_type_other,
      ];

      service.getPaymentMethodTypeByType = getPaymentMethodTypeByType;
      service.getPaymentMethodById = getPaymentMethodById;
      service.filterPaymentMethodsByIds = filterPaymentMethodsByIds;
      service.filterPaymentMethods = filterPaymentMethods;

      function getPaymentMethodTypeByType(is_cash) {
        if (is_cash === undefined) {
          return angular.copy(service.payment_method_types_active);
        }

        if (is_cash) {
          return angular.copy(service.payment_method_types_active_cash);
        } else {
          return angular.copy(service.payment_method_types_active_noncash);
        }
      }

      function getPaymentMethodById(id) {
        let payment_method_type = service.payment_method_types_active.find(
          function (x) {
            return x.id === id;
          }
        );

        return angular.copy(payment_method_type);
      }

      function filterPaymentMethodsByIds(ids, is_cash) {
        return getPaymentMethodTypeByType(is_cash).filter(function (x) {
          return ids.indexOf(x.id) >= 0;
        });
      }

      function filterPaymentMethods(
        query,
        is_cash,
        exclude_advance,
        exclude_order
      ) {
        query = query.replaceAll("ć", "c");
        query = query.replaceAll("Ć", "C");
        query = query.replaceAll("č", "c");
        query = query.replaceAll("Č", "C");
        query = query.replaceAll("ž", "z");
        query = query.replaceAll("Ž", "z");
        query = query.replaceAll("đ", "d");
        query = query.replaceAll("Đ", "D");
        query = query.replaceAll("š", "s");
        query = query.replaceAll("Š", "S");

        return getPaymentMethodTypeByType(is_cash).filter(function (x) {
          if (
            exclude_advance &&
            x.id === service.payment_method_type_advance.id
          )
            return false;

          if (exclude_order && x.id === service.payment_method_type_order.id)
            return false;

          return x.description_lowercase.startsWith(query.toLowerCase());
        });
      }

      this.$get = [
        "$http",
        function ($http) {
          service.reload = reload;
          return service;

          function reload() {
            return $http({
              method: "GET",
              url: "/api/customer/frontend/initial",
            }).then(function (response) {
              updateFromResponse(response.data);
            });
          }
        },
      ];

      //----------------------------------------------------------------------------------------------------------

      function updateFromResponse(data) {
        service.user = data.korisnik;
        service.units = data.jedinice_mjere;
        service.tax_exemption_reasons = data.tax_exemption_reasons;
        service.valute = data.valute;
        service.payment_method_types = data.payment_method_types;
        service.poreske_stope = data.poreske_stope;
        service.isReady = true;
        service.defaultUnit = service.units.find((x) => {
          return x.ui_default;
        });
        service.countries = data.countries;
        service.identification_types = data.identification_types;
        service.certificate_expiration_date = data.certificate_expiration_date;

        if (service.user.firma.je_poreski_obaveznik) {
          service.defaultTaxRate = service.poreske_stope.find(function (x) {
            return x.procenat === 21;
          });
        } else {
          service.defaultTaxRate = service.poreske_stope.find(function (x) {
            return x.procenat === 0;
          });
        }
      }
    }

    angular.element(document).ready(function () {
      angular.bootstrap(document, ["app"], {
        strictDi: true,
      });
    });
  }

  function redirect(rejection) {
    if (rejection.config.url.match("^/api")) {
      if (rejection.status === 401) {
        // window.location.href = './login.html';
        return;
      }
      if (rejection.status === 403) {
        window.location.href = "./forbidden.html";
        return;
      }
    }

    // window.location.href = './login.html';
  }
})();
