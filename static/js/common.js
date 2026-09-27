"use strict";

async function apiFetch(url, options) {
  try {
    let response = await fetch(url, options);
    if (!response.ok) {
      const data = await response.json();
      throw new Error(
        data.message || `Error ${response.status}: ${response.statusText}`,
      );
    }
    let data = await response.json();
    return data;
  } catch (error) {
    showToast("danger", error.message);
    return null;
  }
}

async function apiFetchText(url, options) {
  try {
    let response = await fetch(url, options);
    if (!response.ok) {
      const data = await response.text();
      throw new Error(
        data.message || `Error ${response.status}: ${response.statusText}`,
      );
    }
    let data = await response.text();
    return data;
  } catch (error) {
    showToast("danger", error.message);
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

function showToast(type, message) {
  const toastElement = document.getElementById(`toast-${type}`);
  let toastMessage = d.getElementById(`toast-${type}-msg`);
  toastMessage.textContent = message;
  const toast = new bootstrap.Toast(toastElement);
  toast.show();
}
