"use strict";
import { menuFunction, show, animateScroll } from "./base.js";
const rowTrendings = document.querySelector(".popular-party .row-parties");
const userPerties = document.querySelector(".user-party .row-parties");
const bgcImg = document.querySelector(".parties_bgc");
document.addEventListener("DOMContentLoaded", menuFunction);

window.addEventListener("scroll", show);

// ////////////////////////////////////////////////

if (window.matchMedia("(min-width: 724px)").matches) {
  bgcImg.addEventListener("click", (e) => {
    if (!e.target.closest(".signup-btn")) return;
    const id = e.target.getAttribute("id");
    document.cookie = `party=${id};`;
    console.log(document.cookie);
  });

  rowTrendings.addEventListener(
    "wheel",
    (e) => {
      e.preventDefault();
      if (e.deltaY == 0) return;
      console.log(`12`);
      const partiesBgc = rowTrendings.querySelector(".parties_bgc");
      animateScroll(partiesBgc, rowTrendings, e.deltaY);
    },
    { passive: false }
  );

  userPerties.addEventListener(
    "wheel",
    (e) => {
      console.log(e);
      e.preventDefault();
      if (e.deltaY == 0) return;
      const partiesBgc = userPerties.querySelector(".parties_bgc");
      animateScroll(partiesBgc, userPerties, e.deltaY);
    },
    { passive: false }
  );
}
