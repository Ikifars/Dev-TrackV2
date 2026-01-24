function loadProjects() {
  const token = localStorage.getItem("token")

  if (!token) {
    window.location = "index.html"
    return
  }

  projectList.innerHTML = "<li>Carregando projetos...</li>"

  fetch(API + "/projects", {
    headers: {
      "Authorization": "Bearer " + token
    }
  })
  .then(res => {
    if (!res.ok) throw new Error("Falha ao carregar projetos")
    return res.json()
  })
  .then(data => {
    if (!Array.isArray(data)) {
      throw new Error("Resposta inválida da API")
    }

    projectList.innerHTML = ""

    if (data.length === 0) {
      projectList.innerHTML = "<li>Nenhum projeto ainda. Crie o primeiro 🚀</li>"
      return
    }

    data.forEach(project => {
      projectList.innerHTML += `
        <li>
          <strong>${project.name}</strong>
          <small style="opacity:0.7">#${project.id}</small>
        </li>
      `
    })
  })
  .catch(err => {
    console.error(err)
    alert("Sessão expirada ou erro no servidor")
    localStorage.removeItem("token")
    window.location = "index.html"
  })
}
