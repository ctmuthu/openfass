import http from 'k6/http';
import { sleep } from 'k6';
const data = JSON.parse(open("../terraform/config.json"));
/*export let options = {
  stages: [
    { duration: "1m", target: 1},
    { duration: "2m", target: 10},
    { duration: "3m", target: 100},
    { duration: "4m", target: 100},
    { duration: "5m", target: 100},
    { duration: "6m", target: 100},
]
  };*/

export default function() {
  var url = 'http://'.concat(`${data.master_ip}`, ':31112/function/figlet');
  var payload = "This is a text that I think will increase the memory usage. But please increase the memory usage at any cost. I have very little time for the meeting. Please do it. Make sure the memory is used. On the other hand, we denounce with righteous indignation and dislike men who are so beguiled and demoralized by the charms of pleasure of the moment, so blinded by desire, that they cannot foresee the pain and trouble that are bound to ensue; and equal blame belongs to those who fail in their duty through weakness of will, which is the same as saying through shrinking from toil and pain. These cases are perfectly simple and easy to distinguish. In a free hour, when our power of choice is untrammelled and when nothing prevents our being able to do what we like best, every pleasure is to be welcomed and every pain avoided. But in certain circumstances and owing to the claims of duty or the obligations of business it will frequently occur that pleasures have to be repudiated and annoyances accepted. The wise man therefore always holds in these matters to this principle of selection: he rejects pleasures to secure other greater pleasures, or else he endures pains to avoid worse pains.";
  http.post(url,payload);
}

