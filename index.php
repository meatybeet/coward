<?php
/**
 * PHP site test page.
 *
 * Upload this as index.php. The php vhost lists `index index.php index.html`, so
 * it wins over the placeholder page the deploy left behind, and unknown paths fall
 * back here (`try_files $uri $uri/ /index.php?$query_string`) — which is what makes
 * a front controller work.
 */

$uri       = $_SERVER['REQUEST_URI'] ?? '/';
$path      = parse_url($uri, PHP_URL_PATH);
$root      = $_SERVER['DOCUMENT_ROOT'] ?? getcwd();
$basedir   = ini_get('open_basedir') ?: '(not set)';
$user      = function_exists('posix_getpwuid')
    ? (posix_getpwuid(posix_geteuid())['name'] ?? '?')
    : get_current_user();

// open_basedir pins this pool to /home/<account>/web and /tmp. Reading outside it
// must fail — that failure is the isolation working, not a broken page.
$outside = @file_get_contents('/etc/passwd');

// Writing inside the site counts against the account's disk quota.
$probe   = $root . '/.write-probe';
$writable = @file_put_contents($probe, "ok\n") !== false;
if ($writable) { @unlink($probe); }

$extensions = ['mysqli', 'pdo_mysql', 'mbstring', 'curl', 'gd', 'zip', 'xml'];

// A front controller: any path that is not a real file lands here.
$isRoute = $path !== '/' && $path !== '/index.php';
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PHP site — WAYHOST hosting</title>
<style>
  body{margin:0;padding:40px 20px;font:16px/1.6 system-ui,sans-serif;background:#f2f5fb;color:#1a2b4b}
  main{max-width:720px;margin:0 auto;background:#fff;border:1px solid #e2e8f3;border-radius:12px;padding:28px 32px}
  h1{margin:0 0 6px;font-size:24px}
  h2{margin:26px 0 8px;font-size:16px;color:#5b6b8a}
  table{width:100%;border-collapse:collapse;font-size:14px}
  td{padding:7px 0;border-bottom:1px solid #eef1f7;vertical-align:top}
  td:first-child{color:#5b6b8a;width:190px}
  code{font-family:ui-monospace,monospace;background:#f2f5fb;padding:1px 5px;border-radius:4px;font-size:.9em;word-break:break-all}
  .ok{color:#0f7a52;font-weight:600}
  .no{color:#b42318;font-weight:600}
  .pill{display:inline-block;padding:2px 9px;border-radius:20px;font-size:12px;font-weight:600;margin:0 4px 4px 0}
  .has{background:#d1fae5;color:#065f46}
  .hasnt{background:#f1f5f9;color:#5b6b8a}
  a{color:#2b73f4}
  form{margin-top:8px;display:flex;gap:8px}
  input{flex:1;padding:8px 12px;border:1px solid #e2e8f3;border-radius:8px;font:inherit}
  button{padding:8px 16px;border:0;border-radius:8px;background:#2b73f4;color:#fff;font:inherit;cursor:pointer}
</style>
</head>
<body>
<main>
  <h1>PHP is running</h1>
  <p>Served through the PHP-FPM pool that belongs to this hosting account.</p>

  <?php if ($isRoute): ?>
    <p><strong>Front controller works.</strong> You asked for <code><?= htmlspecialchars($path) ?></code>,
       no such file exists, and nginx handed the request to <code>index.php</code> —
       the same mechanism a framework router relies on.
       <a href="/">back to /</a></p>
  <?php endif; ?>

  <h2>Runtime</h2>
  <table>
    <tr><td>PHP version</td><td><code><?= PHP_VERSION ?></code></td></tr>
    <tr><td>SAPI</td><td><code><?= php_sapi_name() ?></code> (expected <code>fpm-fcgi</code>)</td></tr>
    <tr><td>Running as</td><td><code><?= htmlspecialchars($user) ?></code> — your account, not www-data</td></tr>
    <tr><td>Document root</td><td><code><?= htmlspecialchars($root) ?></code></td></tr>
    <tr><td>open_basedir</td><td><code><?= htmlspecialchars($basedir) ?></code></td></tr>
    <tr><td>memory_limit</td><td><code><?= ini_get('memory_limit') ?></code></td></tr>
    <tr><td>upload_max_filesize</td><td><code><?= ini_get('upload_max_filesize') ?></code></td></tr>
  </table>

  <h2>Isolation</h2>
  <table>
    <tr>
      <td>Read <code>/etc/passwd</code></td>
      <td><?= $outside === false
            ? '<span class="ok">refused</span> — open_basedir is doing its job'
            : '<span class="no">allowed</span> — open_basedir is not applied' ?></td>
    </tr>
    <tr>
      <td>Write into the site</td>
      <td><?= $writable
            ? '<span class="ok">allowed</span> — and it counts against your disk quota'
            : '<span class="no">refused</span> — check the directory owner, or you are out of quota' ?></td>
    </tr>
  </table>

  <h2>Extensions</h2>
  <p>
    <?php foreach ($extensions as $extension): ?>
      <span class="pill <?= extension_loaded($extension) ? 'has' : 'hasnt' ?>"><?= $extension ?></span>
    <?php endforeach; ?>
  </p>
  <p style="font-size:13.5px;color:#5b6b8a">
    <code>mysqli</code> and <code>pdo_mysql</code> being present only means the client
    library is there. No MySQL server is installed on the node and no database is
    created per account, so there is nothing to connect to yet.
  </p>

  <h2>Request</h2>
  <table>
    <tr><td>Method / path</td><td><code><?= htmlspecialchars($_SERVER['REQUEST_METHOD'] . ' ' . $uri) ?></code></td></tr>
    <tr><td>Host header</td><td><code><?= htmlspecialchars($_SERVER['HTTP_HOST'] ?? '?') ?></code></td></tr>
    <tr><td>Client IP</td><td><code><?= htmlspecialchars($_SERVER['REMOTE_ADDR'] ?? '?') ?></code></td></tr>
    <tr><td>Server time</td><td><code><?= date('Y-m-d H:i:s') ?></code></td></tr>
    <tr><td>Query <code>name</code></td><td><code><?= htmlspecialchars($_GET['name'] ?? '(none)') ?></code></td></tr>
  </table>
  <form method="get" action="/">
    <input name="name" placeholder="type a name and submit" value="<?= htmlspecialchars($_GET['name'] ?? '') ?>">
    <button type="submit">Send</button>
  </form>

  <h2>Also try</h2>
  <ul>
    <li><a href="/api.php">/api.php</a> — a JSON endpoint.</li>
    <li><a href="/any/made/up/path">/any/made/up/path</a> — falls back here.</li>
    <li><a href="/index.php?name=wayhost">/index.php?name=wayhost</a> — query strings survive the fallback.</li>
  </ul>
</main>
</body>
</html>
