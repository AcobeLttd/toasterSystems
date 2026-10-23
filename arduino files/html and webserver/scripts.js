
var gateway = `ws://${window.location.hostname}/ws`;
var websocket;
window.addEventListener('load', onLoad);
function initWebSocket() {
    console.log('Trying to open a WebSocket connection...');
    websocket = new WebSocket(gateway);
    websocket.onopen = onOpen;
    websocket.onclose = onClose;
    websocket.onmessage = onMessage; // <-- add this line
}
function onOpen(event) {
    console.log('Connection opened');
}
function onClose(event) {
    console.log('Connection closed');
    setTimeout(initWebSocket, 2000);
}
// Function under here replaces all the placeholder values for the html code with actual values sent from the ESP32 via json.
function onMessage(event) {
    const thingThing = JSON.parse(event.data);
    var state;
    if (thingThing.state) {
        state = "ON";
    }
    else {
        state = "OFF";
    }

    document.getElementById('delay').innerText = thingThing.delay + " min";
    console.log('Data Recieved Delay: ', thingThing.delay);

    var pirState
    if (thingThing.pirState) {
        pirState = "Active";
    }
    else {
        pirState = "Innactive";
    }

    document.getElementById('pirSens').innerText = pirState;
    console.log('Data Recieved PIR: ', thingThing.pirState);

    var pirOverride
    if (thingThing.pirOverride) {
        pirOverride = "Enabled";
    }
    else {
        pirOverride = "Disabled";
    }
    document.getElementById('pirOverride').innerText = pirOverride;
    console.log('Data Recieved pirOverride: ', thingThing.pirOverride);

    document.getElementById('pirTime').innerText = thingThing.pirTime + " secs";
    console.log('Data Recieved pirTime: ', thingThing.pirTime);


    document.getElementById('state').innerText = state;
    console.log('Data Recieved Relay: ', thingThing.state);
}
function onLoad(event) {
    initWebSocket();
    initButton();
}
function initButton() {
    document.getElementById('button').addEventListener('click', toggle);
}
function toggle() {
    if (websocket && websocket.readyState === websocket.OPEN){
        websocket.send(JSON.stringify({
            command: "toggle"
        }));
        console.log('Button pressed');
    }
    else {
        console.log('Error with sending toggle.')
    }
}
