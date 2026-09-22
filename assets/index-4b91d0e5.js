// Stand-in for a bundled SPA. Hand-written so the dist stays self-contained (no
// CDN, no network), but the shape is what a real build emits: one hashed module
// under assets/, mounted into #app, routing on the hash.

const routes = {
  '/': {
    title: 'Home',
    body: `
      <p>This is a single-page app served as a <strong>static</strong> site. nginx
         handed the browser <code>index.html</code> and the hashed bundle; everything
         after that happens in the page.</p>
      <p>Navigate with the links above, then <strong>refresh</strong>. The URL keeps
         its <code>#/route</code> and the page still loads — that is the point of hash
         routing on a host with no SPA fallback.</p>`
  },
  '/about': {
    title: 'About',
    body: `
      <p>You are on <code>#/about</code>. The server was never asked for
         <code>/about</code> — the hash never leaves the browser.</p>
      <p>With Vue Router in <em>history</em> mode this same view would live at
         <code>/about</code>, and reloading it would hit nginx, which has no rule
         sending unknown paths back to <code>index.html</code>, so it would 404.</p>`
  },
  '/build': {
    title: 'Build',
    body: `
      <p>To ship your own app:</p>
      <pre>npm run build          # writes ./dist
cd dist
zip -r ../site.zip .   # the CONTENTS, not the folder</pre>
      <p>Then upload <code>site.zip</code> to the site. Unpacking keeps the paths
         inside the archive, so zipping <code>dist/</code> itself would land your
         files in <code>&lt;root&gt;/dist/</code> and the site root would have no
         index.</p>`
  }
};

function view(path) {
  const route = routes[path] || {
    title: 'Not found',
    body: `<p>No route <code>${path}</code> in this build.</p>`
  };
  return `
    <header>
      <span class="logo">▲</span>
      <nav>
        <a href="#/" class="${path === '/' ? 'on' : ''}">Home</a>
        <a href="#/about" class="${path === '/about' ? 'on' : ''}">About</a>
        <a href="#/build" class="${path === '/build' ? 'on' : ''}">Build</a>
      </nav>
    </header>
    <main>
      <h1>${route.title}</h1>
      ${route.body}
      <footer>
        <span>route <code>${path}</code></span>
        <span>bundle <code>index-4b91d0e5.js</code></span>
        <span>loaded ${new Date().toLocaleTimeString()}</span>
      </footer>
    </main>`;
}

function render() {
  const path = location.hash.replace(/^#/, '') || '/';
  document.getElementById('app').innerHTML = view(path);
}

window.addEventListener('hashchange', render);
render();
