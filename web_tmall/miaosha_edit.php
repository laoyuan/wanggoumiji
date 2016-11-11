<?php
header('Content-Type: text/html; charset=utf-8');
date_default_timezone_set('PRC');

$db = 'tmall';
$con = mysql_connect('127.0.0.1:3306',"root","your_pass");
if (!$con){
    exit('Could not connect: '.mysql_error());
}
mysql_select_db($db, $con);
mysql_query("set names utf8");

$time = time();

if (isset($_POST['itemId'])) {
    $w9 = "update `tmall_items` set itemTitle = '".addslashes($_POST['itemTitle'])."', secKillTime = '$_POST[secKillTime]', itemNum = $_POST[itemNum], itemSecKillPrice = $_POST[itemSecKillPrice] where itemId = $_POST[itemId]";
    $q9 = mysql_query($w9) or exit('w9 error: '.mysql_error());
    header('Location: miaosha_list.php');
    exit;
}


if (isset($_GET['itemId'])) {
    $itemId = $_GET['itemId'];
    $w0 = "select * from `tmall_items` where itemId = $itemId";
    $q0 = mysql_query($w0) or exit('w0 error: '.mysql_error());
    $d0 = mysql_fetch_assoc($q0);
    if (!$d0) {
        exit('itemId not found');
    }
    
    $shang = '<form action="miaosha_edit.php" method="post" accept-charset="utf-8">';
    $shang .= '<input type="hidden" name="itemId" value="'.$itemId.'">';
    $shang .= 'Title: <input type="input" name="itemTitle" style="width: 600px;" value="'.$d0['itemTitle'].'"><br>';
    $shang .= 'Price: <input type="input" name="itemSecKillPrice" style="width: 600px;" value="'.$d0['itemSecKillPrice'].'"><br>';
    $shang .= 'Nums: <input type="input" name="itemNum" style="width: 600px;" value="'.$d0['itemNum'].'"><br>';
    $shang .= 'Time_seckill: <input type="input" name="secKillTime" style="width: 600px;" value="'.$d0['secKillTime'].'"><br>';
    $shang .= '<input type="submit" name="submit" value="编辑"></form>';
}


else {
    exit('data Wrong');
}

?>

<!doctype html>
<html>
    <head><meta http-equiv=Content-Type content="text/html;charset=utf-8" />
        <title>Edit - 天猫秒杀列表</title>
        <link href="../css.css" rel="stylesheet" type="text/css" />
    </head>

<body>
<div id="body">
    <div id="main" style="line-height: 33px; width: 1080px; font-size: 14px;">
        <br><br><h1 id="h1_t">编辑</h1>
        <?php
            echo $shang;
        ?>
    </div>
</div>
</body>
</html>
