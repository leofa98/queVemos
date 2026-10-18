"use strict";

const d = document;
const csrfToken = d.querySelector("meta[name='csrf-token']").content;

d.addEventListener("DOMContentLoaded", function () {
  const deleteModalElement = d.getElementById("delete-modal");
  const editModalElement = d.getElementById("edit-modal");
  const addTitleModalElement = d.getElementById("add-title-modal");
  const deleteModal = new bootstrap.Modal(deleteModalElement);
  const editModal = new bootstrap.Modal(editModalElement);
  const addTitleModal = new bootstrap.Modal(addTitleModalElement);
  const addTitleButton = d.getElementById("add-title-btn");
  const saveTitleButton = d.getElementById("save-title-btn");
  const statusChips = d.querySelectorAll(".status-chip");
  const entryList = d.getElementById("entry-list");
  const spinner = d.getElementById("spinner");
  const searchInput = d.getElementById("search-input");
  const editTitleSelect = editModalElement.querySelector("select");
  const editStatusRadioButtons =
    editModalElement.querySelectorAll(".edit-status input");
  const editRating = editModalElement.querySelector("input[name='rating']");
  const editComment = editModalElement.querySelector(
    "textarea[name='comment']",
  );
  const addEntrySelect = addTitleModalElement.querySelector("select");
  const addEntryStatusRadioButtons = addTitleModalElement.querySelectorAll(
    ".add-title-status input",
  );
  const addEntryRating = addTitleModalElement.querySelector(
    "input[name='rating']",
  );
  const addEntryComment = addTitleModalElement.querySelector(
    "textarea[name='comment']",
  );

  const debouncedFilter = debounce(async () => {
    try {
      let entries = await filterEntries(query, status, page);
      if (entries) {
        entryList.innerHTML = entries;
      }
    } finally {
      entryList.classList.remove("d-none");
      spinner.classList.add("d-none");
    }
  }, 1000);

  let status = "";
  let query = "";
  let page = "";

  [...editStatusRadioButtons].forEach((button) => {
    button.addEventListener("change", (e) => {
      editRating.disabled = e.target.value != "seen";
      editRating.value = editRating.disabled ? "" : editRating.value;
    });
  });

  [...addEntryStatusRadioButtons].forEach((button) => {
    button.addEventListener("change", (e) => {
      addEntryRating.disabled = e.target.value != "seen";
      editRating.value = editRating.disabled ? "" : editRating.value;
    });
  });

  addTitleButton.addEventListener("click", () => {
    [...addEntryStatusRadioButtons].map((option) =>
      option.value == "pending"
        ? (option.checked = true)
        : (option.checked = false),
    ).value;
    addEntryRating.value = null;
    addEntrySelect.value = "";
    addEntryComment.value = null;
    addTitleModal.show();
  });

  saveTitleButton.addEventListener("click", async () => {
    let title = addEntrySelect.value;
    let status = [...addEntryStatusRadioButtons].find(
      (option) => option.checked,
    ).value;

    let rating = addEntryRating.value;
    let comment = addEntryComment.value;
    let response = await addEntry(title, status, rating, comment);
    if (response) {
      page = 1;
      entryList.classList.add("d-none");
      spinner.classList.remove("d-none");
      debouncedFilter();
      showToast("success", response.message);
      addTitleModal.hide();
    }
  });

  entryList.addEventListener("click", async (e) => {
    if (e.target.closest(".entry-card-delete")) {
      let entryId = e.target.closest(".entry-card-delete").dataset.entryid;
      deleteModalElement.dataset.entryid = entryId;
      deleteModal.show();
      d.getElementById("deleteConfirm").onclick = async () => {
        let response = await removeEntry(entryId);
        if (response) {
          entryList.classList.add("d-none");
          spinner.classList.remove("d-none");
          debouncedFilter();
          showToast("success", response.message);
          deleteModal.hide();
        }
      };
    }

    if (e.target.closest(".entry-card-edit")) {
      let entryId = e.target.closest(".entry-card-edit").dataset.entryId;
      let entryData = await getEntry(entryId);

      editTitleSelect.value = entryData.title;

      [...editStatusRadioButtons].map((option) => {
        option.checked = option.value == entryData.status;
      });

      editRating.value = entryData.rating;
      editComment.value = entryData.comment;

      editRating.disabled =
        entryData.status == "pending" || entryData.status == "dropped";

      editModal.show();
      editModalElement.querySelector("#save-edit").onclick = async () => {
        let selectedStatusOption = [...editStatusRadioButtons].find(
          (option) => option.checked,
        );

        let response = await editEntry(
          entryId,
          editTitleSelect.value,
          selectedStatusOption.value,
          editRating.value,
          editComment.value,
        );

        if (response) {
          debouncedFilter();
          showToast("success", response.message);
          entryList.classList.add("d-none");
          spinner.classList.remove("d-none");
          editModal.hide();
        }
      };
    }
    if (e.target.closest(".page-item")) {
      entryList.classList.add("d-none");
      spinner.classList.remove("d-none");
      page = e.target.closest(".page-item").dataset.pageNum;
      debouncedFilter();
    }
  });

  searchInput.addEventListener("keyup", () => {
    query = searchInput.value.trim();
    page = 1;
    entryList.classList.add("d-none");
    spinner.classList.remove("d-none");
    debouncedFilter();
  });

  statusChips.forEach((chip) => {
    chip.addEventListener("click", async (e) => {
      entryList.classList.add("d-none");
      spinner.classList.remove("d-none");
      status = chip.dataset.status;

      [...statusChips].map((chip) => {
        if (chip.dataset.status == status) {
          chip.classList.add("active");
        } else {
          chip.classList.remove("active");
        }
      });
      page = 1;
      debouncedFilter();
    });
  });
});

async function addEntry(title, status, rating, comment) {
  let data = await apiFetch(`/library/new`, {
    method: "POST",
    headers: { "X-CSRFToken": csrfToken },
    body: new URLSearchParams({
      title: title,
      status: status,
      rating: rating,
      comment: comment,
    }),
  });
  return data;
}

async function removeEntry(entryId) {
  let data = await apiFetch(`/library/${entryId}/remove`, {
    method: "POST",
    headers: { "X-CSRFToken": csrfToken },
  });
  return data;
}

async function getEntry(entryId) {
  let data = await apiFetch(`/library/entry/${entryId}`, { method: "GET" });
  return data;
}

async function editEntry(entryId, title, status, rating, comment) {
  let data = await apiFetch(`/library/${entryId}/edit`, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
      "Content-Type": "application/x-www-form-urlencoded",
    },

    body: new URLSearchParams({
      title: title,
      status: status,
      rating: rating,
      comment: comment,
    }),
  });
  return data;
}

async function filterEntries(query, status, page) {
  const params = new URLSearchParams({
    status,
    query,
    page,
  });
  let data = await apiFetchText(`/library/entries?${params}`, {
    method: "GET",
    headers: { "X-CSRFToken": csrfToken },
  });
  return data;
}
