function setCookie(cookieName, cookieValue, expirationDays) {
    deleteCookie(cookieName); // Delete existing cookie
    var d = new Date();
    d.setTime(d.getTime() + (expirationDays * 24 * 60 * 60 * 1000)); // Calculate expiration date
    var expires = "expires=" + d.toUTCString();
    document.cookie = cookieName + "=" + cookieValue + ";" + expires + ";path=/";
}
function getCookie(cookieName) {
    var name = cookieName + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookieArray = decodedCookie.split(";");

    for (var i = 0; i < cookieArray.length; i++) {
        var cookie = cookieArray[i].trim();
        if (cookie.indexOf(name) === 0) {
        return cookie.substring(name.length, cookie.length);
        }
    }

    return null;
}

function deleteCookie(cookieName) {
  document.cookie = cookieName + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}

function autoResize() {
  const textArea = document.getElementById("user-query");
  textArea.style.height = "auto";
  textArea.style.height = textArea.scrollHeight + "px";
}

function render_markdown(markdown) {
return window.markdownit({
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value;
      } catch (__) {}
    }

    return '';      }
}).render(markdown);
}

