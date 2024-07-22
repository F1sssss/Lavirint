import {AfterViewInit, Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import {Router} from "@angular/router";
import {AgentApiService} from "../../services/agent-api-service/agent-api.service";
import {FormBuilder, Validators} from "@angular/forms";
import {AuthLoginRequest} from "../../services/agent-api-service/agent-api-dto";

@Component({
  selector: 'app-login',
  templateUrl: './login-view.component.html',
  styleUrls: ['./login-view.component.scss']
})
export class LoginViewComponent implements OnInit, AfterViewInit {
  @ViewChild('usernameInput') usernameInput= {} as ElementRef<HTMLInputElement>;

  formGroup = this.fb.group({
    username: ['', Validators.required],
    password: ['', [Validators.required, Validators.minLength(8)]]
  });

  errorMessage: string | null = null;

  constructor(
    private agentApiService: AgentApiService,
    private router: Router,
    private fb: FormBuilder
  ) {
    this.errorMessage = this.router.getCurrentNavigation()?.extras.state?.['errorMessage'];

    this.agentApiService
  }

  ngOnInit(): void {
    this.formGroup.valueChanges.subscribe(data => {
      this.errorMessage = null;
    });
  }

  ngAfterViewInit() {
    setTimeout(() => {
      this.usernameInput.nativeElement.focus();
    });
  }

  login() {
    if (this.formGroup.invalid) {
      this.errorMessage = 'Podaci nisu ispravno popunjeni.';
      return;
    }

    let requestData = this.formGroup.value as AuthLoginRequest;

    this.agentApiService.loginViewSubmit(requestData).subscribe(response => {
      if (response.errorMessage !== null) {
        this.errorMessage = response.errorMessage;
        return;
      }

      this.router.navigate(['']);
    });
  }
}
