window.onload = function(){
    if (location.pathname=='/'){
        authenticate();
    }
}

function openForm() {
    document.getElementById("popupForm").style.display = "block";
    const form = document.getElementById('formContainer');
    form.addEventListener('submit', async function(e){
        e.preventDefault();
        const formData = new FormData(form);
        let token = await fetch("/login",
            {
                body: formData,
                method: "post"
            })
            .then(res3 => {
                if(!res3.ok){
                    alert('Wrong account or password!')
                }
                return res3
            })
            .then(res => res.json())
            .then(res2 => res2['token'])
            
        sessionStorage.setItem('jwt', token);
        authenticate();
    })
}

function closeForm() {
    document.getElementById("popupForm").style.display = "none";
}

function authenticate(){
    const token = sessionStorage.getItem("jwt");
    fetch('/', {
        method: 'GET',
        headers: new Headers({
            'Authorization': 'Bearer '+token,
            'Content-Type': 'application/json'
        })
    })
    .then((response) => {
        return response.text();
    }).then((html) => {
        document.body.innerHTML = html
    });
}

function addEvent(elem, event, fn) {
    if (elem.addEventListener)
    {
        elem.addEventListener(event, fn, false);
    }
    else
    {
        elem.attachEvent("on" + event, function() {
            return(fn.call(elem, window.event));   
        });
    }
}
addEvent(window, 'load', function(e){
    var list = document.querySelector('.tag-list');
    addEvent(list, 'click',  function(e){
        e = e || window.event;
        var el = e.target || e.srcElement;
        console.log(el.innerHTML);
        sendTag(el.innerHTML);
        
    });
});

function sendTag(tag){
    const xml = new XMLHttpRequest();
    xml.onreadystatechange = function() {
    if (this.readyState==4 && this.status==200){
        console.log(this.readyState);
    }
    };
    xml.open('POST', '/collectTag', true);
    xml.setRequestHeader('content-type', 'application/json');
    dataSend = JSON.stringify({'tag': tag}) ;
    xml.send(dataSend);
}