"use strict";

import { menuFunction, safeCreate } from "./base.js";

class Map {
  spinColor = "#9b30ff";
  iconMarkerUrl = "static/imgs/marker.svg";
  NewIconMarkerUrl = "static/imgs/new_marker.svg";
  overlay = document.querySelector(".overlay");
  formSection = document.querySelector(".party-creator");
  btnClosePopUp = document.querySelector(".pop-up button");
  popUp = document.querySelector(".pop-up");
  parties = document.querySelector(".parties");
  last_party = "";
  parties_bgc = document.querySelector(".parties_bgc");
  currentParties = [];
  activeMarker = false;
  party_form = document.querySelector(".form.form-creator");
  new_marker = "";
  constructor() {
    menuFunction();

    // Wyświetlanie formularza gdy nie uda się zapis
    if (!this.formSection.classList.contains("attempt"))
      this.formSection.classList.add("hidden");

    // INICJACJA MAPY
    this.map = L.map("map", {});
    this.map.spin(true, { color: this.spinColor });

    // POBRANIE GEOLOKACJI
    this.getLatLng();

    // DRAG/ZOOM EVENT na mapie
    this.map.on("moveend", async (e) => {
      // Pobieranie map range
      const range = this.map.getBounds();
      await this.sendMapRange(range);
      this.checkParty();
    });

    // CLICK MAP EVENT
    this.map.on("click", this.onMapClick.bind(this));

    // Click event na partybox
    this.parties_bgc.addEventListener("click", async (e) => {
      if (!e.target.closest(".party")) return;

      // Gdy na przycisk
      if (e.target.closest(".signup-btn")) {
        const response = await fetch(
          `map/sign-up/${
            e.target.closest(".party").getAttribute("id").split("-")[1]
          }`,
        );
        if (!response.ok) throw Error("We cant add your relations");
      }

      if (e.target.closest(".delete-btn")) {
        const response = await fetch(
          `map/sign-out/${
            e.target.closest(".party").getAttribute("id").split("-")[1]
          }`,
        );
        if (!response.ok) throw Error("We cant remove your relations");
      }

      this.formSection.classList.add("hidden");

      // Zoom na mapie po kliknięciu w party box
      const id = e.target.closest(".party").id;
      const marker = this.find_marker(id);
      marker.openPopup();
      this.map.setView(marker._latlng);
      this.last_party = e.target.closest(".party");
    });

    this.party_form.addEventListener("submit", () => {
      const party_btn = document.querySelector(".signup-btn");
      party_btn.disabled = true;
      party_btn.textContent = "Saving...";
    });
  }

  // GŁÓWNE
  // ------------------------
  // Pobiera (po zoomie, przesunięciu) skrajne pozycje widocznej mapy
  async sendMapRange(data) {
    const [_southWest, _northEast] = Object.values(data);

    try {
      const response = await fetch(
        `map/generate-parties/${[_southWest["lat"], _northEast["lat"]]},${[
          _southWest["lng"],
          _northEast["lng"],
        ]}`,
      );

      const [participiant_parties, user_parties, parties] =
        await response.json();
      const participiant_parties_data = JSON.parse(participiant_parties);
      const user_parties_data = JSON.parse(user_parties);
      const parties_data = JSON.parse(parties);

      this.parties_bgc.textContent = "";
      parties_data.forEach((el) => {
        // Create party box and return latlng
        const party_box = safeCreate(
          "div",
          { id: `party-${el["pk"]}`, class: "party" },
          this.parties_bgc,
        );
        safeCreate(
          "p",
          {
            class: "date",
          },
          party_box,
          el["fields"]["date"],
        );
        safeCreate(
          "div",
          {
            class: "img-hero",
            style: `background-image:url(https://media.nocturno.click/${el["fields"]["file_thumb"]})`,
          },
          party_box,
        );

        safeCreate("h4", {}, party_box, el["fields"]["party_title"]);
        this.createDesc(el, party_box);
        safeCreate(
          "a",
          { class: "show-users", href: `/buddies/initial-find/${el["pk"]}` },
          party_box,
          "Show users",
        );
        let class_btn = "signup-btn";
        let content = "Sign up";

        if (user_parties_data.some((party) => party.pk == el.pk)) {
          class_btn = "check-btn";
          content = "Check";
        } else if (
          participiant_parties_data.some((party) => party.pk == el.pk)
        ) {
          class_btn = "delete-btn";
          content = "Sign out ";
        }
        safeCreate("button", { class: class_btn }, party_box, content);
        const latlng = [el["fields"]["lat"], el["fields"]["lng"]];

        // Ustawianie active partybox gdy resize
        if (this.last_party.id == `party-${el["pk"]}`) {
          party_box.classList.add("active");
          this.last_party = party_box;
          this.scrollMapPartybox(this.last_party);
        }

        this.createPointer(latlng, el);
      });
    } catch {
      this.openErrorPopUp(
        "😭 We have problems with our database 😭",
        "Try again later ⌛",
      );
    }
  }

