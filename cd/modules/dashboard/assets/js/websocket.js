function getCookie(cookie) {
    const name = cookie + "=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(";");
    for (const element of ca) {
        let c = element;
        while (c.charAt(0) === " ") {
            c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function formatMilliseconds(milliseconds) {

    let seconds = Math.floor(milliseconds / 1000)
    let minutes = Math.floor(seconds / 60)
    let hours = Math.floor(minutes / 60)
    let days = Math.floor(hours / 24)

    seconds = seconds % 60
    minutes = minutes % 60
    hours = hours % 24

    return (
        (days !== 0 ? (("00:" + days).slice(-2) + ":") : "") +
        (hours !== 0 ? (("00:" + hours).slice(-2) + ":") : "") +
        ("00" + minutes).slice(-2) + ":" +
        ("00" + seconds).slice(-2))
}

////////////////
// Websocket //
//////////////

const websocket = new WebSocket(
    `ws${window.location.protocol === "http:" ? "" : "s"}://${window.location.host}/websocket`
);

websocket.onmessage = function (event) {

    const {op, data} = JSON.parse(event.data)

    switch (op) {
        case 0:
            sendIdentify()
            break
        case 2:
            handleEvent(data)
            break;
    }
}


/////////////////////////
// Websocket handlers //
///////////////////////

function sendIdentify() {
    websocket.send(JSON.stringify({
        op: 1,
        data: {
            guild_id: window.location.pathname.replace("/servers/", ""),
            identifier: getCookie("identifier"),
        }
    }))
}

function handleEvent(data) {
    switch (data.type) {
        case "IDENTIFIED":
            handleIdentified(data)
            break
        case "PLAYER_UPDATE":
            handlePlayerUpdateEvent(data)
            break
        case "POSITION_UPDATE":
            handlePositionUpdateEvent(data)
            break
    }
}


/////////////////////
// Event handlers //
////////////////////

function handleIdentified(data) {
    set_current_track(data?.track ?? null)
    set_position(data)
}

function handlePlayerUpdateEvent(data) {
    set_current_track(data?.track ?? null)
}

function handlePositionUpdateEvent(data) {
    set_position(data)
}


////////////////
// UI changes //
////////////////

function set_current_track(data) {

    let artwork = data?.artwork_url ?? "https://dummyimage.com/1280x720/000/fff.png&text=no%20track"
    let title = data?.title ?? "No track playing"
    let url = data?.uri ?? "#"
    let author = data?.author !== null ? `by ${data.author}` : ""

    document.getElementById("trackThumbnail").src = artwork
    document.getElementById("trackTitle").innerHTML = title
    document.getElementById("trackTitle").href = url
    document.getElementById("trackAuthor").innerHTML = author
}

function set_position(data) {

    if (data?.position !== null) {
        document.getElementById("trackPosition").innerHTML = `Position: ${formatMilliseconds(data.position)}`
        document.getElementById("trackProgress").style.width = `${(100 / (data.track.length / 1000)) * (data.position / 1000)}%`
        document.getElementById("trackProgressBar").classList.remove("invisible")
    }
    else {
        document.getElementById("trackPosition").innerHTML = ""
        document.getElementById("trackProgress").style.width = "0%"
        document.getElementById("trackProgressBar").classList.add("invisible")
    }
}
