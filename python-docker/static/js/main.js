window.onload = function(){
    authenticate(location.pathname)
    // if (location.pathname=='/'){
    //     authenticate('/');
    // }
    // else if (location.pathname=='/normalaccount'){
    //     authenticate('/normalaccount');
    // }
    // else if (location.pathname=='/foreignaccount'){
    //     authenticate('/foreignaccount');
    // }
    // else if (location.pathname=='/digitalaccount'){
    //     authenticate('/digitalaccount');
    // }
    // else if (location.pathname=='/securityaccount'){
    //     authenticate('/securityaccount');
    // }
}

function authenticate(url){
    const token = sessionStorage.getItem("jwt");
    fetch(url, {
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
        authenticate('/');
    })
}

function closeForm() {
    document.getElementById("popupForm").style.display = "none";
}

function closeIntro() {
    document.getElementById("popupIntro").style.display = "none";
    document.getElementsByClassName("card-intro-flex")[0].style.filter = "none";
    document.getElementsByTagName("h2")[1].style.filter = "none";
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

function applyFor(item, category, tag){
    const token = sessionStorage.getItem("jwt");
    fetch('/manageApply',{
        method: 'post',
        body: JSON.stringify({'item': item, 'category': category, 'tag': tag}),
        headers: new Headers({
            'Authorization': 'Bearer '+token,
            'Content-Type': 'application/json'
        })
    })
    .then(res=>res.json())
    .then(res2=>alert(res2['status']))
    .catch(res3=>alert('尚未登入，請先登入再申辦'))
}

function openIntro(title, paragraph, webId){
    const token = sessionStorage.getItem("jwt");
    document.getElementsByClassName("card-intro-flex")[0].style.filter = "blur(10px)";
    document.getElementsByTagName("h2")[1].style.filter = "blur(10px)";
    document.getElementById("popupIntro").style.display = "block";
    document.getElementsByTagName("h3")[0].innerHTML = title;
    document.getElementsByTagName("p")[0].innerHTML = paragraph;
    fetch('/interestTag', {
        method: 'post',
        body: JSON.stringify({'web_id': webId}),
        headers: new Headers({
            'Authorization': 'Bearer '+token,
            'Content-Type': 'application/json'
        })

    })
}


function openIntroMulti(title, paragraph, webId){
    const token = sessionStorage.getItem("jwt");
    document.getElementsByClassName("card-intro-flex-multi")[0].style.filter = "blur(10px)";
    document.getElementsByTagName("h2")[1].style.filter = "blur(10px)";
    document.getElementById("popupIntro").style.display = "block";
    document.getElementsByTagName("h3")[0].innerHTML = title;
    document.getElementsByTagName("p")[0].innerHTML = paragraph;
    fetch('/interestTag', {
        method: 'post',
        body: JSON.stringify({'web_id': webId}),
        headers: new Headers({
            'Authorization': 'Bearer '+token,
            'Content-Type': 'application/json'
        })

    })
}

function closeIntroMulti() {
    document.getElementById("popupIntro").style.display = "none";
    document.getElementsByClassName("card-intro-flex-multi")[0].style.filter = "none";
    document.getElementsByTagName("h2")[1].style.filter = "none";
}