  openMapPopUp(el, e, id = false) {
    this.formSection.classList.add("hidden");
    this.map.setView([
      parseFloat(el["fields"]["lat"]),
      parseFloat(el["fields"]["lng"]),
    ]);
    let target;
    if (!id)
      // znajdywanie party box na podstawie id znacznika
      target = this.parties_bgc.querySelector(
        `#${e.target._icon.getAttribute("id")}`,
      );
    else target = this.parties_bgc.querySelector(id);
    return target;
  }

  createPointer(latlng, el = false) {
    const myIcon = L.icon({
      iconUrl: el != false ? this.iconMarkerUrl : this.NewIconMarkerUrl,
      iconSize: [38, 95],
    });

    // Tworzy znaczniki
    if (el != false) {
      // dla generownych
      this.new_marker = L.marker(latlng, {
        icon: myIcon,
        className: `map-popup-${el["pk"]}`,
        bubblingMouseEvents: true,
      });
    } else {
      // dla nowego - po kliknięciu użytkownika na mape
      this.new_marker = L.marker(latlng, {
        icon: myIcon,
        className: `map-popup-${el["pk"]}`,
        bubblingMouseEvents: true,
      });
      if (this.activeMarker) this.activeMarker.remove();
      this.activeMarker = marker;
    }

    this.new_marker.addTo(this.map);
    this.currentParties.push(marker);

    // TWWORZENIE MAP POPUP + SCROLL DO PARTYBOX
    this.new_marker.on("click", (e) => {
      const target = this.openMapPopUp(el, e);

      if (this.last_party.id != target.id) {
        target.classList.add("active");
        this.last_party = target;
        // Podpięcie w wrapper party scrolla do partyBox
        this.scrollMapPartybox(target);
      }
    });

    // Tworzenie popupów
    if (el) {
      this.new_marker._icon.setAttribute("id", `party-${el["pk"]}`);
      const popUpContent = safeCreate("div", { class: "map-popup-content" });
      safeCreate("h4", {}, popUpContent, el["fields"]["party_title"]);
      // dodać description
      safeCreate(
        "p",
        { class: "description" },
        popUpContent,
        el["fields"]["description"],
      );
      this.createDesc(el, popUpContent);

      const mapPopup = L.popup(
        [parseFloat(el["fields"]["lat"]), parseFloat(el["fields"]["lng"])],
        {
          content: popUpContent.innerHTML,
          keepInView: true,
          minWidth: 310,
          maxWidth: 320,
          className: `map-popup `,
          autoPan: false,
        },
      );

      this.new_marker.bindPopup(mapPopup).on("popupclose", () => {
        this.last_party.classList.remove("active");
        this.last_party = "";
      });
    }
  }

  // PO KLIKNIĘCIU PRZEKAZUJE DANE DO CREATE POINTER -> NASTEPUJE PRZYPIECIE ZNACZNIKA
  async onMapClick(e) {
    // Zamknięcie party creator
    const closeBtn = this.formSection.querySelector(".close-creator");
    closeBtn.addEventListener("click", () =>
      this.formSection.classList.add("hidden"),
    );

    // Otwarcie
    this.formSection.classList.remove("hidden");
    const latlng = Object.values(e.latlng);
    // Dodawanie ikony
    this.createPointer(latlng);

    const [lat, lng] = latlng;

    // Pozyskiwanie współżędnych eventu
    let address;
    try {
      address = await this.getAdress(lat, lng);
    } catch (error) {
      this.openErrorPopUp(
        "We have problems with reverse geolocalization 😭",
        "Try again later ⌛",
      );
    }

    const addressFields = document.querySelectorAll(".address input");
    //Wypełnienie addressForm
    if (address != undefined) this.fillForm(address, lat, lng, addressFields);
  }

  // POZYSKIWANIE  WSPÓŁŻĘDNYCH EVENTU
  async getAdress(lat, lng) {
    let address;
    try {
      // Reverse geocoding
      address = await fetch(`/geocode-reverse?lat=${lat}&lng=${lng}`);
      // Sprawdzanie czy ok
      if (!address.ok) throw new Error(`Data isn't correct!`);

      // json -> obj
      const data = await address.json();

      if (data["type"] == "university")
        throw new Error("This isn't good place to party");

      return data;
    } catch (error) {
      this.popUp;
      this.openErrorPopUp("Reverse geocoding failed! 😭", "Try again later ⌛");
    }
  }

