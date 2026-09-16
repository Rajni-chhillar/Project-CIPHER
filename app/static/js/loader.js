const progress = document.querySelector(".progress");
const loader = document.getElementById("loader");
const main = document.getElementById("main-content");
main.style.display = "none";
let width = 0;
const interval = setInterval(() => {
    width++;
    progress.style.width = width + "%";
    if(width >= 100){
        clearInterval(interval);
        loader.style.display = "none";
        main.style.display = "block";
        document.body.style.overflow = "auto";
    }
},30);