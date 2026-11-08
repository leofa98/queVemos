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
  const suggestCandidatesBtn = d.getElementById("btn-suggest-candidates");
  copyCodeBtn.addEventListener("click", async () => {
    await navigator.clipboard.writeText(invitationCodeField.textContent.trim());
    copyCodeBtn.textContent = "Copiado ✔";
    setTimeout(() => {
      copyCodeBtn.textContent = "Copiar";
    }, 3000);
  });
  candidateList.addEventListener("click", async (e) => {
    if (e.target.closest(".vote-btn")) {
      let voteBtn = e.target.closest(".vote-btn");
      voteBtn.disabled = true;
      let position = voteBtn.dataset.votePosition;
      let candidateId = voteBtn.dataset.candidateId;
      await voteCandidate(invitationCode, candidateId, position);
      await loadCandidates();
    }

    if (e.target.closest("#close-room-btn")) {
      let closeRoomModalElement = d.getElementById("closeRoomModal");
      let closeRoomModal = bootstrap.Modal.getOrCreateInstance(
        closeRoomModalElement,
      );
      closeRoomModal.show();
      let dataLeader = d.querySelector("[data-leader]");
      if (dataLeader) {
        let candidateSelect = d.getElementById("candidate-select");
        candidateSelect.value = dataLeader.dataset.candidateId;
      }
    }
    if (e.target.closest("#confirm-close-room-btn")) {
      let candidateSelect = d.getElementById("candidate-select");
      let candidateId = candidateSelect.value;
      let closed = await closeRoom(invitationCode, candidateId);
      if (closed) {
        location.reload();
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
      loadCandidates();
      proposeTitleModal.hide();
      proposeTitleSelect.value = "";
    }
  });

  suggestCandidatesBtn.addEventListener("click", async () => {
    let response;
    try {
      suggestCandidatesBtn.disabled = true;
      response = await suggestCandidates(invitationCode);
    } finally {
      if (response) {
        showToast("success", response.message);
        loadCandidates();
      }
      suggestCandidatesBtn.disabled = false;
    }
  });

  async function loadCandidates() {
    let candidates = await apiFetchText(`/rooms/${invitationCode}/candidates`);
    if (candidates) {
      candidateList.innerHTML = candidates;
    }
  }
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

async function closeRoom(invitationCode, candidateId) {
  let data = await apiFetch(`/rooms/close`, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      invitation_code: invitationCode,
      candidate_id: candidateId,
    }),
  });

  return data;
}

async function suggestCandidates(invitationCode) {
  let data = await apiFetch(`/rooms/${invitationCode}/candidates/suggest`, {
    method: "POST",
    headers: { "X-CSRFToken": csrfToken },
    body: new URLSearchParams({
      invitation_code: invitationCode,
    }),
  });

  return data;
}
