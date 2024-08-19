class js_script:
    def get_js_script(self):
        js_script_old = """(function() {function captureAndSaveAudioData() {
    const captureDuration = 6 * 1000; // 20 seconds
    const allData = [];

    // 請求捕獲螢幕音頻
    navigator.mediaDevices.getDisplayMedia({ audio: true, video: true })
        .then(stream => {
            // 創建 AudioContext 和 MediaStreamAudioSourceNode
            const audioContext = new AudioContext();
            const source = audioContext.createMediaStreamSource(stream);

            // 連接到 AnalyserNode 進行音頻分析
            const analyser = audioContext.createAnalyser();
            source.connect(analyser);

            // 擷取音頻數據
            function analyze() {
                const data = new Uint8Array(analyser.frequencyBinCount);
                analyser.getByteFrequencyData(data);

                allData.push([...data]);

                if (allData.length * (1000 / 60) < captureDuration) { // Assuming 60 FPS for requestAnimationFrame
                    requestAnimationFrame(analyze);
                } else {
                    saveDataAsTxt(allData);
                }
            }

            analyze();
        })
        .catch(error => {
            console.error("Error capturing audio:", error);
        });

    // Save data as TXT
    function saveDataAsTxt(data) {
        const blob = new Blob([data.toString()], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'audio_data.txt';
        a.click();
        URL.revokeObjectURL(url);
    }
}

captureAndSaveAudioData();
})();
"""
        js_script_get_audio_data = """(function() {
    function recordAudio() {
        return new Promise((resolve, reject) => {
            const captureDuration = 10000; // 10 seconds
            const chunks = [];

            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    const recorder = new MediaRecorder(stream);
                    recorder.addEventListener('dataavailable', (event) => {
                        chunks.push(event.data);
                    });
                    recorder.start();

                    recorder.addEventListener('stop', () => {
                        const blob = new Blob(chunks, {
                            type: 'audio/webm'
                        });
                        const fileReader = new FileReader();
                        fileReader.onloadend = function(e) {
                            const arrayBuffer = e.target.result;
                            const base64 = btoa(
                                new Uint8Array(arrayBuffer)
                                .reduce((data, byte) => data + String.fromCharCode(byte), '')
                            );
                            resolve(base64);
                        };
                        fileReader.readAsArrayBuffer(blob);
                    });

                    setTimeout(() => {
                        recorder.stop();
                    }, captureDuration);
                })
                .catch(error => {
                    console.error("Error capturing audio:", error);
                    reject(error);
                });
        });
    }

    return recordAudio();
})();
"""


        return js_script_get_audio_data


