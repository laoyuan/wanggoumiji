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

//编辑
if (isset($_GET['end']) && isset($_GET['itemId'])) {
    $itemId = addslashes($_GET['itemId']);
    $end_time = strftime("%Y-%m-%d %H:%M:%S", $time);
    $w9 = "update `tmall_items` set secKillTime = '$end_time' where itemId = '$itemId'";
    $q9 = mysql_query($w9) or exit($w9.'<br>w9 error: '.mysql_error());
}


$secKillTime = '';
$ar_row = [];
$ar_act_id = [];
$ar_act = [];
$w0 = "select * from `tmall_items` where auctionStatus >= 0 order by secKillTime, itemNum desc";
$q0 = mysql_query($w0) or exit('w0 error: '.mysql_error());
while ($row = mysql_fetch_assoc($q0)) {
    $ar_row[$row['id']] = $row;
    if ($row['act_id'] > 0) {
        $ar_act_id[$row['act_id']] = $row['act_id'];
    }
}

if ($ar_act_id) {
    $ids_act = implode(',', $ar_act_id);
    $w1 = "select * from `tmall_acts` where id in ($ids_act)";
    $q1 = mysql_query($w1) or exit('w1 error: '.mysql_error());
    while ($row = mysql_fetch_assoc($q1)) {
        $ar_act[$row['id']] = $row;
    }
}


//输出部分
$shang = '<table><tbody>';

foreach ($ar_row as $row) {
    if(strtotime($row['secKillTime']) < $time && $row['secKillTime'] != '0000-00-00 00:00:00') {
        continue;
    }

    if($row['secKillTime'] != $secKillTime) {
       $shang .= '<tr><td>　</td></tr><tr><td><b>' . $row['secKillTime'] . '</b></td><td></td><td></td><td></td><td></td></tr>'; 
    }

    $secKillTime = $row['secKillTime'];

    $shang .= '<tr>';

        $shang .= '<td><a target="_blank" href="https://detail.tmall.com/item.htm?id=' . $row['itemId'] . '">' . $row['itemTitle'] . '　</a></td>';
        $shang .= '<td><a href="' . (array_key_exists($row['act_id'], $ar_act) ? $ar_act[$row['act_id']]['act_url'] : '#') . '">' . fn_price_format($row['itemSecKillPrice']) . '元</a>　</td>';
        $shang .= '<td><a href="miaosha_edit.php?itemId=' . urlencode($row['itemId']) . '">' . ($row['itemNum'] ? $row['itemNum'] : '?') . '件</a></td>';
        $shang .= '<td><a target="_blank" href="http://miao.item.taobao.com/'.$row['itemId'].'.htm">http://miao.item.taobao.com/' . $row['itemId'] .  '.htm</a></td>';

    $shang .= '</tr>';
}

$shang .= '</tbody></table>';

function fn_price_format($price)
{
    if($price <= 0)
        $price_f = '?';
    else
        $price_f = preg_replace("/.00$|0$/",'', number_format($price/100, 2));
    return $price_f;
}
?>

<!doctype html>
<html>
    <head><meta http-equiv=Content-Type content="text/html;charset=utf-8" />
        <title>天猫秒杀列表</title>
        <link href="../css.css" rel="stylesheet" type="text/css" />
    </head>

<body>
<div id="body">
    <div id="main" style="line-height: 33px; width: 1080px; font-size: 14px;">
        <?php
            echo $shang;
        ?>
    </div>
</div>
</body>
</html>
