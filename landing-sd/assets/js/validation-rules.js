
var rules = {
    rules: {
      showcaseName: { required: true},
      webmasterGTM: { required: false },
      domain: { required: true, url: true },
      labelsUTM: { required: true },
      // language: { required: true },
      headerTheme: { required: true },
      headerLogotype: { required: true },
      logotypeText: { required: true, minlength: 2, maxlength: 10},
      headerTitle: { required: true, maxlength: 128 },
      headerText: { required: false, maxlength: 256 },
      offerTheme: { required: true },
      offersOrientation: { required: true },
      offersCols: { required: true },
      btnText: { required: true },
      faqTheme: { required: true },
      widgetsPush: { required: false },
      widgetsCredit: { required: false },
      footerTheme: { required: true },
      footerTitle: { required: true },
      footerText: { required: true },
    },
    messages: {
      showcaseName: { required: "Введите название витрины"},
      webmasterID: { required: "Введите ваш ID вебмастера в системе Salesdoubler", digits: "ID вебмастера состоит только из цифр" },
      webmasterGTM: { required: "Введите GTM-код вашего аккаунта Google Analytics" },
      domain: { required: "Введите название домена", url: "Введите название домена в формате: http(s)://mysite.com" },
      labelsUTM: { required: "Введите UTM-метки в формате a=AAA&b=BBB&c=CCC" },
      // language: { required: "Выберите язык витрины" },
      headerTheme: { required: "Выберите тему" },
      headerLogotype: { required: "Выберите логотип" },
      logotypeText: { required: "Введите текст логотипа", minlength: "Минимум 2 символа", maxlength: "Максимум 10 символов" },
      headerTitle: { required: "Введите текст заголовка", maxlength: "Максимум 128 символов" },
      headerText: { required: false, maxlength: "Максимум 256 символов" },
      offerTheme: { required: "Выберите тему для оффера" },
      offersOrientation: { required: "Выберите ориентацию офферов" },
      offersCols: { required: "Выберите количество офферов в строке" },
      btnText: { required: "Введите название кнопки в блоке оффера" },
      faqTheme: { required: "Выберите тему для блока F.A.Q." },
      widgetsPush: { required: false },
      widgetsCredit: { required: false },
      footerTheme: { required: "Выберите тему для футера" },
      footerTitle: { required: "Введите текст заголовка" },
      footerText: { required: "Введите основной текст" },
    },
    errorElement: "em",
    errorPlacement: function ( error, element ) {
      error.addClass( "help-block" );
      if ( element.prop( "type" ) === "checkbox" ) {
        error.insertAfter( element.parent( "label" ) );
      } else {
        error.insertAfter( element );
      }
    },
    highlight: function ( element, errorClass, validClass ) {
      $( element ).parent().addClass( "has-error" ).removeClass( "has-success" ); // fix
    },
    unhighlight: function (element, errorClass, validClass) {
      $( element ).parent().addClass( "has-success" ).removeClass( "has-error" ); // fix
    }
  }

  function addClassValidationMethods(){
    $.validator.addMethod("requiredQuestion", $.validator.methods.required, "Введите текст вопроса");
    $.validator.addMethod("requiredAnswer", $.validator.methods.required, "Введите текст ответа");
    
    jQuery.validator.addClassRules({
        faqQuestion: { requiredQuestion: true },
        faqAnswer: { requiredAnswer: true }
    });
  }