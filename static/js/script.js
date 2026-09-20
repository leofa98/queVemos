"use strict";

const d = document;
const csrfToken = d.querySelector("meta[name='csrf-token']").content;

d.addEventListener("DOMContentLoaded", function () {
  const deleteModal = d.getElementById("deleteModal");
  let entryCardDelete = d.querySelectorAll(".entry-card-delete");

  entryCardDelete.forEach((button) => {
    button.addEventListener("click", (e) => {
      let entryId = e.currentTarget.dataset.entryid;

      deleteModal.dataset.entryid = entryId;
      new bootstrap.Modal(deleteModal).show();
      d.getElementById("deleteConfirm").onclick = () => {
        removeEntry(entryId);
        d.querySelector(`[data-entryId='${entryId}']`).remove();
        bootstrap.Modal.getInstance(deleteModal).hide();
      };
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

    let data = response.json();

    return data;
  } catch (error) {
    console.error(error.message);
    return null;
  }
}
