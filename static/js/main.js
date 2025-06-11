var socket = io();
var beepAudio = document.getElementById('beep-sound');

// Definición de trazos para los gráficos en tiempo real
function createTrace(name) {
    return {
        x: [],
        y: [],
        mode: 'lines',
        name: name
    };
}

var trace_esfuerzo = createTrace('Tiempo Real');
var trace_q_p = createTrace('Tiempo Real');
var trace_pressure = createTrace('Tiempo Real');
var trace_qp = createTrace('Tiempo Real');

// Definición de trazos para los datos estáticos
var static_traces = {
    esfuerzo: [],
    q_p: [],
    pressure: [],
    qp: []
};

var data_esfuerzo = [trace_esfuerzo];
var data_q_p = [trace_q_p];
var data_pressure = [trace_pressure];
var data_qp = [trace_qp];

// Configuraciones de diseño para los gráficos
function createLayout(xTitle, yTitle) {
    return {
        xaxis: { title: xTitle },
        yaxis: { title: yTitle },
        legend: {
            yanchor: 'middle',
            y: 0.5,
            xanchor: 'right',
            x: 1.1,
            bgcolor: 'rgba(0, 0, 0, 0)'
        },
        margin: {
            l: 60,  // margen izquierdo
            r: 50,  // margen derecho
            t: 30,  // margen superior
            b: 60   // margen inferior
        }
    };
}

var layout_esfuerzo = createLayout('Desplazamiento', 'Esfuerzo desviador');
var layout_q_p = createLayout('p', "q'");
var layout_pressure = createLayout('Desplazamiento', 'Presión de poros');
var layout_qp = createLayout('Desplazamiento', "q'/p");

// Inicializa los gráficos con Plotly
function initializeGraphs() {
    Plotly.newPlot('graph_esfuerzo', data_esfuerzo, layout_esfuerzo);
    Plotly.newPlot('graph_q_p', data_q_p, layout_q_p);
    Plotly.newPlot('graph_pressure', data_pressure, layout_pressure);
    Plotly.newPlot('graph_qp', data_qp, layout_qp);
}
initializeGraphs();

// Event listeners para los botones de selección de archivos
document.getElementById('select-file-button').addEventListener('click', function() {
    document.getElementById('file-input').click();
});

document.getElementById('file-input').addEventListener('change', function(event) {
    var file = event.target.files[0];
    if (file) {
        console.log(`Archivo seleccionado: ${file.name}`);
        document.getElementById('file-params').style.display = 'block';
        document.getElementById('submit-params').onclick = function() {
            var params = {
                name: file.name,
                sigma3: parseFloat(document.getElementById('sigma3').value),
                H0: parseFloat(document.getElementById('H0').value),
                D0: parseFloat(document.getElementById('D0').value),
                DH0: parseFloat(document.getElementById('DH0').value),
                DV0: parseFloat(document.getElementById('DV0').value),
                PP0: parseFloat(document.getElementById('PP0').value)
            };
            socket.emit('selected_file', params);
        };
    }
});

document.getElementById('select-static-files-button').addEventListener('click', function() {
    document.getElementById('static-file-input').click();
});

document.getElementById('static-file-input').addEventListener('change', function(event) {
    var files = event.target.files;
    var file_paths = [];
    var params_container = document.getElementById('static-file-params-container');
    params_container.innerHTML = '';

    for (var i = 0; i < files.length; i++) {
        file_paths.push(files[i].name);
        params_container.appendChild(createStaticFileParamsForm(files[i], i));
    }

    if (file_paths.length > 0) {
        console.log(`Archivos estáticos seleccionados: ${file_paths}`);
        document.getElementById('static-file-params').style.display = 'block';
        document.getElementById('submit-static-params').onclick = function() {
            var static_params = [];
            for (var i = 0; i < files.length; i++) {
                static_params.push(getStaticFileParams(i));
            }
            socket.emit('load_static_files', { file_paths: file_paths, static_params: static_params });
        };
    }
});

