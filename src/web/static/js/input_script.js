document.getElementById('apiForm').addEventListener('submit', async (event) => {
event.preventDefault(); // 기본 제출 동작 방지

const form = event.target;
const clientip = "127.0.0.1:18000";
const actionUrl = form.action;
const targetUrl = document.getElementById('ip').value.trim();
if (!targetUrl) {
    alert("목표 엔드포인트 주소(ip)를 입력해 주세요.");
    return;
}

const methodSelect = document.getElementById('method');
const httpMethod = methodSelect.value.trim();

const repeatCount = parseInt(document.getElementById('repeatCount').value);
if (isNaN(repeatCount) || repeatCount < 1) {
    alert("반복 횟수는 1 이상의 숫자여야 합니다.");
    return;
}

const contentText = document.getElementById('content').value.trim();
function prepareJsonData(text) {
    if (!text) return {};
    try {
    return JSON.parse(text);
    } catch(e) {
    return { content: text };
    }
}

// jsonFile 필드에 업로드된 파일이 있는지 확인
const fileInput = document.getElementById('jsonFile');
    if (fileInput.files && fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const reader = new FileReader();
        reader.onload = async function(e) {
        const fileContent = e.target.result;
        let jsonData;
        try {
            jsonData = JSON.parse(fileContent);
        } catch (err) {
            jsonData = fileContent;
        }
        await sendRequests(actionUrl, httpMethod, clientip, targetUrl, jsonData, repeatCount);
        };
        reader.readAsText(file);
    } else {
        // 파일이 없는 경우 textarea의 내용을 사용
        const jsonData = prepareJsonData(contentText);
        await sendRequests(actionUrl, httpMethod, clientip, targetUrl, jsonData, repeatCount);
    }
});

async function sendRequests(actionUrl, httpMethod, clientip, targetUrl, jsonData, repeatCount) {
    const payload = {
        client_ip: clientip,
        target_url: targetUrl,
        method: httpMethod,
        content: jsonData,
    };

    const headers = {
        "Content-Type": "application/json"
    };

    const methodUpper = httpMethod.toUpperCase();
    let finalUrl = actionUrl;
    let fetchOptions = {
        method: methodUpper,
        headers: headers,
    };

    if (methodUpper === "GET" || methodUpper === "HEAD") {
        const queryString = new URLSearchParams(payload).toString();
        finalUrl = `${actionUrl}?${queryString}`;
        // GET/HEAD 방식은 body가 있으면 안됨. fetchOptions에는 body가 없도록 처리.
    } else {
        // GET/HEAD가 아닐 경우에만 body 추가
        fetchOptions.body = JSON.stringify(payload);
    }

    for (let i = 0; i < repeatCount; i++) {
        try {
        const response = await fetch(finalUrl, fetchOptions);

        if (!response.ok) {
            const errorData = await response.json();
            alert(`요청 실패: ${response.status} - ${JSON.stringify(errorData)}`);
            return;
        }

        const data = await response.json();
        console.log(`요청 성공: ${JSON.stringify(data)}`);
        } catch (error) {
        console.error('요청 중 오류 발생:', error);
        alert('요청 중 오류가 발생했습니다.');
        }
    }
}