  // TWORZENIE MAPY
  createMap(lat, lng) {
    // Ustawianie lokalizacji na mapie
    this.map.setView([lat, lng], 15);

    // Dodanie warstwy
    const tile = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      referrerPolicy: "strict-origin-when-cross-origin",
      attribution:
        '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    });
    // Spin on load
    tile.on("load", () => this.map.spin(false));

    tile.addTo(this.map);
  }

  // POBRANIE GEOLOKACJI
  getLatLng = () => {
    try {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          let { latitude: lat, longitude: lng } = pos.coords;

          // dla main -> check -> map find party

          this.createMap(lat, lng);
        },
        () => {
          const lat = 52.237049;
          const lng = 21.017532;
          this.createMap(lat, lng);
        },
      );
    } catch {
      this.openErrorPopUp(
        "😭 Something goes wrong 😭",
        "We haven't acces to your geolocation ⌛",
      );
    }
  };

  // POMOCNICZE
  // ------------------------
  // Scroll do konkretnego partybox
  scrollMapPartybox(scrollToEl) {
    if (window.matchMedia("(min-width: 1250px)").matches) {
      const parties = document.querySelector(".parties");
      parties.scrollTop = scrollToEl.offsetTop;
    } else {
      this.parties_bgc.scrollLeft = scrollToEl.offsetLeft - 16;
    }
  }

  async checkParty() {
    let check_party = document.cookie.split(";");
    let party_id;
    check_party.forEach((el) => {
      if (el.includes("party=")) {
        party_id = el.split("=")[1];
      }
    });
    try {
      party_id = Number(party_id);
    } catch {
      console.log("no choice id");
    }
    if (party_id) {
      const respone = await fetch(`map/check/${party_id}`);
      if (!respone.ok) throw new Error("We can't find your Party:(");
      const party = await respone.json();
      const party_parsed = JSON.parse(party)[0];

      console.log(party_parsed["pk"]);

      const target = this.parties_bgc.querySelector(
        `#party-${party_parsed["pk"]}`,
      );

      if (this.last_party.id != target.id) {
        target.classList.add("active");
        this.last_party = target;
        // Podpięcie w wrapper party scrolla do partyBox
        this.scrollMapPartybox(target);
        document.cookie = "party=";
        const marker = this.find_marker(`#party-${party_parsed["pk"]}`);
        this.map.setView(marker._latlng);
        marker.openPopup();
      }
    }
  }

  find_marker(id) {
    const marker = this.currentParties.find(
      (el) => el.options.className.split("-")[2] == id.split("-")[1],
    );
    return marker;
  }

  openErrorPopUp(header, content, btnTxt = "Refresh the page", error = true) {
    const popHeader = this.popUp.querySelector(".pop-header");
    const popContent = this.popUp.querySelector(".pop-content");
    if (error == true) {
      popHeader.textContent = header;
      popContent.textContent = content;
      safeCreate("a", { href: "/map" }, this.popUp, btnTxt);
    }

    this.popUp.classList.remove("hidden");
    this.overlay.classList.remove("hidden");
  }

  createDesc(el, wrapper) {
    const desc = safeCreate("div", { class: "desc" }, wrapper);

    const el1 = safeCreate("div", { class: "el" }, desc);
    safeCreate("i", { class: "fas fa-wine-glass-alt" }, el1);
    safeCreate("p", {}, el1, el["fields"]["alco"]);

    const el2 = safeCreate("div", { class: "el" }, desc);
    safeCreate("i", { class: "far fa-id-card" }, el2);
    safeCreate("p", {}, el2, el["fields"]["age"]);

    const el3 = safeCreate("div", { class: "el" }, desc);
    safeCreate("i", { class: "fas fa-users" }, el3);
    safeCreate("p", {}, el3, el["fields"]["participants"].length);
  }

  // WYPEŁNIANIE FORMADDRESS
  fillForm(data, lat, lng, form_fields) {
    const latField = document.querySelector(".lat input");
    const lngField = document.querySelector(".lng input");
    const ageField = document.querySelector(".age input");
    const alcoField = document.querySelector(".alco");

    // Wyciąganie adresu
    const { address: clearData } = data;

    // Uzupełnianie pół
    form_fields.forEach((field) => {
      field.value = clearData[`${field.name}`];
      if (field.value == "undefined")
        field.value = `No ${field.name.split("_").join(" ")}`;
    });
    latField.value = String(lat).slice(0, 8);
    lngField.value = String(lng).slice(0, 8);

    let age = "";
    ageField.addEventListener("input", (e) => {
      if (Number(e.data)) {
        age += e.data;
      } else {
        const num = ageField.value;
        age = num;
      }

      if (Number(age) >= 18) {
        alcoField.style.display = "block";
      }
    });
  }
}

const map = new Map();
