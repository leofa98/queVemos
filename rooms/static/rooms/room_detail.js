"use strict";

const d = document;
const csrfToken = d.querySelector("meta[name='csrf-token']").content;
d.addEventListener("DOMContentLoaded", () => {
  const copyCodeBtn = d.getElementById("copy-code");
  const invitationCodeField = d.getElementById("invitation-code");
  const exitConfirm = d.getElementById("exit-confirm");
  const candidateList = d.getElementById("candidate-list");
  const proposeTitleElement = d.getElementById("proposeTitleModal");
  const proposeTitlebtn = d.getElementById("propose-title-btn");
  const proposeTitleModal = new bootstrap.Modal(proposeTitleElement);
  const proposeTitleSelect = d.getElementById("propose-title-select");
  const invitationCode = d.querySelector(".room-detail").dataset.roomCode;
  const voteBtns = d.querySelectorAll(".vote-btn");
  const spinner = d.getElementById("spinner");
  const debouncedList = debounce(async () => {
    try {
      let candidates = await candidateListFetch(invitationCode);
      if (candidates) {
        candidateList.innerHTML = candidates;
      }
    } finally {
      spinner.classList.add("d-none");
      candidateList.classList.remove("d-none");
    }
  }, 1000);
  copyCodeBtn.addEventListener("click", async () => {
    await navigator.clipboard.writeText(invitationCodeField.textContent.trim());
    copyCodeBtn.textContent = "Copiado ✔";
    setTimeout(() => {
      copyCodeBtn.textContent = "Copiar";
    }, 3000);
  });
  candidateList.addEventListener("click", async (e) => {
    if (e.target.closest(".vote-btn")) {
      let position = e.target.closest(".vote-btn").dataset.votePosition;
      let candidateId = e.target.closest(".vote-btn").dataset.candidateId;
      await voteCandidate(invitationCode, candidateId, position);
      let candidates = await candidateListFetch(invitationCode);
      if (candidates) {
        candidateList.innerHTML = candidates;
      }
    }
  });
  exitConfirm.addEventListener("click", async (e) => {
    let roomCode = e.target.dataset.roomCode;
    let response = await roomExit(roomCode);
    if (response) {
      showToast("success", response.message);
      setTimeout(() => {
        window.location.href = "/rooms";
      }, 1000);
    }
  });
  proposeTitlebtn.addEventListener("click", async () => {
    let titleId = proposeTitleSelect.value;
    let response = await proposeTitle(titleId, invitationCode);
    if (response) {
      showToast("success", response.message);
      spinner.classList.remove("d-none");
      candidateList.classList.add("d-none");
      debouncedList();
      proposeTitleModal.hide();
      proposeTitleSelect.value = "";
    }
  });
});

async function roomExit(invitation_code) {
  let data = await apiFetch("/rooms/exit", {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      invitation_code,
    }),
  });

  return data;
}

async function proposeTitle(title_id, invitation_code) {
  let data = await apiFetch(`/rooms/${invitation_code}/candidates/new`, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      title_id,
    }),
  });
  return data;
}

async function voteCandidate(invitation_code, candidate_id, position) {
  let data = await apiFetch(
    `/rooms/${invitation_code}/candidates/${candidate_id}/vote`,
    {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        position,
      }),
    },
  );
  return data;
}

async function candidateListFetch(invitation_code) {
  let data = await apiFetchText(`/rooms/${invitation_code}/candidates`, {
    method: "GET",
  });

  return data;
}
