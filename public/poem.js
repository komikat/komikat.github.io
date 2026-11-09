const poems = [...document.querySelectorAll('[data-poem]')];
const selected = poems[Math.floor(Math.random() * poems.length)];
for (const poem of poems) poem.hidden = poem !== selected;
