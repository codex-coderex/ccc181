const joinForm = document.getElementById("join-form");
if (joinForm) {
  joinForm.addEventListener("submit", () => {
    const button = joinForm.querySelector("button[type=submit]");
    button.disabled = true;
    button.textContent = "Getting your ticket…";
  });
}

document.querySelectorAll("form[data-confirm]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    if (!confirm(form.dataset.confirm)) event.preventDefault();
  });
});

// Staff Dashboard live updates
const staffQueueState = document.getElementById("staff-queue-state");

if (staffQueueState) {
  // Update waiting times every second
  function updateStaffWaitingTimes() {
    document.querySelectorAll(".live-wait-time").forEach((element) => {
      const joinedAt = new Date(element.dataset.joinedAt);

      const totalSeconds = Math.max(
        0,
        Math.floor((Date.now() - joinedAt.getTime()) / 1000)
      );

      const minutes = Math.floor(totalSeconds / 60);
      const seconds = totalSeconds % 60;

      element.textContent = minutes === 0
        ? `${seconds} seconds`
        : `${minutes} min ${seconds} sec`;
    });
  }

  updateStaffWaitingTimes();
  setInterval(updateStaffWaitingTimes, 1000);

  // Check for queue changes every 10 seconds
  async function checkStaffQueue() {
    if (document.hidden) return;

    try {
      const response = await fetch(
        "/staff/queue-state.json" + window.location.search,
        { cache: "no-store" }
      );

      if (!response.ok) return;

      const data = await response.json();

      const previous = JSON.parse(staffQueueState.dataset.state);
      const current = [data.waiting_ids, data.serving_id];

      if (JSON.stringify(previous) !== JSON.stringify(current)) {
        window.location.reload();
      }
    } catch (error) {
      console.error("Could not refresh staff queue:", error);
    }
  }

  setInterval(checkStaffQueue, 10000);
}