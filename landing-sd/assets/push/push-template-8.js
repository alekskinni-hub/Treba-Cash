elMax = pushMessages.length-1;

$("div.push-message").each(function(i) { this.remove(); });
clearInterval(getRandMsg);

function getRandomIntInclusive(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

$("#push-container").on("click", "span.push-close", function () {
  $("div.push-message").remove();
  clearInterval(getRandMsg);
});

function getRandPushMessage() {
  $("#push-container").append('<div id="pushTheme8" class="push-message"><span class="push-message-text">' + pushMessages[getRandomIntInclusive(0, elMax)] + "</span><span class=\"push-close\"><img src=\"data:image/svg+xml,%3C%3Fxml version='1.0' encoding='utf-8'%3F%3E%3Csvg version='1.2' baseProfile='tiny' id='Слой_1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x='0px' y='0px' viewBox='0 0 20 20' xml:space='preserve'%3E%3Cpath fill='%23333333' d='M0,10.8c-0.1-1.3,0-2.6,0.4-3.9c0.4-1.4,1.2-2.7,2.3-3.8c0.7-0.7,1.5-1.4,2.4-1.9c2.9-1.6,6.7-1.7,9.6-0.1 c0.2,0.1,0.3,0.2,0.5,0.3c1.2,0.7,2.1,1.6,2.9,2.7c1.9,2.7,2.4,6.2,1.3,9.3c-0.5,1.3-1.2,2.5-2.2,3.5c-0.7,0.7-1.5,1.4-2.4,1.9 c-2.9,1.6-6.7,1.7-9.6,0.1c-0.2-0.1-0.3-0.2-0.5-0.3c-1.2-0.7-2.1-1.6-2.9-2.7C0.8,14.4,0.2,12.6,0,10.8z M10,11.7 c1.2,1.2,2.3,2.4,3.5,3.5c0.6-0.6,1.1-1.2,1.7-1.8c-1.2-1.1-2.3-2.3-3.5-3.5c1.2-1.2,2.3-2.3,3.5-3.4c-0.6-0.6-1.1-1.1-1.7-1.7 c-1.1,1.2-2.3,2.3-3.5,3.5C8.8,7.1,7.6,5.9,6.5,4.8C5.9,5.4,5.4,5.9,4.7,6.5C5.9,7.7,7.1,8.8,8.3,10c-1.2,1.2-2.3,2.3-3.5,3.5 c0.6,0.6,1.1,1.1,1.7,1.7C7.6,14.1,8.8,12.9,10,11.7z'/%3E%3C/svg%3E%0A\"></span></div>");
  $("div.push-message").fadeIn(500);
  setTimeout(function () { $("div.push-message").fadeOut(500); }, 4000);
  setTimeout(function () { $("div.push-message").remove(); }, 5000); 
}

var getRandMsg = setInterval(getRandPushMessage, 10000);
$("#push-container").append('<div id="pushTheme8" class="push-message"><span class="push-message-text">' + pushMessages[getRandomIntInclusive(0, elMax)] + "</span><span class=\"push-close\"><img src=\"data:image/svg+xml,%3C%3Fxml version='1.0' encoding='utf-8'%3F%3E%3Csvg version='1.2' baseProfile='tiny' id='Слой_1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x='0px' y='0px' viewBox='0 0 20 20' xml:space='preserve'%3E%3Cpath fill='%23333333' d='M0,10.8c-0.1-1.3,0-2.6,0.4-3.9c0.4-1.4,1.2-2.7,2.3-3.8c0.7-0.7,1.5-1.4,2.4-1.9c2.9-1.6,6.7-1.7,9.6-0.1 c0.2,0.1,0.3,0.2,0.5,0.3c1.2,0.7,2.1,1.6,2.9,2.7c1.9,2.7,2.4,6.2,1.3,9.3c-0.5,1.3-1.2,2.5-2.2,3.5c-0.7,0.7-1.5,1.4-2.4,1.9 c-2.9,1.6-6.7,1.7-9.6,0.1c-0.2-0.1-0.3-0.2-0.5-0.3c-1.2-0.7-2.1-1.6-2.9-2.7C0.8,14.4,0.2,12.6,0,10.8z M10,11.7 c1.2,1.2,2.3,2.4,3.5,3.5c0.6-0.6,1.1-1.2,1.7-1.8c-1.2-1.1-2.3-2.3-3.5-3.5c1.2-1.2,2.3-2.3,3.5-3.4c-0.6-0.6-1.1-1.1-1.7-1.7 c-1.1,1.2-2.3,2.3-3.5,3.5C8.8,7.1,7.6,5.9,6.5,4.8C5.9,5.4,5.4,5.9,4.7,6.5C5.9,7.7,7.1,8.8,8.3,10c-1.2,1.2-2.3,2.3-3.5,3.5 c0.6,0.6,1.1,1.1,1.7,1.7C7.6,14.1,8.8,12.9,10,11.7z'/%3E%3C/svg%3E%0A\"></span></div>");
$("div.push-message").fadeIn(500);
