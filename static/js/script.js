"use strict";

const d = document;
const csrfToken = d.querySelector("meta[name='csrf-token']").content;

d.addEventListener("DOMContentLoaded", function () {
  const deleteModal = d.getElementById("deleteModal");
  const editModal = d.getElementById("editModal");
  const statusChips = d.querySelectorAll(".status-chip");
  const entryList = d.getElementById("entry-list");
  const searchInput = d.getElementById("search-input");
  const editTitleSelect = editModal.querySelector("select");
  const editStatusRadioButtons =
    editModal.querySelectorAll(".edit-status input");
  const editRating = editModal.querySelector("input[name='rating']");
  const editComment = editModal.querySelector("textarea[name='comment']");
  const debouncedFilter = debounce(async () => {
    let entries = await filterEntries(query, status, page);
    entryList.innerHTML = entries;
  }, 1500);
  let status = "";
  let query = "";
  let page = "";

  entryList.addEventListener("click", async (e) => {
    if (e.target.closest(".entry-card-delete")) {
      let entryId = e.target.closest(".entry-card-delete").dataset.entryid;
      deleteModal.dataset.entryid = entryId;
      new bootstrap.Modal(deleteModal).show();
      d.getElementById("deleteConfirm").onclick = async () => {
        await removeEntry(entryId);
        entryList.querySelector(`[data-entryId='${entryId}']`).remove();
        debouncedFilter();
        bootstrap.Modal.getInstance(deleteModal).hide();
      };
    }

    if (e.target.closest(".entry-card-edit")) {
      let entryId = e.target.closest(".entry-card-edit").dataset.entryid;
      let entryData = await getEntry(entryId);

      console.log(entryData);

      editTitleSelect.value = entryData.title;

      [...editStatusRadioButtons].map((option) => {
        option.checked = option.value == entryData.status;
      });

      editRating.value = entryData.rating;
      editComment.value = entryData.comment;

      new bootstrap.Modal(editModal).show();
      editModal.querySelector("#save-edit").onclick = async () => {
        let selectedStatusOption = [...editStatusRadioButtons].find(
          (option) => option.checked,
        );
        await editEntry(
          entryId,
          editTitleSelect.value,
          selectedStatusOption.value,
          editRating.value,
          editComment.value,
        );
        debouncedFilter();
        bootstrap.Modal.getInstance(editModal).hide();
      };
    }
  });

  searchInput.addEventListener("keyup", () => {
    query = searchInput.value.trim();
    debouncedFilter();
  });

  statusChips.forEach((chip) => {
    chip.addEventListener("click", async (e) => {
      status = chip.dataset.status;

      [...statusChips].map((chip) => {
        if (chip.dataset.status == status) {
          chip.classList.add("active");
        } else {
          chip.classList.remove("active");
        }
      });
      debouncedFilter();
    });
  });
});

async function removeEntry(entryId) {
  try {
    let response = await fetch(`library/${entryId}/remove`, {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken },
    });
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }

    let data = await response.json();

    return data;
  } catch (error) {
    console.error(error.message);
    return null;
  }
}

async function getEntry(entryId) {
  try {
    console.log(`library/entry/${entryId}`);
    let response = await fetch(`library/entry/${entryId}`);

    if (!response.ok) {
      throw Error(`Error ${response.status} ${response.statusText}`);
    }

    let data = await response.json();

    return data;
  } catch (error) {
    console.error(error.message);
    return null;
  }
}

async function editEntry(entryId, title, status, rating, comment) {
  try {
    let response = await fetch(`library/${entryId}/edit`, {
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

    if (!response.ok) {
      throw Error(`Error ${response.status} ${response.statusText}`);
    }
    let data = await response.text();
    return data;
  } catch (error) {
    console.error(error.message);
    return null;
  }
}

async function filterEntries(query, status, page) {
  try {
    const params = new URLSearchParams({
      status,
      query,
      page,
    });
    let response = await fetch(`library/entries?${params}`, {
      method: "GET",
      headers: { "X-CSRFToken": csrfToken },
    });

    if (!response.ok) {
      throw new Error(`${response.status}: ${response.statusText}`);
    }

    let data = await response.text();
    return data;
  } catch (error) {
    return null;
  }
}

function debounce(callback, time) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      callback(...args);
    }, time);
  };
}
