"use strict";
import { menuFunction, show } from "./base.js";

menuFunction();

const layout = document.querySelector(".layout");

if (layout.getBoundingClientRect() <= 524)
  window.addEventListener("scroll", show);
const register_form = document.querySelector(".register-form");

register_form.addEventListener("submit", () => {
  const register_btn = document.querySelector(".signup-btn");
  register_btn.disabled = true;
  register_btn.textContent = "Saving...";
});
