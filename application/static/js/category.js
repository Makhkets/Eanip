//brows category
let browse = [document.getElementById('men1'), document.getElementById('women1'), document.getElementById('accessories1'),
document.getElementById('footwear1'), document.getElementById('bayItem1'), document.getElementById('electronics1'), document.getElementById('food1')]
let browseInput = document.getElementById('browseInput')
browse.forEach(function(item, key ) {
    item.onclick = browseInputSet;
});
function browseInputSet(){
    browseInput.value = this.lastChild.innerHTML;
}

//brand
let brand = [document.getElementById('apple1'), document.getElementById('asus1'), document.getElementById('gionee1')]
let brandInput = document.getElementById('brandInput')
brand.forEach(function(item, key ) {
    item.onclick = brandInputSet;
});
function brandInputSet(){
    brandInput.value = this.lastChild.innerHTML;
}

//colors
let color = [document.getElementById('black1'), document.getElementById('balckleather1'), document.getElementById('blackred1'),
document.getElementById('gold1'), document.getElementById('spacegrey1')]
let colorInput = document.getElementById('colorInput')
color.forEach(function(item, key ) {
    item.onclick = colorInputSet;
});
function colorInputSet(){
    colorInput.value = this.lastChild.innerHTML;
}

//price
// let priceInput = document.getElementById('priceInput')
// document.getElementById('apply').onclick = updatePrice;

// function updatePrice() {
//     let price = [document.getElementById('lower-value'), document.getElementById('upper-value')]
//     priceInput.value = price[0].innerHTML + ' to ' + price[1].innerHTML
// }