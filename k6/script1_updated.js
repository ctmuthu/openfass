import http from 'k6/http';
import { sleep, check } from 'k6';
const data = JSON.parse(open("../terraform/config.json"));
/*export let options = {
  vus: 5,
  duration: '10s'
};*/


export default function() {
  //const before = new Date().getTime();
  //const T = 120;
	
  var url = 'http://'.concat(`${data.master_ip}`, ':31112/function/sentimentanalysis');
  var payload = "Personally I like functions to do one thing and only one thing well, it makes them more readable.";
  http.post(url,payload);

  /*const after = new Date().getTime();
  const diff = (after - before) / 1000;
  const remainder = T - diff;
  check(remainder, { 'reached request rate': remainder > 0 });
  if (remainder > 0) {
    sleep(remainder);
  } else {
    console.warn(
      `Timer exhausted! The execution time of the test took longer than ${T} seconds`
    );
  }*/
}
