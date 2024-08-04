angular.module("app").directive("orderGroupPicker", orderGroupPicker);

orderGroupPicker.$inject = ["fisModal", "invoiceFactory", "api"];

function orderGroupPicker(fisModal, invoiceFactory, api) {
  return {
    require: "ngModel",
    restrict: "E",
    templateUrl:
      "app/directives/order-group-picker/order-group-picker.template.html",
    transclude: true,
    link: link,
    scope: {
      invoice: "=",
      fisDisabled: "&",
      fisChange: "&",
    },
  };

  function link(scope, element, attrs, ngModel) {
    element.addClass("order-group-picker");

    scope.disabled = scope.fisDisabled();

    if (attrs.buttonResponsiveClasses) {
      scope.buttonResponsiveClasses = attrs.buttonResponsiveClasses;
    } else {
      scope.buttonResponsiveClasses = "col-6 col-lg-3 col-xxl-2";
    }

    scope.searchGroups = function (query) {
      return api.order_groups.all(query).then(function (data) {
        return data;
      });
    };

    scope.onSelect = function ($item, $model, $label) {
      invoiceFactory.setOrderGroup(scope.invoice, $item);
      ngModel.$setViewValue(scope.invoice.order_group_id);
    };

    scope.showGroupUpdateModal = function () {
      fisModal
        .orderGroupCreateOrEditModal(scope.invoice.order_group)
        .then(function (result) {
          if (result.isConfirmed) {
            invoiceFactory.setOrderGroup(scope.invoice, result.group);
            ngModel.$setViewValue(scope.invoice.order_group_id);
          }
        });
    };

    scope.showCreateGroupModal = function () {
      fisModal.orderGroupCreateOrEditModal().then(function (result) {
        if (result.isConfirmed) {
          invoiceFactory.setOrderGroup(scope.invoice, result.group);
          ngModel.$setViewValue(scope.invoice.order_group_id);
        }
      });
    };

    scope.removeGroup = function () {
      invoiceFactory.setOrderGroup(scope.invoice, null);
    };
  }
}
