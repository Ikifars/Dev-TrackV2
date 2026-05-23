const API = "https://dev-trackv2.onrender.com/api";

// Helper pra pegar elementos sem dar erro
const $ = (id) => document.getElementById(id);

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

    // 1. Trata erro HTTP antes de tudo
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.message || "Login inválido");
    }

    const data = await res.json();
    
    // 2. Ideal: token via cookie httpOnly no back. 
    // Como você usa localStorage, pelo menos checa expiração
    if (data.token) {
      localStorage.setItem("token", data.token);
      localStorage.setItem("token_exp", Date.now() + 15 * 60 * 1000); // 15min
      window.location.href = "dashboard.html";
    } else {
      throw new Error("Token não recebido");
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

  // 3. Checa se token expirou antes de bater na API
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
      // Token inválido/expirado no back
      localStorage.clear();
      window.location.href = "index.html";
      return;
    }
    
    if (!res.ok) throw new Error("Erro ao carregar projetos");

    const projects = await res.json(); // Espero [{id: 1, name: "Site", description: "LP"}]
    const projectList = $("#projectList");
    projectList.innerHTML = ""; // Limpa 1x só

    // 4. Evita XSS e innerHTML em loop
    const fragment = document.createDocumentFragment();
    projects.forEach(p => {
      const li = document.createElement("li");
      li.textContent = `${p.name} - ${p.description}`; // textContent escapa HTML
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
      throw new Error(error.message || "Erro ao criar projeto");
    }

    $("#projectName").value = ""; // Limpa input
    await loadProjects(); // Recarrega lista
  } catch (err) {
    alert(err.message);
  }
}