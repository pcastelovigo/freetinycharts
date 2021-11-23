<?php
header("Content-Type:application/json");
require "data.php";
if ( filter_var($_GET['asset_in'], FILTER_VALIDATE_INT) === false ) { exit(); }
if ( filter_var($_GET['asset_out'], FILTER_VALIDATE_INT) === false ) { exit(); }

if(isset($_GET['asset_in']))
{
	if(isset($_GET['asset_out']))
		{
			$asset_in=$_GET['asset_in'];
			$asset_out=$_GET['asset_out'];
			$price = get_price($asset_in."_".$asset_out);
			if(empty($price)){ response(200,"Not Found",NULL); } else { response(200,"Found",$price); }
		} else { response(400,"Invalid Request",NULL); } 
} else { response(400,"Invalid Request",NULL); }



function response($status,$status_message,$data)
{
	header("HTTP/2 ".$status);
	header('Access-Control-Allow-Origin: *');	
	$response['status']=$status;
	$response['status_message']=$status_message;
	$response['data']=$data;
	
	$json_response = json_encode($response);
	echo $json_response;
}
