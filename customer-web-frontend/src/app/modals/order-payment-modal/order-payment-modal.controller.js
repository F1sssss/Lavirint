angular
  .module("app")
  .controller("OrderPaymentModalController", OrderPaymentModalController);

OrderPaymentModalController.$inject = [
  "$uibModalInstance",
  "$rootScope",
  "invoiceFactory",
  "api",
  "orders",
  "total",
];

function OrderPaymentModalController(
  $uibModalInstance,
  $rootScope,
  invoiceFactory,
  api,
  orders,
  total
) {
  let ctrl = this;
  // orders: { id1: true, id2: false, id3: true ...} true/false: selected/unselected
  ctrl.orders = Object.keys(orders).filter((id) => orders[id]);
  ctrl.total = total;
  ctrl.payment_methods = [];
  ctrl.is_cash = true;
  ctrl.errors = {};
  ctrl.napomena = "";

  ctrl.onPaymentMethodTypeaheadSelect = onPaymentMethodTypeaheadSelect;
  ctrl.recalculatePaymentMethodTotals = recalculatePaymentMethodTotals;
  ctrl.deletePaymentMethod = deletePaymentMethod;
  ctrl.divideEqually = divideEqually;
  ctrl.findErrors = findErrors;
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
    if (!ctrl.payment_methods.length) return;

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

  function calcTotalDifference() {
    let payment_methods_sum = 0;
    ctrl.payment_methods.forEach((pm) => (payment_methods_sum += pm.amount));

    ctrl.payment_methods_total_difference = Math.abs(
      ctrl.total - payment_methods_sum
    );
  }

  function findErrors() {
    if (!ctrl.firstSubmitted) return;

    calcTotalDifference();

    return Boolean(ctrl.payment_methods_total_difference);
  }

  function confirm() {
    ctrl.firstSubmitted = true;

    if (ctrl.findErrors()) return;

    api.order.summerize({
      invoice_ids: Object.keys($rootScope.selectedOrders).filter(
        (k) => $rootScope.selectedOrders[k]
      ),
      is_cash: ctrl.is_cash,
      payment_methods: ctrl.payment_methods.filter((pm) => pm.amount),
      napomena: ctrl.napomena,
    });

    Object.keys($rootScope.selectedOrders).forEach(
      (k) => delete $rootScope.selectedOrders[k]
    );

    Object.keys($rootScope.selectedOrdersTotals).forEach(
      (k) => delete $rootScope.selectedOrdersTotals[k]
    );

    $uibModalInstance.close({ isConfirmed: true });
  }
}
