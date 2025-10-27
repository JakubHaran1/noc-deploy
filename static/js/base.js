"use strict";
const nav = document.querySelector(".nav");

const menuFunction = () => {
  window.addEventListener("scroll", show);
  const menu = document.querySelector(".nav");
  const menuHeight = menu.getBoundingClientRect().height;
  const layout = document.querySelector("body");
  layout.style.paddingBottom = `${menuHeight}px`;
};

const iconLoad = () => {
  const layout = document.querySelector(".layout");
  layout.classList.add("unload");
  window.addEventListener("load", () => {
    layout.classList.remove("unload");
  });
};

//
let timeOut;
const show = () => {
  clearTimeout(timeOut);
  nav.classList.add("scroll");
  timeOut = setTimeout(() => {
    nav.classList.remove("scroll");
  }, 300);
};

const animateScroll = (inner, outer, speed) => {
  let maxScroll = inner.scrollWidth - outer.clientWidth;
  let currX = new Number(inner.style.transform.match(/-?\d+/g));
  currX += speed;
  console.log(currX);
  if (currX > 0) {
    currX = 0;
  } else if (currX <= -maxScroll) {
    currX = -maxScroll;
  }
  inner.style.transform = `translateX(${currX}px)`;
};

const safeCreate = (tag, attr = {}, parent = false, field_content = null) => {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attr)) {
    el.setAttribute(key, value);
  }
  if (field_content != null) el.textContent = field_content;
  if (parent != false) parent.append(el);
  return el;
};

const addBuddie = async (e) => {
  e.preventDefault();
  const el = e.target.closest(".actionBtn");
  console.log(el);
  if (!el) return;
  const action = el.dataset.action;
  const friendID = el.dataset.id;
  const fetchLink = `/buddies/action-buddie/`;

  try {
    const sendData = await fetch(fetchLink, {
      method: "POST",
      body: JSON.stringify([friendID, action]),
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document
          .querySelector('meta[name="csrf-token"]')
          .getAttribute("content"),
      },
    });

    if (!sendData.ok)
      throw new Error("We can't add this buddie to your list 😭");
    if (action == "add") {
      el.classList.remove("signup-btn");
      el.classList.add("delete-btn");
      el.textContent = "Delete";
    } else {
      el.classList.remove("delete-btn");
      el.classList.add("signup-btn");
      el.textContent = "Add";
    }
  } catch (err) {
    console.log(err);
  }
};

export { menuFunction, iconLoad, show, animateScroll, safeCreate, addBuddie };
