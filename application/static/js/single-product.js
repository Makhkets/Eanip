let stars = []
for (let i = 1; i <= 5; i++) {
    stars.push(document.getElementById(`star-rate${i}`))
}
let starChecker = document.getElementById('star-check')
stars.forEach(function(item, key ) {
    item.onclick = starsCheck;
})

function starsCheck() {
    let a = this.dataset.value
    stars.forEach(function(item, key, ) {
        if (key + 1 <= a) {
            item.src = '../static/img/star_zakrash.png'
        } else {
            item.src = '../static/img/star.png'
        }
    })
    starChecker.value = a;

}