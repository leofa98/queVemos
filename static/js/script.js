"use strict";

const d = document;
const csrfToken = d.querySelector("meta[name='csrf-token']").content;

d.addEventListener("DOMContentLoaded", function () {
  const deleteModal = d.getElementById("deleteModal");
  const entryCardDelete = d.querySelectorAll(".entry-card-delete");
  const statusChips = d.querySelectorAll(".status-chip");
  const entryList = d.getElementById("entry-list");
  const searchInput = d.getElementById("search-input");
  let status = "";
  let query = "";
  let page = "";
  entryList.addEventListener("click", (e) => {
    if (e.target.closest(".entry-card-delete")) {
      let entryId = e.target.dataset.entryid;
      console.log("fdsd");
      deleteModal.dataset.entryid = entryId;
      new bootstrap.Modal(deleteModal).show();
      d.getElementById("deleteConfirm").onclick = () => {
        removeEntry(entryId);
        d.querySelector(`[data-entryId='${entryId}']`).remove();
        bootstrap.Modal.getInstance(deleteModal).hide();
      };
    }
  });

  searchInput.addEventListener("keyup", () => {
    query = searchInput.value.trim();
    const debouncedFilter = debounce(async () => {
      let entries = await filterEntries(query, status, page);
      entryList.innerHTML = entries;
    }, 2000);
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
      const debouncedFilter = debounce(async () => {
        let entries = await filterEntries(query, status, page);
        entryList.innerHTML = entries;
      }, 2000);

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

async function filterEntries(query, status, page) {
  try {
    let response = await fetch(
      `library/entries?status=${status}&query=${query}&page=${page}`,
      {
        method: "GET",
        headers: { "X-CSRFToken": csrfToken },
      },
    );

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
