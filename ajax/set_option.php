<?php
require_once('../lib/header_ajax.php');
require_once('../lib/lib_users.php');

try {
    if (!is_logged())
        throw new Exception();
    save_user_option($_POST['option'], $_POST['value']);
}
catch (Exception $e) {
    $result['error'] = 1;
}

log_timing(true);
die(json_encode($result));
