angular
  .module("app")
  .controller("OrderPaymentModalController", OrderPaymentModalController);

OrderPaymentModalController.$inject = [
  "$uibModalInstance",
  "$rootScope",
  "invoiceFactory",
  "orders",
  "total",
];

function OrderPaymentModalController(
  $uibModalInstance,
  $rootScope,
  invoiceFactory,
  orders,
  total
) {
  let ctrl = this;
  // orders: { id1: true, id2: false, id3: true ...} true/false: selected/unselected
  ctrl.orders = Object.keys(orders).filter((id) => orders[id]);
  ctrl.total = total;
  ctrl.payment_methods = [];
  ctrl.is_cash = true;

  ctrl.onPaymentMethodTypeaheadSelect = onPaymentMethodTypeaheadSelect;
  ctrl.recalculatePaymentMethodTotals = recalculatePaymentMethodTotals;
  ctrl.deletePaymentMethod = deletePaymentMethod;
  ctrl.divideEqually = divideEqually;
  ctrl.confirm = confirm;

  function onPaymentMethodTypeaheadSelect($item, $model, $label) {
    ctrl.payment_methods = invoiceFactory.mergePaymentMethods(
      ctrl.payment_methods,
      [invoiceFactory.createPaymentMethod($item.id)]
    );

    recalculatePaymentMethodTotals();
  }

  function deletePaymentMethod(index) {
    ctrl.payment_methods.splice(index, 1);
    recalculatePaymentMethodTotals();
  }

  function recalculatePaymentMethodTotals(autodistribute) {
    let ukupna_cijena_prodajna = new Big(ctrl.total);

    if (angular.isUndefined(autodistribute)) {
      autodistribute = true;
    }

    if (
      autodistribute &&
      ctrl.payment_methods.length === 1 &&
      ctrl.payment_methods[0].payment_method_type_id !==
        PAYMENT_METHOD_TYPE_ADVANCE
    ) {
      ctrl.payment_methods[0].amount = ukupna_cijena_prodajna.toNumber();
      ctrl.payment_methods_total_difference = 0;
      ctrl.payment_method_total_amount = ukupna_cijena_prodajna.toNumber();
      return;
    }

    let payment_methods_total_amount = new Big(0);
    for (let ii = 0; ii < ctrl.payment_methods.length; ii++) {
      payment_methods_total_amount = payment_methods_total_amount.plus(
        ctrl.payment_methods[ii].amount || 0
      );
    }

    ctrl.payment_methods_total_difference = new Big(ukupna_cijena_prodajna)
      .minus(payment_methods_total_amount)
      .toNumber();
    ctrl.payment_methods_total_amount = payment_methods_total_amount.toNumber();
  }

  function divideEqually() {
    const equalNumber = +(total / ctrl.payment_methods.length).toFixed(2);
    const pm = ctrl.payment_methods;

    let current_sum = 0;
    for (let i = 0; i < pm.length; i++) {
      if (i === pm.length - 1) pm[i].amount = ctrl.total - current_sum;
      else pm[i].amount = equalNumber;

      current_sum += equalNumber;
    }

    ctrl.payment_methods_total_difference = 0;
  }

  function confirm() {
    Object.keys($rootScope.selectedOrders).forEach(
      (k) => delete $rootScope.selectedOrders[k]
    );

    Object.keys($rootScope.selectedOrdersTotals).forEach(
      (k) => delete $rootScope.selectedOrdersTotals[k]
    );

    $uibModalInstance.close({ isConfirmed: true });
  }
}
