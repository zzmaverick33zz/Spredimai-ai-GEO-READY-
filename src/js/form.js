// Consultation form: validation, chips, success state. Submission goes to VITE_FORM_ENDPOINT;
// without it the form runs as a stub (nothing is sent).
const ENDPOINT = import.meta.env.VITE_FORM_ENDPOINT || '';

export function initForm() {
  const form = document.getElementById('form');
  const done = document.getElementById('formDone');
  const note = document.getElementById('stubNote');
  if (ENDPOINT && note) note.remove();
  const err = document.createElement('p');
  err.className = 'form-error'; err.setAttribute('role', 'alert'); err.hidden = true;
  form.querySelector('button[type=submit]').parentElement.append(err);

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const email = form.elements.email, name = form.elements.name;
    const okEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim());
    email.closest('.field').classList.toggle('is-invalid', !okEmail);
    document.getElementById('f-email-err').hidden = okEmail;
    name.closest('.field').classList.toggle('is-invalid', !name.value.trim());
    if (!name.value.trim()) { name.focus(); return; }
    if (!okEmail) { email.focus(); return; }

    const fd = new FormData(form);
    const payload = { ...Object.fromEntries(fd), type: fd.getAll('type') };
    const submit = form.querySelector('button[type=submit]');
    submit.disabled = true; err.hidden = true;
    try {
      if (ENDPOINT) {
        const r = await fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        if (!r.ok) throw new Error(String(r.status));
      } else {
        await new Promise(r => setTimeout(r, 400));
      }
      form.hidden = true; done.hidden = false;
      done.setAttribute('tabindex', '-1'); done.focus();
    } catch {
      err.textContent = 'Something went wrong. Please try again or write to info@bffloors.com.';
      err.hidden = false; submit.disabled = false;
    }
  });
}
