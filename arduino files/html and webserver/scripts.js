
var gateway = `ws://${window.location.hostname}/ws`;
var websocket;

function makeTerminal(elementID, maxLines = 200) {
    return {
        element: null,
        maxLines,
        lines: ["Waiting for ESP32..."],
        updatePending: false,
        lastMessage: null,

        init() {
            this.element = document.getElementById(elementID);
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
    }
};

const terminalThing = makeTerminal("terminal");
const matrixStatus = makeTerminal("matrixStatus");
const rpiStatus = makeTerminal("rpiDebug");

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
    matrixStatus.init();
    rpiStatus.init();
}
function initButtons() {
    document.getElementById('button').addEventListener('click', playBadApple);
    document.getElementById('button1').addEventListener('click', stopMatrix);
    document.getElementById('shutdown').addEventListener('click', shutdown);
    document.getElementById('displayImage').addEventListener('click', displayImage);
}
function initTextInputs() {
    document.getElementById('progrenCLI').addEventListener('submit', sendSerial);
    document.getElementById('videoPath').value = "./test-media/theAppleThatIsBad.mp4";
    document.getElementById('imagePath').value = "./test-media/actualPNGtest.png";
}

function sendSerial(event) {
    event.preventDefault();

    const input = document.getElementById('commandLine');
    const command = input.value.trim();

    sendCommands(command);
    input.value = "";
}

// Function under here replaces all the placeholder values for the html code with actual values sent from the ESP32 via json.
function onMessage(event) {
    const thingThing = JSON.parse(event.data);

    terminalThing.addMessage(thingThing.debug);
    matrixStatus.addMessage(thingThing.matrix);
    rpiStatus.addMessage(thingThing.rpiDebug);

    document.getElementById('lastMessage').innerText = thingThing.lastMessage + " secs";
    console.log('Data Recieved lastMessage: ', thingThing.lastMessage);

    document.getElementById('delay').innerText = thingThing.delay + " min";
    console.log('Data Recieved Delay: ', thingThing.delay);

    var piConnect;
    if (thingThing.piConnect) {
        piConnect = "Connected";
    }
    else {
        piConnect = "Disconnected";
    }
    document.getElementById('piConnect').innerText = piConnect;
    console.log('Data Recieved Relay: ', thingThing.piConnect);

    var pirState
    if (thingThing.pirState) {
        pirState = "Active";
    }
    else {
        pirState = "Innactive";
    }

    document.getElementById('pirSens').innerText = pirState;
    console.log('Data Recieved PIR: ', thingThing.pirState);

}

function getPathForVideo() {
    const input = document.getElementById('videoPath');
    const command = input.value.trim();
    return command;
}

function getPathForImage() {
    const input = document.getElementById('imagePath');
    const command = input.value.trim();
    return command;
}

function displayImage() {
    const pathToVideo = getPathForImage();
    const command = `matrix|display|${pathToVideo}`;
    sendCommands(command);
}



function playBadApple() {
    const pathToVideo = getPathForVideo();
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
