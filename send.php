<?php
// ekam vets booking form handler.
// Every submission is logged first, then emailed over SMTP. The log means a
// request is never lost even if mail fails.

$TO   = 'hello@ekamvets.com';
$LOG  = __DIR__ . '/../form-log.txt';
$CONF = __DIR__ . '/../mail-config.php';

$lang   = (isset($_POST['lang']) && $_POST['lang'] === 'hi') ? 'hi' : 'en';
$thanks = $lang === 'hi' ? '/hi/thanks.html' : '/thanks.html';
$fail   = $lang === 'hi' ? '/hi/visit.html?e=1' : '/visit.html?e=1';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: /visit.html'); exit; }
if (!empty($_POST['website'])) { header('Location: ' . $thanks); exit; }  // honeypot

function f($k) { return isset($_POST[$k]) ? trim(strip_tags((string)$_POST[$k])) : ''; }
$name = f('n'); $phone = f('p'); $animal = f('a');
$need = f('s'); $when = f('d'); $msg = f('m');
if ($name === '' || $phone === '') { header('Location: ' . $fail); exit; }

$subject = 'Booking request: ' . $name . ' (' . ($need ?: 'no service chosen') . ')';
$body  = "New booking request from ekamvets.com\n";
$body .= "======================================\n\n";
$body .= "Name            : $name\n";
$body .= "Phone / WhatsApp: $phone\n";
$body .= "Animal          : $animal\n";
$body .= "Needs           : $need\n";
$body .= "Preferred time  : $when\n\n";
$body .= "What is going on:\n" . ($msg ?: '(nothing written)') . "\n\n";
$body .= "--------------------------------------\n";
$body .= 'Language : ' . ($lang === 'hi' ? 'Hindi' : 'English') . "\n";
$body .= 'Submitted: ' . date('d M Y, H:i') . " server time\n";
$body .= 'IP       : ' . ($_SERVER['REMOTE_ADDR'] ?? '') . "\n";

@file_put_contents($LOG, "\n=== " . date('c') . " ===\n" . $body, FILE_APPEND | LOCK_EX);

function smtp_send($cfg, $to, $subject, $body) {
    $host = $cfg['host'] ?? 'smtp.hostinger.com';
    $port = $cfg['port'] ?? 465;
    $user = $cfg['user'] ?? '';
    $pass = $cfg['pass'] ?? '';
    if ($user === '' || $pass === '') return false;

    $fp = @stream_socket_client("ssl://$host:$port", $e, $s, 20);
    if (!$fp) return false;
    $read = function () use ($fp) {
        $out = '';
        while (($line = fgets($fp, 1024)) !== false) {
            $out .= $line;
            if (strlen($line) < 4 || $line[3] === ' ') break;
        }
        return $out;
    };
    $cmd = function ($c, $expect) use ($fp, $read) {
        if ($c !== null) fwrite($fp, $c . "\r\n");
        $r = $read();
        return substr($r, 0, 3) == $expect;
    };
    $ok = $cmd(null, '220')
       && $cmd('EHLO ekamvets.com', '250')
       && $cmd('AUTH LOGIN', '334')
       && $cmd(base64_encode($user), '334')
       && $cmd(base64_encode($pass), '235')
       && $cmd('MAIL FROM:<' . $user . '>', '250')
       && $cmd('RCPT TO:<' . $to . '>', '250')
       && $cmd('DATA', '354');
    if ($ok) {
        $headers  = 'From: ekam vets website <' . $user . ">\r\n";
        $headers .= 'To: <' . $to . ">\r\n";
        $headers .= 'Reply-To: <' . $user . ">\r\n";
        $headers .= 'Subject: ' . $subject . "\r\n";
        $headers .= "MIME-Version: 1.0\r\n";
        $headers .= "Content-Type: text/plain; charset=UTF-8\r\n\r\n";
        $data = preg_replace('/^\./m', '..', $body);
        fwrite($fp, $headers . $data . "\r\n.\r\n");
        $ok = $cmd(null, '250');
    }
    @fwrite($fp, "QUIT\r\n");
    @fclose($fp);
    return $ok;
}

$cfg = file_exists($CONF) ? (include $CONF) : null;
if (is_array($cfg)) { @smtp_send($cfg, $TO, $subject, $body); }

header('Location: ' . $thanks);
exit;
