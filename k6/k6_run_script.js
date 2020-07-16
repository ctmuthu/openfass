import { check, sleep } from 'k6';
import http from 'k6/http';
const data = JSON.parse(open("../terraform/config.json"));

export default function() {
    var url = 'http://'.concat(`${__ENV.MASTER_IP}`, ':31112/function/',`${__ENV.FUNCTION}`);
    var payload = `${__ENV.PAYLOAD}`;
    var r = http.post(url,payload);
    check(r, {
        'status is 200': r => r.status === 200,
    });
}