function createStaticFileParamsForm(file, index) {
    var div = document.createElement('div');
    div.innerHTML = `
        <h4>Parámetros para ${file.name}</h4>
        <label for="sigma3_${index}">Sigma3:</label>
        <input type="number" id="sigma3_${index}" name="sigma3_${index}" step="0.01" value="0"><br>
        <label for="H0_${index}">H0:</label>
        <input type="number" id="H0_${index}" name="H0_${index}" step="0.01" value="20"><br>
        <label for="D0_${index}">D0:</label>
        <input type="number" id="D0_${index}" name="D0_${index}" step="0.01" value="10"><br>
        <label for="DH0_${index}">DH0:</label>
        <input type="number" id="DH0_${index}" name="DH0_${index}" step="0.01" value="0"><br>
        <label for="DV0_${index}">DV0:</label>
        <input type="number" id="DV0_${index}" name="DV0_${index}" step="0.01" value="0"><br>
        <label for="PP0_${index}">PP0:</label>
        <input type="number" id="PP0_${index}" name="PP0_${index}" step="0.01" value="0"><br>
    `;
    return div;
}

function getStaticFileParams(index) {
    var file = document.getElementById('static-file-input').files[index];
    return {
        name: file.name,
        sigma3: parseFloat(document.getElementById(`sigma3_${index}`).value),
        H0: parseFloat(document.getElementById(`H0_${index}`).value),
        D0: parseFloat(document.getElementById(`D0_${index}`).value),
        DH0: parseFloat(document.getElementById(`DH0_${index}`).value),
        DV0: parseFloat(document.getElementById(`DV0_${index}`).value),
        PP0: parseFloat(document.getElementById(`PP0_${index}`).value)
    };
}

socket.on('new_data', function(data) {
    console.log('Datos recibidos:', data);
    updateMonitoringPanel(data);
    updateRealTimeData(data);
    redrawGraphs();
});

function updateMonitoringPanel(data) {
    document.getElementById('displacement').innerText = data.displacement.toFixed(3);
    document.getElementById('force').innerText = data.force.toFixed(2);
    document.getElementById('volume').innerText = data.volume.toFixed(2);
    document.getElementById('pressure').innerText = data.pressure.toFixed(2);
}

function updateRealTimeData(data) {
    trace_esfuerzo.x.push(data.displacement);
    trace_esfuerzo.y.push(data.esf_desv);
    trace_q_p.x.push(data.p);
    trace_q_p.y.push(data.q);
    trace_pressure.x.push(data.displacement);
    trace_pressure.y.push(data.pressure);
    trace_qp.x.push(data.displacement);
    trace_qp.y.push(data.qp);
}

function redrawGraphs() {
    Plotly.redraw('graph_esfuerzo');
    Plotly.redraw('graph_q_p');
    Plotly.redraw('graph_pressure');
    Plotly.redraw('graph_qp');
}

socket.on('static_data', function(static_data) {
    console.log('Datos estáticos recibidos:', static_data);
    resetStaticTraces();
    static_data.forEach(function(file_data) {
        addStaticTraces(file_data);
    });
    plotStaticData();
    if (beepAudio) {
        beepAudio.currentTime = 0;
        beepAudio.play();
    }
});

function resetStaticTraces() {
    static_traces.esfuerzo = [];
    static_traces.q_p = [];
    static_traces.pressure = [];
    static_traces.qp = [];
}

function addStaticTraces(file_data) {
    var short_name = getShortFileName(file_data.file_path);

    static_traces.esfuerzo.push(createStaticTrace(file_data.data, 'displacement', 'esf_desv', `${short_name} kPa`));
    static_traces.q_p.push(createStaticTrace(file_data.data, 'p', 'q', `${short_name} kPa`));
    static_traces.pressure.push(createStaticTrace(file_data.data, 'displacement', 'pressure', `${short_name} kPa`));
    static_traces.qp.push(createStaticTrace(file_data.data, 'displacement', 'qp', `${short_name} kPa`));
}

function createStaticTrace(data, xKey, yKey, name) {
    return {
        x: data.map(d => d[xKey]),
        y: data.map(d => d[yKey]),
        mode: 'lines',
        name: name
    };
}

function getShortFileName(file_path) {
    var match = file_path.match(/_(\d+)KPA/);
    return match ? match[1] : file_path;
}

function plotStaticData() {
    Plotly.newPlot('graph_esfuerzo', [trace_esfuerzo].concat(static_traces.esfuerzo), layout_esfuerzo);
    Plotly.newPlot('graph_q_p', [trace_q_p].concat(static_traces.q_p), layout_q_p);
    Plotly.newPlot('graph_pressure', [trace_pressure].concat(static_traces.pressure), layout_pressure);
    Plotly.newPlot('graph_qp', [trace_qp].concat(static_traces.qp), layout_qp);
}

function updateDate() {
    var currentDate = new Date().toLocaleDateString();
    document.getElementById('current-date').innerText = currentDate;
}

updateDate();
