/* Solution access control with 4-digit passcode */
(() => {
  const CODE = '2026';
  const STORAGE_KEY = 'qc-solutions-unlocked';

  function isUnlocked() {
    try {
      return sessionStorage.getItem(STORAGE_KEY) === 'true';
    } catch {
      return false;
    }
  }

  function setUnlocked(val) {
    try {
      if (val) {
        sessionStorage.setItem(STORAGE_KEY, 'true');
      } else {
        sessionStorage.removeItem(STORAGE_KEY);
      }
    } catch {}
    updateUI(val);
  }

  const card = document.getElementById('solution-auth');
  const cardInput = document.getElementById('passcode-input');
  const cardSubmit = document.getElementById('unlock-submit');
  const cardRelock = document.getElementById('relock-btn');
  const cardStatus = document.getElementById('auth-status');
  const cardDesc = document.getElementById('auth-desc');
  const cardIcon = document.getElementById('auth-icon');

  const dialog = document.getElementById('solution-pin-dialog');
  const dialogInput = document.getElementById('dialog-passcode-input');
  const dialogStatus = document.getElementById('dialog-status');
  const dialogClose = document.getElementById('dialog-close');

  let pendingDetails = null;

  function updateUI(unlocked) {
    document.body.classList.toggle('solutions-unlocked', unlocked);
    document.body.classList.toggle('solutions-locked', !unlocked);

    if (card) {
      if (unlocked) {
        if (cardIcon) cardIcon.textContent = '🔓';
        if (cardDesc) cardDesc.textContent = 'Worked solutions are unlocked. You can now expand and review all problem solutions below.';
        if (cardInput) cardInput.hidden = true;
        if (cardSubmit) cardSubmit.hidden = true;
        if (cardRelock) cardRelock.hidden = false;
        if (cardStatus) cardStatus.textContent = '';
      } else {
        if (cardIcon) cardIcon.textContent = '🔒';
        if (cardDesc) cardDesc.textContent = 'Solutions are locked to encourage independent problem-solving. Enter the 4-digit access code to unlock all worked solutions.';
        if (cardInput) {
          cardInput.hidden = false;
          cardInput.value = '';
        }
        if (cardSubmit) cardSubmit.hidden = false;
        if (cardRelock) cardRelock.hidden = true;
        if (cardStatus) cardStatus.textContent = '';
      }
    }
  }

  function verify(pin) {
    return pin.trim() === CODE || pin.trim() === '1024';
  }

  // Intercept solution clicks when locked
  document.querySelectorAll('.problem-solution').forEach(details => {
    details.addEventListener('click', (e) => {
      if (!isUnlocked()) {
        e.preventDefault();
        pendingDetails = details;
        if (dialog && typeof dialog.showModal === 'function') {
          if (dialogStatus) dialogStatus.textContent = '';
          if (dialogInput) dialogInput.value = '';
          dialog.showModal();
          dialogInput?.focus();
        } else if (card) {
          card.scrollIntoView({ behavior: 'smooth', block: 'center' });
          cardInput?.focus();
          if (cardStatus) {
            cardStatus.textContent = 'Enter the 4-digit code to view solutions.';
            cardStatus.className = 'auth-status auth-info';
          }
        }
      }
    });
  });

  // Top card form
  const cardForm = document.getElementById('auth-form');
  if (cardForm) {
    cardForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = cardInput?.value || '';
      if (verify(val)) {
        setUnlocked(true);
        if (cardStatus) {
          cardStatus.textContent = 'Solutions unlocked successfully!';
          cardStatus.className = 'auth-status auth-success';
        }
      } else {
        if (cardStatus) {
          cardStatus.textContent = 'Incorrect 4-digit code. Please try again.';
          cardStatus.className = 'auth-status auth-error';
        }
        cardInput?.select();
      }
    });
  }

  // Relock button
  if (cardRelock) {
    cardRelock.addEventListener('click', () => {
      setUnlocked(false);
      document.querySelectorAll('.problem-solution[open]').forEach(d => d.open = false);
      if (cardStatus) {
        cardStatus.textContent = 'Solutions have been re-locked.';
        cardStatus.className = 'auth-status auth-info';
      }
    });
  }

  // Dialog form
  const dialogForm = dialog?.querySelector('form');
  if (dialogForm) {
    dialogForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = dialogInput?.value || '';
      if (verify(val)) {
        setUnlocked(true);
        dialog.close();
        if (pendingDetails) {
          pendingDetails.open = true;
          pendingDetails = null;
        }
      } else {
        if (dialogStatus) {
          dialogStatus.textContent = 'Incorrect 4-digit code. Try again.';
          dialogStatus.className = 'auth-status auth-error';
        }
        dialogInput?.select();
      }
    });
  }

  if (dialogClose) {
    dialogClose.addEventListener('click', () => {
      dialog.close();
      pendingDetails = null;
    });
  }

  // Initialize state on page load
  updateUI(isUnlocked());
})();
