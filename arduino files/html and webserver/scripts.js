
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
    addTerminalMessage(event.data);
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
    initButtons();
    initTextInputs();
}
function initButtons() {
    document.getElementById('button').addEventListener('click', playBadApple);
    document.getElementById('button1').addEventListener('click', stopMatrix);
}
function initTextInputs() {
    document.getElementById('commandLine').addEventListener('submit', sendSerial)
}

function initTerminal() {
    const terminal = document.getElementById("terminal");

    terminal.textContent = "random shit"
}

function sendSerial(event) {
    event.preventDefault()
}

function addTerminalMessage(message) {
    lines.push(String(message));

    if (lines.length > MAX_LINES) {
        lines.splice(0, lines.length - MAX_LINES);
    }

    if (!updatePending) {
        updatePending = true;

        requestAnimationFrame(() => {
            terminal.textContent = lines.join("\n");
            terminal.scrollTop = terminal.scrollHeight;
            updatePending = false;
        });
    }
}

function playBadApple() {
    const pathToVideo = "./test-media/theAppleThatIsBad.mp4"
    const command = `matrix|play|${pathToVideo}`;
    sendCommands(command);
}

function stopMatrix() {
    const command = "matrix|stop";
    sendCommands(command);
}

function sendCommands(command) {
    console.log(`Trying to send: "${command}"`);
    if (websocket && websocket.readyState === websocket.OPEN) {
        websocket.send(JSON.stringify({
            command: command
        }));
        console.log(`command sent: ${command}`);
    }
    else {
        console.log('Error with sending command. Websocket most likely not connected.');
    }
}
