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
  var url = 'http://'.concat(`${data.master_ip}`, ':31112/function/colorise');
  var payload = "https://i.kinja-img.com/gawker-media/image/upload/s--hs_50-b2--/c_scale,f_auto,fl_progressive,q_80,w_800/wv7kqqfxxtswupj2zhqi.jpg";
  var headers = { 'Content-Type': 'application/x-www-form-urlencoded' };
  //console.log(JSON.stringify(http.request('POST', url,payload,{ headers: headers} )));
  http.request('POST', url,payload,{ headers: headers} );
}
