
const timerDisplay = document.getElementById("timer-display");

if (window.location.search.includes("stopped_duration=")) {
    window.history.replaceState(
        {},
        document.title,
        window.location.pathname
    );
}

function formatTime(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    return [hours, minutes, seconds]
        .map(value => String(value).padStart(2, "0"))
        .join(":");
}

function updateTimer() {
    if (!timerDisplay) {
        return;
    }

    const startedAt = timerDisplay.dataset.startedAt;
    let elapsedSeconds;

    if (startedAt) {
        const startMilliseconds = new Date(startedAt).getTime();

        elapsedSeconds = Math.max(
            0,
            Math.floor((Date.now() - startMilliseconds) / 1000)
        );
    } else {
        elapsedSeconds = Number(timerDisplay.dataset.elapsed || 0);
    }

    timerDisplay.textContent = formatTime(elapsedSeconds);
}

updateTimer();
setInterval(updateTimer, 1000);
