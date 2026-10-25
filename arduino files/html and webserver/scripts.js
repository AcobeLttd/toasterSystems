
var gateway = `ws://${window.location.hostname}/ws`;
var websocket;

const terminalThing = {
    element: null,
    maxLines: 200,
    lines: ["Waiting for ESP32..."],
    updatePending: false,
    lastMessage: null,

    init() {
        this.element = document.getElementById("terminal");
    },

    addMessage(message) {
        message = String(message);

        if (message === this.lastMessage) {
            return;
        }

        this.lastMessage = message;
        this.lines.push(String(message));

        if (this.lines.length > this.maxLines) {
            this.lines.splice(0, this.lines.length - this.maxLines);
        }

        if (!this.updatePending) {
            this.updatePending = true;

            requestAnimationFrame(() => {
                this.element.textContent = this.lines.join("\n");
                this.element.scrollTop = this.element.scrollHeight;
                this.updatePending = false;
            });
        }
    }
};

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

function onLoad(event) {
    initWebSocket();
    initButtons();
    initTextInputs();
    terminalThing.init();
}
function initButtons() {
    document.getElementById('button').addEventListener('click', playBadApple);
    document.getElementById('button1').addEventListener('click', stopMatrix);
    document.getElementById('shutdown').addEventListener('click', shutdown);
}
function initTextInputs() {
    document.getElementById('commandLine').addEventListener('submit', sendSerial)
}

function sendSerial(event) {
    event.preventDefault()
}

// Function under here replaces all the placeholder values for the html code with actual values sent from the ESP32 via json.
function onMessage(event) {
    const thingThing = JSON.parse(event.data);

    terminalThing.addMessage(thingThing.debug);

    var piConnect;
    if (thingThing.piConnect) {
        piConnect = "Connected";
    }
    else {
        piConnect = "Disconnected";
    }
    document.getElementById('piConnect').innerText = piConnect;
    console.log('Data Recieved Relay: ', thingThing.piConnect);

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

    document.getElementById('lastMessage').innerText = thingThing.lastMessage + " secs";
    console.log('Data Recieved lastMessage: ', thingThing.lastMessage);
    
}

function playBadApple() {
    const pathToVideo = "./test-media/theAppleThatIsBad.mp4";
    const command = `matrix|play|${pathToVideo}`;
    sendCommands(command);
}

function stopMatrix() {
    const command = "matrix|stop";
    sendCommands(command);
}

function shutdown() {
    const command = "shutdown";
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
