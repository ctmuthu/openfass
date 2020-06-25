import http from 'k6/http';
import { sleep } from 'k6';
const data = JSON.parse(open("../terraform/config.json"));
//var myArgs = process.argv.slice(2);
//console.log(myArgs);
export let options = {
stages: [
    { duration: "1m", target: 1},
    { duration: "2m", target: 10},
    { duration: "3m", target: 100},
    { duration: "4m", target: 200},
    { duration: "5m", target: 300},
    { duration: "6m", target: 400},
]  
//	vus: 100,
//	duration: '120s',
	//iteration: 300
};

export default function() {
//for (let i = 0; i < 10; i++) {
  var url = 'http://'.concat(`${data.master_ip}`, ':31112/function/sentimentanalysis');
  var payload = "Personally I like functions to do one thing and only one thing well, it makes them more readable.";
  http.post(url,payload);
//}
}
