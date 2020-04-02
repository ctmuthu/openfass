import http from 'k6/http';
import { sleep } from 'k6';
const data = JSON.parse(open("../terraform/config.json"));
export let options = {
    vus: 500,
    duration: '30s',
  };

export default function() {
  http.get('http://'.concat(`${data.master_ip}`, ':31112/function/figlet'));
  sleep(1);
}