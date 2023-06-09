const SERVER_URL = "http://127.0.0.1:8000";
        
const remove = (e) => {
    let delId = e.target.parentNode.id;
    e.target.parentNode.remove();
       
    fetch(`${SERVER_URL}/delete/${delId}`)
    .then(response => response.json())
    .then(data => console.log(data));
}

const ul = document.querySelector(".queue-list");
ul.addEventListener("click", remove, false);

let queueDiv = document.querySelector(".queue-container");
let user = {
        filename: "test.gcode",
        duration: 120,
        machine_id: 2,
        user_id: 1,
        start: Date.now()
}

const submitHandler = (e) => {
    fetch(`${SERVER_URL}/add-session-related`, 
    {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify(user)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
    });  
}

const getAllSessions = (e) => {
    const container = document.querySelector(".queue-list");

    fetch(`${SERVER_URL}/all`)
    .then(response => response.json())
    .then(data => {
        console.log(data);

        let i 
        for (let item of data) {
            let li = document.createElement('li');
            li.setAttribute('id', item.username);

            let p = document.createElement('p');
            p.setAttribute('class', 'queue-item');

            let btn = document.createElement('button');
            btn.setAttribute('class', 'del-btn');
            btn.innerText = 'Remove';

            p.textContent = `${item.username} | ${item.filename} | ${item.duration} | ${item.machine_id}`;

            li.appendChild(p);
            li.appendChild(btn);
            container.appendChild(li);
        }
    }); 
}

const getSessionsByMachine = (e) => {
    const machineId = document.querySelector("#machine-id").value;
    fetch(`${SERVER_URL}/select-by-machine/${machineId}`)
    .then(response => response.json())
    .then(data => {
        console.log(data);
    })
}
