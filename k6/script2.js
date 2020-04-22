import http from 'k6/http';
import { sleep } from 'k6';
const data = JSON.parse(open("../terraform/config.json"));
export let options = {
    stages: [
        { duration: "10s", target: 1, rps: 0.0167 },
        { duration: "20s", target: 10, rps: 0.0167 },
        { duration: "30s", target: 100, rps: 0.0167 },
    ]
  };

export default function() {
  var url = 'http://'.concat(`${data.master_ip}`, ':31112/function/classify');
  var payload = "Müller";
  http.post(url,payload);
}