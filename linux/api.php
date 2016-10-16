<?php

// Send POST request to remote device
function sendToDevice ($regToken) {

	$url = 'https://gcm-http.googleapis.com/gcm/send';
	$data = array('data' => 'SomeData', 'registration_ids' => $regToken);
	  
	// use key 'http' even if you send the request to https://...
	$options = array(
		'http' => array(
	    'header'  => array('Content-Type:application/json', 
                   'Authorization:key=' .
         					 'AIzaSyCP55eg2J2ZPhexPHcHyNKXpDUDTWakAvY'),
      'method'  => 'POST',
      'content' => "{\"registration_ids\":[\"$regToken\"]}" #json_encode($data),
    ),
  );	

  $context  = stream_context_create($options);
  $result = file_get_contents($url, false, $context);
  
  $json_out_path = "/tmp/json_out.json";
  $json_in_path = "/tmp/json_in.json";
  $json_in_file = fopen($json_in_path, "w") 
                  or die("could not open: $json_in_path");
  $json_out_file = fopen($json_out_path, "w");
  fwrite($json_out_file, $options['http']['content']);
  fwrite($json_in_file, $result);
  fclose($json_in_file); 
  fclose($json_out_file); 
  
}

  // Receive initial POST request from Device and deal with it
  if (!empty($_POST['id'])) {
    $regToken         = $_POST["id"];
    $regTokenFilePath = "/tmp/token.txt";
		$regTokenFile = fopen($regTokenFilePath, "w") or die("could not open: file");
		fwrite($regTokenFile, $regToken);
		fclose($regTokenFile);
    echo $regToken;
    
    sendToDevice($regToken);
 
  } else {
    echo "POST request empty";
  }
?>
