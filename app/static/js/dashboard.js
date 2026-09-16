const boxes=document.querySelectorAll(".stat-box");
boxes.forEach((box)=>{
    box.addEventListener("mouseenter",()=>{
        box.style.boxShadow="0 0 25px #00E5FF";
    });
    box.addEventListener("mouseleave",()=>{
        box.style.boxShadow="none";
    });
});

// achievements
window.onload=()=>{
    const xp=document.querySelector(".xp-fill");
    if(xp){
        xp.animate(
            [
                {width:"0%"},
                {width:xp.style.width}
            ],
            {duration:1200}
        );
    }
}