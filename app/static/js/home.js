const animateValue = (id, end, speed) => {
    let start = 0;
    const obj = document.getElementById(id);
    const timer = setInterval(()=>{
        start++;
        obj.innerHTML=start;
        if(start>=end){
            clearInterval(timer);
        }
    },speed);
}
animateValue("players",1850,2);
animateValue("missions",32,40);
animateValue("cases",542,5);
animateValue("countries",18,70);

// features
const reveals=document.querySelectorAll(".reveal");
window.addEventListener("scroll",()=>{
    reveals.forEach((card)=>{
        const top=card.getBoundingClientRect().top;
        const visible=window.innerHeight-100;
        if(top<visible){
            card.classList.add("active");
        }
    });
});

// typing animation
const text="PROJECT CIPHER";
let i=0;
const heading=document.getElementById("typing-text");
function typeText(){
    if(i<text.length){
        heading.innerHTML+=text.charAt(i);
        i++;
        setTimeout(typeText,120);
    }
}
typeText();

// mouse glow 
const glow=document.getElementById("cursor-glow");
document.addEventListener("mousemove",(e)=>{
    glow.style.left=e.clientX+"px";
    glow.style.top=e.clientY+"px";
});

// scroll to top

const topBtn=document.getElementById("topBtn");
window.addEventListener("scroll",()=>{
    if(window.scrollY>300){
        topBtn.style.display="block";
    }else{
        topBtn.style.display="none";
    }
});

topBtn.addEventListener("click",()=>{
    window.scrollTo({
        top:0,
        behavior:"smooth"
    });
});