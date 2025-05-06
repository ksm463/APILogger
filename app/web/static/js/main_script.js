// JSON 문자열 포맷 함수
function formatContent(content) {
    try {
        const obj = JSON.parse(content);
        return JSON.stringify(obj, null, 2);
    } catch (e) {
        return content;
    }
}

// 클릭 시 팝업 토글 이벤트 추가
function addClickToggle(container, popup) {
    container.addEventListener('click', function(event) {
        event.stopPropagation();
        popup.classList.toggle('active');
    });
}

// 문서 클릭 시 모든 활성 팝업 닫기
document.addEventListener('click', function() {
    document.querySelectorAll('.popup-tooltip.active').forEach(popup => {
        popup.classList.remove('active');
    });
});

// 셀 생성 함수 (짧은 텍스트와 팝업 포함)
function createTooltipCell(content, isTimeColumn = false) {
    const td = document.createElement('td');
    if (isTimeColumn) {
        td.className = 'time-column';
    }
    const container = document.createElement('span');
    container.className = 'tooltip-container';
    container.textContent = content;

    const popup = document.createElement('div');
    popup.className = 'popup-tooltip';

    const formatted = formatContent(content);
    if (formatted !== content) {
        const pre = document.createElement('pre');
        pre.textContent = formatted;
        popup.appendChild(pre);
    } else {
        popup.textContent = content;
    }

    container.appendChild(popup);
    td.appendChild(container);

    addClickToggle(container, popup);

    return td;
}

// 데이터 배열을 기반으로 테이블 행을 생성 (컬럼 설정 배열 사용하여 중복 코드 제거)
function loadTableData(dataArray) {
    const tbody = document.querySelector('#apiTable tbody');
    tbody.innerHTML = '';

    const columns = [
        { key: 'id', type: 'text' },
        { key: 'method', type: 'text' },
        { key: 'user_agent', type: 'tooltip' },
        { key: 'client_ip', type: 'tooltip' },
        { key: 'request', type: 'tooltip' },
        { key: 'response', type: 'tooltip' },
        { key: 'time', type: 'tooltip', isTime: true },
        { key: 'request_status', type: 'tooltip' },
        { key: 'response_code', type: 'tooltip' },
        { key: 'error_message', type: 'tooltip' }
    ];

    dataArray.forEach(row => {
        const tr = document.createElement('tr');
        columns.forEach(col => {
            let cell;
            if (col.type === 'text') {
                cell = document.createElement('td');
                cell.textContent = row[col.key];
            } else {
                cell = createTooltipCell(row[col.key], col.isTime);
            }
            tr.appendChild(cell);
        });
        tbody.appendChild(tr);
    });
}

// "최근 조회" 버튼 클릭 시 로그 데이터 가져오기
document.getElementById('recentBtn').addEventListener('click', async () => {
    try {
        const response = await fetch('/read');
        if (!response.ok) throw new Error('네트워크 응답 에러');
        const data = await response.json();
        loadTableData(data);
    } catch (error) {
        console.error('데이터 로드 에러:', error);
    }
});

// "날짜별 조회" 버튼 클릭 시 날짜 선택 폼 표시
document.getElementById('dateBtn').addEventListener('click', () => {
    const dateForm = document.getElementById('dateForm');
    dateForm.style.display = 'block';
});

// "취소" 버튼 클릭 시 날짜 선택 폼 숨기기
document.getElementById('cancelDateBtn').addEventListener('click', () => {
    const dateForm = document.getElementById('dateForm');
    dateForm.style.display = 'none';
});

// "조회" 버튼 클릭 시 날짜별 데이터 조회
document.getElementById('submitDateBtn').addEventListener('click', async () => {
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;

    if (!startDate || !endDate) {
        alert("시작일과 종료일을 모두 선택해주세요.");
        return;
    }

    try {
        const response = await fetch(`/read/date?start_date=${startDate}&end_date=${endDate}`);
        if (!response.ok) throw new Error('네트워크 응답 에러');
        const data = await response.json();
        loadTableData(data);
    } catch (error) {
        console.error('데이터 로드 에러:', error);
    } finally {
        // 조회 후 날짜 입력 폼 숨기기
        document.getElementById('dateForm').style.display = 'none';
    }
});
