"use strict";
import { addBuddie } from "./base.js";

const searchRow = document.querySelector(".search-row");

searchRow.addEventListener("click", (e) => addBuddie(e));
