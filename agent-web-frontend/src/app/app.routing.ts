import {Routes} from "@angular/router";
import {AuthGuard} from "./core/auth/auth.guard";
import {NoAuthGuard} from "./core/auth/noAuth.guard";
import {dataResolver} from "./resolvers/data.resolver";
import {
  CustomerCertificatesViewComponent
} from "./views/customer-certificates-view/customer-certificates-view.component";
import {LoginViewComponent} from "./views/login-view/login-view.component";
import {CustomerListViewComponent} from "./views/customer-list-view/customer-list-view.component";
import {CustomerUpdateViewComponent} from "./views/customer-update-view/customer-update-view.component";
import {CustomerInsertViewComponent} from "./views/customer-insert-view/customer-insert-view.component";
import {
  CustomerCertificateUploadViewComponent
} from "./views/customer-certificate-upload-view/customer-certificate-upload-view.component";
import {
  CustomerBusinessUnitsViewComponent
} from "./views/customer-business-units-view/customer-business-units-view.component";


export const routes: Routes = [
  {
    path: '',
    redirectTo: '/customer-list-view',
    pathMatch: 'full'
  },
  {
    path: 'customer-list-view',
    component: CustomerListViewComponent,
    canActivate: [AuthGuard],
    resolve: {
      data: dataResolver
    }
  },
  {
    path: 'login',
    component: LoginViewComponent,
    canActivate: [NoAuthGuard]
  },
  {
    path: 'company/:id/general_info',
    component: CustomerUpdateViewComponent,
    canActivate: [AuthGuard],
    resolve: {
      data: dataResolver
    }
  },
  {
    path: 'company/insert',
    component: CustomerInsertViewComponent,
    canActivate: [AuthGuard],
    resolve: {
      data: dataResolver
    }
  },
  {
    path: 'customer/:customerId/certificates/view',
    component: CustomerCertificatesViewComponent,
    canActivate: [AuthGuard],
    resolve: {
      data: dataResolver
    }
  },
  {
    path: 'customer/:customerId/certificate/upload',
    component: CustomerCertificateUploadViewComponent,
    canActivate: [AuthGuard],
    resolve: {
      data: dataResolver
    }
  },
  {
    path: 'customer/:customerId/business-units/all',
    component: CustomerBusinessUnitsViewComponent,
    canActivate: [AuthGuard],
    resolve: {
      data: dataResolver
    }
  }
];
