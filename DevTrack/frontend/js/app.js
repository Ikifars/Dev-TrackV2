const API = "https://dev-trackv2.onrender.com/api"

function login() {
  if(!email.value || !password.value){
    alert("Preencha todos os campos")
    return
  }

  fetch(API + "/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({email: email.value, password: password.value})
  })
  .then(res => res.json())
  .then(data => {
    if(data.token){
      localStorage.setItem("token", data.token)
      window.location = "dashboard.html"
    } else {
      alert("Login inválido")
    }
  })
}

// function loadProjects(){
//   fetch(API + "/projects", {
//     headers: {"Authorization": "Bearer " + localStorage.getItem("token")}
//   })
//   .then(res => res.json())
//   .then(data => {
//     projectList.innerHTML = ""
//     data.forEach(p => {
//       projectList.innerHTML += `<li>${p[1]} - ${p[2]}</li>`
//     })
//   })
// }
function loadProjects() {
  const token = localStorage.getItem("token")

  if (!token) {
    window.location = "index.html"
    return
  }

  fetch(API + "/projects", {
    headers: {
      "Authorization": "Bearer " + token
    }
  })
  .then(res => res.json())
  .then(data => {
    if (!Array.isArray(data)) {
      console.error("Erro API:", data)
      alert("Sessão expirada. Faça login novamente.")
      localStorage.removeItem("token")
      window.location = "index.html"
      return
    }

    data.forEach(project => {
      console.log(project)
      // renderiza seus cards aqui
    })
  })
}


function createProject(){
  if(!projectName.value.trim()){
    alert("Nome obrigatório")
    return
  }

  fetch(API + "/projects", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + localStorage.getItem("token")
    },
    body: JSON.stringify({name: projectName.value})
  }).then(() => loadProjects())
}
