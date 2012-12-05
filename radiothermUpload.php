<?php

/**
 * OCDperture
 * quick script to take ocd's temperture
 * needs Tstat and Pachube php libs
 */

header('Content-type: text/plain');

// where am i
$root = '/home/bc/therm';

// ip address of radiotherm
$radiotherm = '10.20.30.40';

// your Pachube read/write api key
$pachube_api_key = 'put a key here';

// your pachube put url
$puturl = 'http://api.pachube.com/v2/feeds/XXXXX/datastreams/';

require_once($root . '/Tstat/Autoloader.php');
require_once($root . '/Pachube/pachube_functions.php');

Tstat_Autoloader::register();

$request = new Tstat_Client($radiotherm);
$datas = json_decode($request->info());

$pachube = new Pachube($pachube_api_key);

$environ = $pachube->environment('15729');

print("Environment:\n\n");
print_r($environ);

print("\n\n");
print("temp:\n\n");
print_r($datas->temp);

print("\n\n");
print("theat:\n\n");
print_r($datas->t_heat);

$response = $pachube->updatePachube($puturl.'temp.csv',$datas->temp);

print("\n\n");
print("temp put response:\n\n");
print_r($response);

$response = $pachube->updatePachube($puturl.'theat.csv',$datas->t_heat);

print("\n\n");
print("theat put response:\n\n");
print_r($response);

?>