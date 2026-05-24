const API = "https://dev-trackv2.onrender.com/api";
const $ = (id) => document.getElementById(id);
let isLogin = true;

// Seta tudo quando a página carrega
window.addEventListener('load', () => {
  $("#submit-btn").addEventListener('click', handleSubmit);
  $("#toggle-text").addEventListener('click', toggleAuthMode);
  
  // Se já tá logado, vai pra dashboard
  const token = localStorage.getItem("token");
  const exp = localStorage.getItem("token_exp");
  if (token && exp && Date.now() < exp) {
    window.location.href = "dashboard.html";
  }
});

function toggleAuthMode() {
  isLogin = !isLogin;
  
  if (isLogin) {
    $("#name").style.display = 'none';
    $("#form-title").textContent = 'DevTrack - Login';
    $("#submit-btn").textContent = 'Entrar';
    $("#toggle-text").innerHTML = 'Não tem conta? <span>Cadastre-se</span>';
  } else {
    $("#name").style.display = 'block';
    $("#form-title").textContent = 'DevTrack - Cadastro';
    $("#submit-btn").textContent = 'Criar conta';
    $("#toggle-text").innerHTML = 'Já tem conta? <span>Fazer login</span>';
  }
}

async function handleSubmit() {
  const name = $("#name").value.trim();
  const email = $("#email").value.trim();
  const password = $("#password").value;

  if (!email || !password || (!isLogin && !name)) {
    alert("Preencha todos os campos");
    return;
  }

  if (!isLogin && password.length < 8) {
    alert("Senha deve ter no mínimo 8 caracteres");
    return;
  }

  const endpoint = isLogin ? '/login' : '/register';
  const body = isLogin ? { email, password } : { name, email, password };

  try {
    const res = await fetch(API + endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || "Erro ao processar");
    }

    // Login retorna "token", Register retorna "access_token"
    const token = data.token || data.access_token;
    if (token) {
      localStorage.setItem("token", token);
      localStorage.setItem("token_exp", Date.now() + 15 * 60 * 1000);
      localStorage.setItem("user", JSON.stringify(data.user || {}));
      window.location.href = "dashboard.html";
    } else {
      throw new Error("Token não recebido");
    }
  } catch (err) {
    alert(err.message);
  }
}
