function validarEmail() {
  var email = document.getElementById("email").value;

  var regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (regex.test(email)) {
    alert("E-mail válido! Enviando formulário...");
    return true;
  } else {
    alert("E-mail inválido. Por favor, insira um e-mail válido.");
    return false;    
    }
}