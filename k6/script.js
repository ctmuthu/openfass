import http from 'k6/http';
import { sleep } from 'k6';
const data = JSON.parse(open("../terraform/config.json"));
export let options = {
  stages: [
    { duration: "1m", target: 1, rps: 1 },
    { duration: "1m", target: 200, rps: 1 },
    { duration: "1m", target: 500, rps: 1 },
    { duration: "1m", target: 1000, rps: 1 },
    { duration: "1m", target: 500, rps: 1 },
    { duration: "1m", target: 200, rps: 1 },
    { duration: "1m", target: 1, rps: 1 },
]
  };

export default function() {
  http.get('http://'.concat(`${data.master_ip}`, ':31112/function/figlet'));
  sleep(2000);
}