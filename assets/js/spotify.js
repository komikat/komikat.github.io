var playing = false;
var song = null;
var artist = null;
var url = null;


//const updateSong = async () => {
//    axios.get("https://spotify-now-playing-1.akshitkumar3110.repl.co/now").then(
//        response => {
//            console.log(response.data.playing);
//            if (response.data.playing) {
//                playing = true;
//                song = response.data.song
//                artist = response.data.artist
//                url = response.data.url
//
//
//
//                document.getElementById('off').innerText = ""
//                document.getElementById('song').innerText = song;
//               document.getElementById('song').href = url;
//               document.getElementById('artist').innerText = " – " + artist;
// 
//             } else {
//                 document.getElementById('off').innerText = "Offline";
//                 document.getElementById('song').innerText = "";
//                 document.getElementById('artist').innerText = "";
//             }
//         }
//     ).catch((err) => {
//         console.log("error: ", err);
//         document.getElementById('off').innerText = "Offline";
//         document.getElementById('song').innerText = "";
//         document.getElementById('artist').innerText = "";
//     })
// }
//updateSong()
//setInterval(updateSong, 10000);

document.getElementById('off').innerText = "Offline";
document.getElementById('song').innerText = "";
document.getElementById('artist').innerText = "";
