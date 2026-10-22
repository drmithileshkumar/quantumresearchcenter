(() => {
  const map = document.querySelector('.quantum-map');
  if (!map) return;
  const branches = [...map.querySelectorAll('.qm-branch')];
  const expand = map.querySelector('[data-qm-expand]');
  const status = map.querySelector('[data-qm-status]');
  const visible = branch => {
    for (let parent = branch.parentElement.closest('details'); parent; parent = parent.parentElement.closest('details')) {
      if (!parent.open) return false;
    }
    return true;
  };
  function update() {
    const count = branches.filter(branch => branch.open && visible(branch)).length;
    expand.disabled = branches.every(branch => branch.open);
    status.textContent = `${count} branches expanded.`;
  }
  map.querySelector('.qm-controls').hidden = false;
  expand.addEventListener('click', () => {
    const next = branches.filter(branch => !branch.open && visible(branch));
    next.forEach(branch => { branch.open = true; });
    update();
  });
  map.querySelector('[data-qm-reset]').addEventListener('click', () => {
    branches.forEach(branch => { branch.open = branch.dataset.depth === '0'; });
    map.querySelector('.qm-viewport').scrollTo({ left: 0, top: 0, behavior: 'instant' });
    update();
  });
  branches.forEach(branch => branch.addEventListener('toggle', update));
  update();
})();
