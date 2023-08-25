c = require('./colorize_hanzi.js');

fixtures = [
  ["推薦信",         "tuījiànxìn",             [1, 4, 4]],
  ["軟體",           "ruǎntǐ",                 [3, 3]],
];

let passed = 0, total = 0;

fixtures.forEach((fixture) => {
  let hanzis, pinyin, exceptedTones;
  [hanzis, pinyin, exceptedTones] = fixture;
  let hanzisList = hanzis.split('');
  let expectedHtml = exceptedTones
    .map((tone) => {
      let hanzi = hanzisList.shift();
      return '<span class="tone tone-'+tone+'">'+hanzi+'</span>';
    })
    .join('');

  let result = c.colorHanzi(hanzis, hanzis, pinyin);

  let msg = hanzis + '(' + pinyin + ')' + ' tones are not ' + exceptedTones + ': ' + result;
  let assertion = result == expectedHtml;
  console.assert(assertion, msg);
  passed += assertion;
  total += 1;
});

console.log('Tests passed: ' + passed + '/' + total);
if (passed == total) {
  console.log('All OK.')
}
