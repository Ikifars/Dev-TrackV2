const API = "https://dev-trackv2.onrender.com/api";

// Helper pra pegar elementos sem dar erro
const $ = (id) => document.getElementById(id);
let isLogin = true;

// Toggle Login/Cadastro - roda quando carrega a página
document.addEventListener('DOMContentLoaded', () => {
  const toggleText = $("#toggle-text");
  if (toggleText) {
    toggleText.addEventListener('click', toggleAuthMode);
  }
  
  // Se já tiver token válido, manda pra dashboard
  const token = localStorage.getItem("token");
  const exp = localStorage.getItem("token_exp");
  if (token && exp && Date.now() < exp) {
    window.location.href = "dashboard.html";
  }
});

function toggleAuthMode() {
  isLogin = !isLogin;
  const nameInput = $("#name");
  const title = $("#form-title");
  const btn = $("#submit-btn");
  const toggleText = $("#toggle-text");
  
  if (isLogin) {
    nameInput.style.display = 'none';
    title.textContent = 'DevTrack - Login';
    btn.textContent = 'Entrar';
    btn.onclick = login;
    toggleText.innerHTML = 'Não tem conta? <span style="color: #007bff;">Cadastre-se</span>';
  } else {
    nameInput.style.display = 'block';
    title.textContent = 'DevTrack - Cadastro';
    btn.textContent = 'Criar conta';
    btn.onclick = register;
    toggleText.innerHTML = 'Já tem conta? <span style="color: #007bff;">Fazer login</span>';
  }
}

async function login() {
  const email = $("#email").value;
  const password = $("#password").value;

  if (!email || !password) {
    alert("Preencha todos os campos");
    return;
  }

  try {
    const res = await fetch(API + "/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.error || error.message || "Login inválido");
    }

    const data = await res.json();

    if (data.token) {
      localStorage.setItem("token", data.token);
      localStorage.setItem("token_exp", Date.now() + 15 * 60 * 1000); // 15min
      localStorage.setItem("user", JSON.stringify(data.user || {}));
      window.location.href = "dashboard.html";
    } else {
      throw new Error("Token não recebido");
    }
  } catch (err) {
    alert(err.message);
  }
}

async function register() {
  const name = $("#name").value;
  const email = $("#email").value;
  const password = $("#password").value;

  if (!name || !email || !password) {
    alert("Preencha todos os campos");
    return;
  }

  if (password.length < 8) {
    alert("Senha deve ter no mínimo 8 caracteres");
    return;
  }

  try {
    const res = await fetch(API + "/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password })
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.error || error.message || "Erro ao criar conta");
    }

    const data = await res.json();

    // Seu register.py já retorna access_token, então loga direto
    const token = data.access_token || data.token;
    if (token) {
      localStorage.setItem("token", token);
      localStorage.setItem("token_exp", Date.now() + 15 * 60 * 1000);
      localStorage.setItem("user", JSON.stringify(data.user));
      window.location.href = "dashboard.html";
    } else {
      alert("Conta criada. Faça login.");
      toggleAuthMode(); // Volta pro login
    }
  } catch (err) {
    alert(err.message);
  }
}

async function loadProjects() {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "index.html";
    return;
  }

  const exp = localStorage.getItem("token_exp");
  if (exp && Date.now() > exp) {
    alert("Sessão expirada. Faça login novamente.");
    localStorage.clear();
    window.location.href = "index.html";
    return;
  }

  try {
    const res = await fetch(API + "/projects", {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (res.status === 401) {
      localStorage.clear();
      window.location.href = "index.html";
      return;
    }

    if (!res.ok) throw new Error("Erro ao carregar projetos");

    const projects = await res.json();
    const projectList = $("#projectList");
    projectList.innerHTML = "";

    if (projects.length === 0) {
      projectList.innerHTML = "<li>Nenhum projeto ainda. Crie o primeiro 🚀</li>";
      return;
    }

    const fragment = document.createDocumentFragment();
    projects.forEach(p => {
      const li = document.createElement("li");
      li.textContent = `${p.name} - ${p.description || 'Sem descrição'}`;
      fragment.appendChild(li);
    });
    projectList.appendChild(fragment);

  } catch (err) {
    console.error(err);
    alert("Não foi possível carregar os projetos");
  }
}

async function createProject() {
  const projectName = $("#projectName").value.trim();
  if (!projectName) {
    alert("Nome obrigatório");
    return;
  }

  try {
    const res = await fetch(API + "/projects", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      },
      body: JSON.stringify({ name: projectName })
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.error || error.message || "Erro ao criar projeto");
    }

    $("#projectName").value = "";
    await loadProjects();
  } catch (err) {
    alert(err.message);
  }
}