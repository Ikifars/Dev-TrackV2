const API = "http://localhost:5000/api"

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

function loadProjects(){
  fetch(API + "/projects", {
    headers: {"Authorization": "Bearer " + localStorage.getItem("token")}
  })
  .then(res => res.json())
  .then(data => {
    projectList.innerHTML = ""
    data.forEach(p => {
      projectList.innerHTML += `<li>${p[1]} - ${p[2]}</li>`
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
