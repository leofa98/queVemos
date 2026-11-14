"use strict";

const d = document;
const csrfToken = d.querySelector("meta[name='csrf-token']").content;
d.addEventListener("DOMContentLoaded", () => {
  const statusChips = d.querySelectorAll(".status-chip");
  const createRoomBtn = d.getElementById("create-room-btn");
  const createRoomBtnModal = d.getElementById("create-room-modal-btn");
  const addRoomModalElement = d.getElementById("create-room-modal");
  const addRoomModal = new bootstrap.Modal(addRoomModalElement);
  const roomNameInput = d.getElementById("room-name");
  const allowSeenCheck = d.getElementById("allow-seen");
  const roomList = d.getElementById("room-list");
  const spinner = d.getElementById("spinner");
  const btnJoinRoom = d.getElementById("btn-join-room");
  const codeInput = d.getElementById("invitation-code");

  let status = "";
  let page = "";
  const debouncedFilter = debounce(async () => {
    try {
      let roomsHtml = await filterRooms(status, page);
      if (roomsHtml) {
        roomList.innerHTML = roomsHtml;
      }
    } finally {
      roomList.classList.remove("d-none");
      spinner.classList.add("d-none");
    }
  }, 1000);

  createRoomBtn.addEventListener("click", async () => {
    roomNameInput.value = "";
    allowSeenCheck.checked = false;
  });

  createRoomBtnModal.addEventListener("click", async () => {
    let name = roomNameInput.value;
    let allowSeen = allowSeenCheck.checked;
    let response = await addRoom(name, allowSeen);

    if (response) {
      roomList.classList.add("d-none");
      spinner.classList.remove("d-none");
      showToast("success", response.message);
      debouncedFilter();
      addRoomModal.hide();
    }
  });

  [...statusChips].forEach((chip) => {
    chip.addEventListener("click", (e) => {
      status = e.currentTarget.dataset.status;
      [...statusChips].map((chip) => {
        if (chip.dataset.status == status) {
          chip.classList.add("active");
        } else {
          chip.classList.remove("active");
        }
      });
      roomList.classList.add("d-none");
      spinner.classList.remove("d-none");
      debouncedFilter();
    });
  });
  roomList.addEventListener("click", (e) => {
    if (e.target.closest(".page-item")) {
      page = e.target.closest(".page-item").dataset.pageNum;
      roomList.classList.add("d-none");
      spinner.classList.remove("d-none");
      debouncedFilter();
    }
  });
  btnJoinRoom.addEventListener("click", async () => {
    let code = codeInput.value.trim().toUpperCase();
    let response = await joinRoom(code);
    if (response) {
      window.location.href = response.redirect_url;
    }
  });
});

async function addRoom(name, allow_seen) {
  let data = await apiFetch("rooms/new", {
    method: "POST",
    headers: { "X-CSRFToken": csrfToken },
    body: new URLSearchParams({
      name,
      allow_seen,
    }),
  });
  return data;
}

async function joinRoom(invitationCode) {
  let data = await apiFetch(`rooms/join`, {
    method: "POST",
    headers: { "X-CSRFToken": csrfToken },
    body: new URLSearchParams({
      invitation_code: invitationCode,
    }),
  });
  return data;
}

async function filterRooms(status, page) {
  const params = new URLSearchParams({
    status,
    page,
  });
  let data = await apiFetchText(`rooms/list?${params} `, {
    method: "GET",
  });
  return data;
}
