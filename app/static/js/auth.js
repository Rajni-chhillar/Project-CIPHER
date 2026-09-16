const password =document.getElementById("password");
const strength =document.getElementById("strength");

if(password){
    password.addEventListener("input",()=>{
        let value=password.value;
        if(value.length < 5){
            strength.innerHTML="Weak Password";
        }
        else if(value.length < 8){
            strength.innerHTML="Medium Password";
        }
        else{
            strength.innerHTML="Strong Password 🔥";
        }
    });
}

// show password

function showPassword(id){
    const input=document.getElementById(id);
    if(input.type==="password"){
        input.type="text";
    }
    else{
        input.type="password";
    }
}

const forms=document.querySelectorAll("form");
forms.forEach(form=>{
    form.addEventListener("submit",()=>{
        const button=form.querySelector("button");
        button.innerHTML="Processing... ⏳";
        button.style.opacity="0.7";
    });
});