<!DOCTYPE html>
<html>
<head>
<title>筛选节目源</title>
<style>
body {
  background-color: black;
  color: yellow;
}
#output-container {
  position: relative;
}

#copy-button {
  position: absolute;
  top: 0;
  right: 0;
}
</style>
<script>
function autoResizeTextarea(element) {
  element.style.height = "auto";
  element.style.height = (element.scrollHeight) + "px";
}

function copyToClipboard() {
  var output = document.getElementById("output");
  output.select();
  document.execCommand("copy");
}
</script>
</head>
<body>
<style>
textarea {
  width: 100%;

  resize: vertical;
}
</style>
<h1>整理节目源</h1>

<p>    自动更换成统一节目名称（数据表自己个性整理），过滤重复的地址以及一些错误的地址，同时去掉一些源被私贴标识。</p>
<form method="post">
    <textarea name="input" placeholder="请输入节目源，如：
台湾地区,#genre#
年代新聞,http://64.176.42.202/dynamic/5.php?id=live1192
東森新聞HD,http://64.176.42.202/dynamic/5.php?id=live1014
中天新聞HD,http://64.176.42.202/dynamic/5.php?id=live1015
民視新聞,http://64.176.42.202/dynamic/5.php?id=live1204"  id="input" rows="10" cols="50" required oninput="autoResizeTextarea(this)"></textarea><br>


  <input type="submit" value=" 提 交 ">
</form><br>
<div id="output-container">
  <label for="output">整理好后：</label><br>
  <textarea id="output" placeholder="
台湾地区,#genre#
年代新闻,http://64.176.42.202/dynamic/5.php?id=live1192
东森新闻,http://64.176.42.202/dynamic/5.php?id=live1014
中天新闻,http://64.176.42.202/dynamic/5.php?id=live1015
民视新闻,http://64.176.42.202/dynamic/5.php?id=live1204" rows="10" cols="50" readonly oninput="autoResizeTextarea(this)"><?php echo filterProgramSources(); ?></textarea><br>
  <button id="copy-button" onclick="copyToClipboard()"> 复 制 </button>
</div>

<?php
function filterProgramSources() {
  if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = $_POST['input'];
    $lines = explode("\n", $input);
    $filteredSources = array();
    $programNames = loadProgramNames();
    $filteredUrls = array(); // 用于存储已经出现过的$url

    foreach ($lines as $line) {
      $line = trim($line);
      if (!empty($line)) {
        if (strpos($line, "//") === 0 || strpos($line, "#genre#") !== false) {
          // 保留以//开头的行和带有#genre#的行
          $filteredSources[] = $line;
        } else {
          $parts = explode(",", $line);
          if (count($parts) === 2) {
            $name = trim($parts[0]);
            $url = trim($parts[1]);
            // 过滤.m3u8后面的?及其后面的内容
            $url = preg_replace('/\.m3u8\?.*/', '.m3u8', $url);
            if (filter_var($url, FILTER_VALIDATE_URL) && !in_array($url, $filteredUrls)) {
              $filteredSources[] = replaceProgramName($name, $programNames) . "," . $url;  //这个","中间不能留空格，否则出来的地址前会有空格，可能会造成播放出错。
              $filteredUrls[] = $url; // 将$url添加到已过滤的数组中
            }
          }
        }
      }
    }

    $output = implode("\n", $filteredSources);
    return $output;
  }
}

// 加载节目名称数据
function loadProgramNames() {
  $programNames = array();
  $file = fopen("转换节目名称数据.txt", "r");
  if ($file) {
    while (($line = fgets($file)) !== false) {
      $line = trim($line);
      if (!empty($line)) {
        $names = explode(",", $line);
        $mainName = trim($names[count($names) - 1]);
        foreach ($names as $name) {
          $programNames[trim($name)] = $mainName;  //统一节目名，是最每一行的最后一名称。
        }
      }
    }
    fclose($file);
  }
  return $programNames;
}

// 替换节目名称
function replaceProgramName($name, $programNames) {
  if (array_key_exists($name, $programNames)) {
    return $programNames[$name];
  }
  return $name;
}
?>
</body>
</html>
