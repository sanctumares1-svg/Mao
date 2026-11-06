self.onmessage = e => {
  const { id, url } = e.data;
  fetch(url).then(r => { if (!r.ok) throw 0; return r.text(); })
    .then(text => self.postMessage({ id, ok: true, text }))
    .catch(() => self.postMessage({ id, ok: false }));
};
