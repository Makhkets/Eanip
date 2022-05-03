//brows category
let browse = [document.getElementById('unbrowse1'), document.getElementById('men1'), document.getElementById('women1'), document.getElementById('accessories1'),
document.getElementById('footwear1'), document.getElementById('bayItem1'), document.getElementById('electronics1'),
document.getElementById('electroproduct1'), document.getElementById('animals1'), document.getElementById('buisness1'), document.getElementById('equipment1')]
let browseInput = document.getElementById('browseInput')
browse.forEach(function(item, key ) {
    item.onclick = browseInputSet;
});
function browseInputSet(){
    browseInput.value = this.lastChild.innerHTML;
}

//brand
let brand = [document.getElementById('unchecking1'),document.getElementById('apple1'), document.getElementById('asus1'), document.getElementById('gionee1')]
let brandInput = document.getElementById('brandInput')
brand.forEach(function(item, key ) {
    item.onclick = brandInputSet;
});
function brandInputSet(){
    brandInput.value = this.lastChild.innerHTML;
}

//colors
let color = [document.getElementById('uncolor1'),document.getElementById('black1'), document.getElementById('balckleather1'), document.getElementById('uncolor'), document.getElementById('blackred1'),
document.getElementById('gold1'), document.getElementById('spacegrey1'),document.getElementById('orange1'), document.getElementById('purple1'),
document.getElementById('gray1'), document.getElementById('blue1')]
let colorInput = document.getElementById('colorInput')
color.forEach(function(item, key ) {
    item.onclick = colorInputSet;
});
function colorInputSet(){
    colorInput.value = this.lastChild.innerHTML;
}
