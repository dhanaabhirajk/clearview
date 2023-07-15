

window.addEventListener('DOMContentLoaded', function() {
  var input = document.getElementById('markdown-input');
  var output = document.getElementById('markdown-output');

  input.addEventListener('input', function() {
    var markdown = input.value;
    var html = window.markdownit({
      highlight: function (str, lang) {
        if (lang && hljs.getLanguage(lang)) {
          try {
            return hljs.highlight(str, { language: lang }).value;
          } catch (__) {}
        }
    
        return '';      }
    }).render(markdown);
    output.innerHTML = html;
  });
});
