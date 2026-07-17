// Remove visitor_id from the address bar (it is persisted server-side in an httpOnly cookie)
(function () {
  try {
    var url = new URL(window.location.href);
    if (url.searchParams.has("visitor_id")) {
      url.searchParams.delete("visitor_id");
      var cleaned =
        url.pathname +
        (url.searchParams.toString() ? "?" + url.searchParams.toString() : "") +
        url.hash;
      window.history.replaceState({}, document.title, cleaned);
    }
  } catch (e) {}
})();

$("#offers").on("mousedown", "a.rdr, a.img-link", function () {
  url = this.dataset.href;
  if (url !== undefined) {
    this.href = "#"; 
  }
});

$("#offers").on("contextmenu", "a.rdr, a.img-link", function () {
  url = this.dataset.href;
  if (url !== undefined) {
    this.href = this.dataset.href; 
  }
});

$("#offers").on("click", "a.rdr, a.img-link", function () {
  url = this.dataset.href;
  if (url !== undefined) {
    window.open(url);
    return false;
  }
});

$(window).scroll(function () {
  if ($(this).scrollTop() > 100) {
    $(".scrollup").fadeIn();
  } else {
    $(".scrollup").fadeOut();
  }
});


$("body").on("click", ".scrollup, .scroll-to-top", function () {
  $("body").animate({ scrollTop: 0 }, 600);
// clear hash from URL
  history.pushState("",document.title,window.location.pathname + window.location.search);
  return false;
});


window.addEventListener("load", function(event) {
  setTimeout(function(){ $("#funnels").fadeIn(); }, 3000);
});

// Close funnel popup
$("#viewShowcase").on("click",".funnels-close", function(){
  $("#funnels > .row").empty();
});


// Show Cookie Agreement
let cookie = false;
let cookieContent = $(".cookie-disclaimer");

checkCookie();

if (cookie === true) { cookieContent.hide(); }

function setCookie(cname, cvalue, exdays) {
  var d = new Date();
  d.setTime(d.getTime() + exdays * 24 * 60 * 60 * 1000);
  var expires = "expires=" + d.toGMTString();
  document.cookie = cname + "=" + cvalue + "; " + expires;
}

function getCookie(cname) {
  var name = cname + "=";
  var ca = document.cookie.split(";");
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i].trim();
    if (c.indexOf(name) === 0) return c.substring(name.length, c.length);
  }
  return "";
}

function checkCookie() {
  var check = getCookie("showcaseAgreement");
  if (check !== "") {
    return (cookie = true);
  } else {
    return (cookie = false);
  }
}
$(".accept-cookie").click(function () {
  setCookie("showcaseAgreement", "accepted", 30);
  cookieContent.fadeOut(333);
});
