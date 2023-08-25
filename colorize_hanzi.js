// The following code changes the text color
// of hanzi according to pinyin tones.
// You can change the colors in the CSS

function colorHanzi(html, hanzi, pinyin) {
  function getTones(pinyin) {
    function getToneNumber(diac) {
      var allDiacs = ['āēīōūǖ','áéíóúǘ','ǎěǐǒǔǚ','àèìòùǜ','aeiouür'];
      for (var i = 0; i < allDiacs.length; i++) {
        if (allDiacs[i].includes(diac)) {
          return i+1;
        }
      }
      return 0;
    }
    var a = '([aāáǎà])';
    var e = '([eēéěè])';
    var ae = '([aāáǎàeēéěè])';
    var i = '([iīíǐì])';
    var o = '([oōóǒò])';
    var u = '([uūúǔùüǖǘǚǜ])';
    var eu = '([eēéěèuūúǔù])';
    var regex=
      '(?:'
        +'(?:'
          +'mi'+u
          +'|[pm]'+o+'u'
          +'|[bpm](?:'
              +o
              +'|'+e+'(?:i|ng??)?'
              +'|'+a+'(?:ng?|i|o)?'
              +'|i(?:'+e+'|'+a+'[no])'
              +'|'+i+'(?:ng?)?'
              +'|'+u
            +')'
          +')'
        +'|(?:f(?:'+o+'u?|'+ae+'(?:ng?|i)?|'+u+'))'
        +'|(?:'
          +'d(?:'+e+'(?:i|ng?)|i(?:'+a+'[on]?|'+u+'))'
          +'|[dt](?:'
              +a+'(?:i|ng?|o)?'
              +'|'+e+'(?:i|ng)?'
              +'|i(?:'+a+'[on]?|'+eu+')'
              +'|'+i+'(?:ng)?'
              +'|'+o+'(?:ng?|u)'
              +'|u(?:'+o+'|'+i+'|'+a+'n?)'
              +'|'+u+'n?'
            +')'
          +')'
        +'|(?:'
          +'n'+e+'ng?'
          +'|[ln](?:'
              +a+'(?:i|ng?|o)?'
              +'|'+e+'(?:i|ng)?'
              +'|i(?:'+a+'ng|'+a+'[on]?|'+e+'|'+u+')'
              +'|'+i+'(?:ng?)?'
              +'|'+o+'(?:ng?|u)'
              +'|u(?:'+o+'|'+a+'n?)'
              +'|ü'+e+'?'
              +'|'+u+'n?'
            +')'
          +')'
        +'|(?:[ghk](?:'+a+'(?:i|ng??|o)?|'+e+'(?:i|ng?)?|'+o+'(?:u|ng)|u(?:'+a+'(?:i|ng??)??|'+i+'|'+o+')|'+u+'n?))'
        +'|(?:zh?'+e+'i|[cz]h?(?:'+e+'(?:ng?)?|'+o+'(?:ng?|u)?|'+a+'o|u?'+a+'(?:i|ng?)?|u?(?:'+o+'|'+i+')|'+u+'n?))'
        +'|(?:'
          +'s'+o+'ng'
          +'|shu'+a+'(?:i|ng?)?'
          +'|sh'+e+'i'
          +'|sh?(?:'
              +a+'(?:i|ng?|o)?'
              +'|'+e+'n?g?'
              +'|'+o+'u'
              +'|u(?:'+a+'n|'+o+'|'+i+')'
              +'|'+u+'n?'
              +'|'+i
            +')'
          +')'
        +'|(?:'
          +'r(?:'
            +ae+'ng?'
            +'|'+i
            +'|'+e
            +'|'+a+'o'
            +'|'+o+'u'
            +'|'+o+'ng'
            +'|u(?:'+o+'|'+i+')'
            +'|u'+a+'n?'
            +'|'+u+'n?'
            +')'
          +'|(r)'
          +')'
        +'|(?:[jqx](?:i(?:'+a+'(o|ng??)?|(?:'+e+'|'+u+')|'+o+'ng)|'+i+'(?:ng?)??|u(?:'+e+'|'+a+'n)|'+u+'n??))'
        +'|(?:'
          +'(?:'
              +a+'(?:i|o|ng?)?'
              +'|'+o+'u?'
              +'|'+e+'(?:i|ng?|r)?'
            +')'
          +')'
        +'|(?:w(?:'+a+'(?:i|ng??)?|'+o+'|'+e+'(?:i|ng?)?|'+u+'))'
        +'|y(?:'+a+'(?:o|ng??)?|'+e+'|'+i+'(?:ng?)?|'+o+'(?:u|ng)?|u(?:'+e+'|'+a+'n)|'+u+'n??)'
      +')'
      +'([12345])?';
    pinyin = pinyin.normalize();
    pinyin = pinyin.split('/')[0];
    pinyin = pinyin.trim();
    const re = new RegExp(regex, 'g');
    const matches = pinyin.matchAll(re);
    var tones = Array.from(matches).map(function (match) {
      var m = match;
      m.shift();
      var diac = m.filter(function(v) { return v !== undefined; });
      if (diac.length > 0) {
        if (diac.length > 1 && '12345'.includes(diac[1])) {
          return parseInt(diac[1]); // tone as pinyin number
        } else {
          return getToneNumber(diac[0]); // tone as pinyin diacritic
        }
      } else {
        return 0;
      }
    });
    return tones;
  }

  pinyin = pinyin.toLowerCase();
  var tones = getTones(pinyin);

  hanzi = hanzi.normalize();
  // \p{Han} according to ftp://ftp.unicode.org/Public/UNIDATA/Scripts.txt (only codepoints lower than U+FFFF)
  const Han = '\u2E80-\u2E99\u2E9B-\u2EF3\u2F00-\u2FD5\u3005\u3007\u3021-\u3029\u3038-\u303A\u303B\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFA6D\uFA70-\uFAD9';
  const hanziRe = '[/0-9'+Han+']';
  const re = new RegExp(hanziRe, 'gu');
  var memory = {};
  var n = 0;
  return html.replace(re, function (match) {
    if (match == '/') {
      n = 0;
      return match;
    }
    var tone = tones[n++];
    if (tone === undefined && match in memory) {
      tone = memory[match];
    }
    if (tone !== undefined) {
      memory[match] = tone;
      var tag = '<span class="tone tone-' + tone + '">' + match + '</span>';
      return tag;
    } else {
      return match;
    }
  });
}

function colorFlashCard() {
  var pinyin = document.getElementById("ddzw-pinyin");
  if (!pinyin)
    return;

  var hanziElem = document.getElementById("ddzw-hanzi");
  if (!hanziElem)
    return;

  hanziElem.innerHTML = colorHanzi(hanziElem.innerHTML, hanziElem.textContent, pinyin.innerText);
}

try {
  module.exports = {
    colorHanzi: colorHanzi
  }
} catch (e) {
}

if (typeof require === 'undefined' || typeof require.main === 'undefined') {
  colorFlashCard();
}
