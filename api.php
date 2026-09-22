<?php
/**
 * A JSON endpoint, to check the pool from the command line:
 *
 *   curl -s http://<your-domain>/api.php | jq
 */
header('Content-Type: application/json; charset=utf-8');

echo json_encode([
    'ok'          => true,
    'php'         => PHP_VERSION,
    'sapi'        => php_sapi_name(),
    'user'        => function_exists('posix_getpwuid')
        ? (posix_getpwuid(posix_geteuid())['name'] ?? null)
        : get_current_user(),
    'root'        => $_SERVER['DOCUMENT_ROOT'] ?? null,
    'open_basedir'=> ini_get('open_basedir') ?: null,
    'host'        => $_SERVER['HTTP_HOST'] ?? null,
    'time'        => date('c'),
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
