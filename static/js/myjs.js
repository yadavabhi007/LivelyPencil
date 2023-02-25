const img = document.querySelectorAll('img')
img.forEach(ele=>{
    ele.addEventListener('error',(e)=>{
        e.target.src="/home/mobapps/Downloads/livelypencilrepo/static/images/about-2.jpg"
    })
})