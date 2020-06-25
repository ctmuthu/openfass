import http from 'k6/http';
import { sleep } from 'k6';
const data = JSON.parse(open("../terraform/config.json"));
export let options = {
	stages: [
    { duration: "1m", target: 1, rps: 1},
    { duration: "2m", target: 10, rps: 10},
    { duration: "3m", target: 100},
    { duration: "4m", target: 200},
    { duration: "5m", target: 300},
    { duration: "6m", target: 400},
]
  };

export default function() {
  var url = 'http://'.concat(`${data.master_ip}`, ':31112/function/pigo-face-detector');
  var payload = "https://upload.wikimedia.org/wikipedia/commons/2/2b/2017_class_of_NASA_astronauts_in_September_2019.jpg";
  var headers = { 'Content-Type': 'application/x-www-form-urlencoded' };
  //console.log(JSON.stringify(http.request('POST', url,payload,{ headers: headers} )));
  http.request('POST', url,payload,{ headers: headers} );
}
