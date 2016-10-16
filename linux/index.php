<html>
  <head>
    <title>Landing Page</title>
  </head>
  <body>
  <p>Got app token:
<?php
  if (!empty($_POST['id'])) {
    $mToken         = $_POST["id"];
    $mTokenFilePath = "/tmp/token.txt";
    echo $mToken;
		$mTokenFile = fopen($mTokenFilePath, "w") or die("could not open: file");
		fwrite($mTokenFile, $mToken);
		fclose($mTokenFile);
  } else {
    echo "POST request empty";
  }
?>
  </p>
  </body>
</html>
