"use strict";
import { menuFunction, show } from "./base.js";

menuFunction();

const layout = document.querySelector(".layout");

if (layout.getBoundingClientRect() <= 524)
  window.addEventListener("scroll", show);
