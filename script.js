document.documentElement.classList.add('js');
const menu = document.querySelector('#menu-toggle');
const mobile = window.matchMedia('(max-width: 760px)');
const setMenu = open => {
  if (mobile.matches) document.body.classList.toggle('menu-open', open);
  else document.body.classList.toggle('contents-hidden', !open);
  menu.setAttribute('aria-expanded', String(open));
};
menu.hidden = false;
setMenu(!mobile.matches);
menu.addEventListener('click', () => setMenu(menu.getAttribute('aria-expanded') !== 'true'));
mobile.addEventListener('change', () => {
  document.body.classList.remove('contents-hidden', 'menu-open');
  setMenu(!mobile.matches);
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && mobile.matches && document.body.classList.contains('menu-open')) {
    setMenu(false); menu.focus();
  }
});
const size = document.querySelector('#font-toggle');
size.hidden = false;
size.addEventListener('click', () => {
  const large = document.body.classList.toggle('large-text');
  size.setAttribute('aria-pressed', String(large));
  size.setAttribute('aria-label', large ? 'Restore text size' : 'Increase text size');
});
const search = document.querySelector('#topic-search');
const topicRoots = [...document.querySelectorAll('.sidebar .contents-list > .chapter')];
search.addEventListener('input', () => {
  const query = search.value.trim().toLocaleLowerCase();
  let matches = 0;
  const filter = (node, ancestorMatches = false) => {
    const title = node.querySelector(':scope > a')?.textContent.toLocaleLowerCase() || '';
    const ownMatch = title.includes(query);
    if (ownMatch) matches++;
    const children = [...node.querySelectorAll(':scope > ul > li')];
    const childMatches = children.map(child => filter(child, ancestorMatches || ownMatch));
    const visible = ancestorMatches || ownMatch || childMatches.some(Boolean);
    node.hidden = !visible;
    return visible;
  };
  topicRoots.forEach(node => filter(node));
  document.querySelectorAll('.sidebar .part-label').forEach(label => { label.hidden = Boolean(query); });
  document.querySelector('#search-status').textContent = query ? `${matches} matching topics` : '';
});
const active = document.querySelector('.sidebar a[aria-current="page"]');
if (active && !mobile.matches) {
  const sidebar = document.querySelector('.sidebar');
  sidebar.scrollTop = Math.max(0, active.offsetTop - sidebar.clientHeight / 2);
}
const updateProgress = () => {
  const max = document.documentElement.scrollHeight - window.innerHeight;
  if (max > 0) document.documentElement.style.setProperty('--scroll-progress', `${Math.min(100, Math.max(0, (window.scrollY / max) * 100))}%`);
};
addEventListener('scroll', updateProgress, {passive: true});
updateProgress();
