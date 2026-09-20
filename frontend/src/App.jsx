import { useEffect, useState } from "react";
import {
  CircleMarker,
  MapContainer,
  Polyline,
  TileLayer,
  useMap,
  useMapEvents,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";

const API_BASE =
  "https://nmaqro1w6i.execute-api.ap-south-1.amazonaws.com";

const OVERPASS_URL =
  "https://overpass-api.de/api/interpreter";

const categories = [
  ["healthcare", "Healthcare", "Hospitals, clinics & medical centers", "＋"],
  ["education", "Education", "Schools, colleges & universities", "◇"],
  ["transport", "Transport", "Airports, railway & transit", "↗"],
  ["commerce", "Commerce", "Malls, markets & business areas", "□"],
  ["entertainment", "Entertainment", "Theatres, stadiums & venues", "○"],
  ["public", "Public & Government", "Civic buildings & public services", "△"],
  ["hospitality", "Hospitality", "Hotels, resorts & restaurants", "✦"],
  ["residential", "Residential", "Neighbourhoods & communities", "⌂"],
  ["infrastructure", "Infrastructure", "Utilities, industry & facilities", "▦"],
  ["tourism", "Tourism & Public Spaces", "Parks, museums & landmarks", "◉"],
  ["sports", "Sports", "Stadiums & sports complexes", "◎"],
  ["community", "Community", "Community & gathering spaces", "♧"],
];

const experiments = {
  healthcare: [
    ["medical_access", "Emergency access changes", "See how access could change around a medical facility."],
    ["evacuation", "People need to leave", "Explore movement when people need to leave quickly."],
    ["crowd", "More people arrive", "Explore what happens when arrivals increase."],
    ["road", "An access road closes", "See how a road closure could affect access."],
  ],
  education: [
    ["evacuation", "People need to leave", "Explore how a large group could move out quickly."],
    ["entrance", "An entrance becomes unavailable", "See how movement changes when an access point closes."],
    ["crowd", "A crowd suddenly grows", "Explore movement when more people arrive."],
    ["road", "A road becomes unavailable", "See how surrounding access could change."],
  ],
  transport: [
    ["road", "An access route closes", "Explore how people could reach or leave the transport hub."],
    ["crowd", "Passenger numbers increase", "Explore movement when the crowd becomes larger."],
    ["evacuation", "People need to leave", "Explore movement during an emergency."],
    ["access", "Emergency access changes", "See how emergency response access could change."],
  ],
  commerce: [
    ["evacuation", "People need to leave", "Explore how a large visitor group could leave."],
    ["entrance", "An entrance becomes unavailable", "See how access changes when an entrance closes."],
    ["crowd", "Visitor numbers increase", "Explore movement with more visitors."],
    ["road", "A surrounding road closes", "See how access to the area could change."],
  ],
  entertainment: [
    ["evacuation", "Everyone needs to leave", "Explore how a large crowd could leave quickly."],
    ["entrance", "An entrance becomes unavailable", "See how movement changes when access is reduced."],
    ["crowd", "The crowd grows", "Explore what happens when more visitors arrive."],
    ["road", "An access road closes", "See how surrounding movement could change."],
  ],
  default: [
    ["evacuation", "People need to leave", "Explore movement when people need to leave quickly."],
    ["road", "A road becomes unavailable", "See how access could change when a route closes."],
    ["crowd", "More people arrive", "Explore how the area responds to a larger crowd."],
    ["access", "Emergency access changes", "Explore how emergency access could change."],
  ],
};

const introDots = [
  ["18%", "25%", "-210px", "-110px", ".0s"],
  ["29%", "17%", "180px", "-180px", ".05s"],
  ["41%", "12%", "-160px", "-220px", ".1s"],
  ["54%", "16%", "210px", "-190px", ".15s"],
  ["68%", "25%", "250px", "-80px", ".2s"],
  ["78%", "38%", "220px", "50px", ".25s"],
  ["82%", "52%", "240px", "120px", ".3s"],
  ["72%", "66%", "180px", "190px", ".35s"],
  ["60%", "76%", "110px", "220px", ".4s"],
  ["46%", "82%", "-80px", "230px", ".45s"],
  ["32%", "75%", "-190px", "210px", ".5s"],
  ["21%", "64%", "-240px", "160px", ".55s"],
  ["17%", "49%", "-250px", "10px", ".6s"],
  ["25%", "36%", "-230px", "-70px", ".65s"],
  ["37%", "29%", "-150px", "-160px", ".7s"],
  ["50%", "25%", "0px", "-210px", ".75s"],
  ["63%", "30%", "150px", "-150px", ".8s"],
  ["71%", "44%", "210px", "-20px", ".85s"],
  ["66%", "58%", "150px", "120px", ".9s"],
  ["53%", "68%", "30px", "180px", ".95s"],
  ["40%", "65%", "-100px", "160px", "1s"],
  ["31%", "54%", "-170px", "80px", "1.05s"],
  ["36%", "42%", "-130px", "-10px", "1.1s"],
  ["49%", "38%", "10px", "-70px", "1.15s"],
  ["58%", "47%", "100px", "30px", "1.2s"],
  ["48%", "56%", "-10px", "110px", "1.25s"],
];

function FlyToPlace({ place }) {
  const map = useMap();

  useEffect(() => {
    if (!place?.position) return;

    const [lng, lat] = place.position;

    map.flyTo(
      [Number(lat), Number(lng)],
      16,
      { duration: 1.2 }
    );
  }, [map, place]);

  return null;
}

function CenterTracker({ setCenter }) {
  useMapEvents({
    moveend(event) {
      const c = event.target.getCenter();
      setCenter([c.lat, c.lng]);
    },
  });

  return null;
}

function App() {
  const [intro, setIntro] = useState(true);
  const [screen, setScreen] = useState("home");

  const [category, setCategory] = useState(null);

  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState("");

  const [center, setCenter] = useState([20, 0]);

  const [place, setPlace] = useState(null);

  const [roads, setRoads] = useState([]);
  const [nearby, setNearby] = useState([]);
  const [selectedRoad, setSelectedRoad] = useState(null);

  const [experiment, setExperiment] = useState(null);
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    const timer = setTimeout(
      () => setIntro(false),
      3100
    );

    return () => clearTimeout(timer);
  }, []);

  async function searchPlace() {
    if (!query.trim()) return;

    setSearching(true);
    setResults([]);
    setError("");

    try {
      const [lat, lng] = center;

      const response = await fetch(
        `${API_BASE}/places/search?q=${encodeURIComponent(
          query
        )}&lat=${lat}&lng=${lng}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.message ||
            data?.error ||
            "Search failed."
        );
      }

      setResults(
        Array.isArray(data.places)
          ? data.places
          : []
      );
    } catch {
      setError(
        "We couldn't find that place. Try a more specific name."
      );
    } finally {
      setSearching(false);
    }
  }

  async function loadNearby(selectedPlace) {
    if (!selectedPlace?.position) return;

    const [lng, lat] =
      selectedPlace.position;

    try {
      const query = `
        [out:json][timeout:20];
        (
          way["highway"](around:700,${lat},${lng});
          nwr["amenity"](around:700,${lat},${lng});
          nwr["shop"](around:700,${lat},${lng});
          nwr["tourism"](around:700,${lat},${lng});
          nwr["public_transport"](around:700,${lat},${lng});
          nwr["railway"](around:700,${lat},${lng});
        );
        out center geom tags;
      `;

      const response = await fetch(
        OVERPASS_URL,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/x-www-form-urlencoded",
          },
          body:
            `data=${encodeURIComponent(query)}`,
        }
      );

      if (!response.ok) return;

      const data = await response.json();

      const roadList = [];
      const nearbyList = [];

      for (const element of data.elements || []) {
        const tags = element.tags || {};

        if (
          element.type === "way" &&
          tags.highway &&
          Array.isArray(element.geometry)
        ) {
          roadList.push({
            id: element.id,
            name:
              tags.name ||
              "Unnamed road",
            type: tags.highway,
            coordinates:
              element.geometry.map(
                (point) => [
                  Number(point.lat),
                  Number(point.lon),
                ]
              ),
          });

          continue;
        }

        const name =
          tags.name ||
          tags.amenity ||
          tags.shop ||
          tags.tourism ||
          tags.railway ||
          tags.public_transport;

        if (name && element.center) {
          nearbyList.push({
            id:
              `${element.type}-${element.id}`,
            name,
            coordinates: [
              Number(element.center.lat),
              Number(element.center.lon),
            ],
          });
        }
      }

      const uniqueRoads = [];
      const roadNames = new Set();

      for (const road of roadList) {
        if (roadNames.has(road.name)) continue;

        roadNames.add(road.name);
        uniqueRoads.push(road);
      }

      setRoads(
        uniqueRoads.slice(0, 50)
      );

      setNearby(
        nearbyList.slice(0, 30)
      );
    } catch {
      // Keep the map usable even if nearby enrichment fails.
    }
  }

  function choosePlace(selectedPlace) {
    setPlace(selectedPlace);
    setResults([]);
    setQuery(selectedPlace.name || "");
    setSelectedRoad(null);
    setExperiment(null);
    setResult(null);

    const detected =
      detectCategory(selectedPlace);

    if (detected) {
      setCategory(detected);
    }

    setScreen("place");

    loadNearby(selectedPlace);
  }

  function detectCategory(selectedPlace) {
    const text = `
      ${selectedPlace.name || ""}
      ${selectedPlace.type || ""}
      ${selectedPlace.address?.label || ""}
    `.toLowerCase();

    if (
      /hospital|clinic|medical|health|apollo|care/.test(
        text
      )
    ) {
      return "healthcare";
    }

    if (
      /school|college|university|academy|campus|library/.test(
        text
      )
    ) {
      return "education";
    }

    if (
      /airport|railway|station|metro|terminal|port/.test(
        text
      )
    ) {
      return "transport";
    }

    if (
      /mall|market|shopping|retail/.test(
        text
      )
    ) {
      return "commerce";
    }

    if (
      /theatre|theater|cinema|stadium|arena/.test(
        text
      )
    ) {
      return "entertainment";
    }

    return null;
  }

  async function runExperiment() {
    if (!place || !experiment) return;

    setRunning(true);
    setScreen("running");
    setError("");

    try {
      const response = await fetch(
        `${API_BASE}/simulate`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            project_id:
              "aegistwin-live",

            environment: {
              type:
                "real-world-place",

              place_name:
                place.name,

              address:
                place.address
                  ?.label || "",

              coordinates:
                place.position || [],

              selected_road:
                selectedRoad?.name ||
                null,

              mapped_roads:
                roads.slice(0, 20).map(
                  (road) => ({
                    name: road.name,
                    type: road.type,
                  })
                ),

              population_size:
                experiment.id ===
                "crowd"
                  ? 1000
                  : 500,
            },

            scenario: {
              name: experiment.title,
              hazard:
                "blocked_exit",
              blocked_nodes: [
                "staircase_a",
              ],
              start_time: 5,
            },

            interventions: [
              {
                type:
                  "flow_improvement",
                target:
                  "staircase_b->exit_b",
                multiplier:
                  0.75,
              },
            ],
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Experiment failed."
        );
      }

      await waitForRun();

      setScreen("result");
    } catch {
      setError(
        "The experiment could not be completed."
      );
      setScreen("place");
    } finally {
      setRunning(false);
    }
  }

  async function waitForRun() {
    for (let i = 0; i < 20; i++) {
      await new Promise(
        (resolve) =>
          setTimeout(resolve, 2000)
      );

      const response = await fetch(
        `${API_BASE}/runs`
      );

      const data =
        await response.json();

      if (
        Array.isArray(data.runs) &&
        data.runs.length
      ) {
        setResult(data.runs[0]);
        return;
      }
    }

    throw new Error(
      "Result timeout."
    );
  }

  function reset() {
    setScreen("home");
    setPlace(null);
    setResults([]);
    setQuery("");
    setCategory(null);
    setExperiment(null);
    setResult(null);
    setSelectedRoad(null);
    setRoads([]);
    setNearby([]);
  }

  const metrics = {
    average:
      result?.average_evacuation_time ??
      result?.metrics
        ?.average_evacuation_time ??
      "—",

    maximum:
      result?.maximum_evacuation_time ??
      result?.metrics
        ?.maximum_evacuation_time ??
      "—",

    completed:
      result?.completed ??
      result?.metrics?.completed ??
      "—",

    population:
      result?.population ??
      result?.metrics?.population ??
      "—",
  };

  const placeAddress =
    place?.address?.label ||
    [
      place?.address?.locality,
      place?.address?.region,
      place?.address?.country,
    ]
      .filter(Boolean)
      .join(", ");

  const currentExperiments =
    experiments[category] ||
    experiments.default;

  return (
    <div className="aegis">

      <style>{`
        /* GLOBAL RESET — fixes old Vite alignment */
        html,
        body,
        #root {
          width: 100% !important;
          min-width: 0 !important;
          min-height: 100% !important;
          margin: 0 !important;
          padding: 0 !important;
        }

        #root {
          max-width: none !important;
        }

        body {
          overflow-x: hidden;
          background: #f5f5f7;
        }

        * {
          box-sizing: border-box;
        }

        .aegis {
          width: 100%;
          min-height: 100vh;
          background: #f5f5f7;
          color: #1d1d1f;
          font-family:
            -apple-system,
            BlinkMacSystemFont,
            "SF Pro Display",
            "Segoe UI",
            sans-serif;
        }

        /* INTRO */

        .intro {
          position: fixed;
          inset: 0;
          z-index: 10000;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          background:
            radial-gradient(
              circle at center,
              #fff 0%,
              #f8f9fa 48%,
              #edf1f5 100%
            );
          transition:
            opacity 1s ease,
            visibility 1s ease;
        }

        .intro.off {
          opacity: 0;
          visibility: hidden;
          pointer-events: none;
        }

        .globe-stage {
          position: absolute;
          width: min(72vw, 650px);
          aspect-ratio: 1;
          border-radius: 50%;
        }

        .globe-ring {
          position: absolute;
          inset: 0;
          border-radius: 50%;
          border: 1px solid rgba(0,113,227,.10);
        }

        .globe-ring::before,
        .globe-ring::after {
          content: "";
          position: absolute;
          inset: 15%;
          border-radius: 50%;
          border: 1px solid rgba(0,113,227,.07);
        }

        .globe-ring::after {
          inset: 31%;
        }

        .globe-line-a,
        .globe-line-b {
          position: absolute;
          inset: 0;
          border: 1px solid rgba(0,113,227,.055);
          border-radius: 50%;
          transform: rotate(52deg);
        }

        .globe-line-b {
          transform: rotate(-52deg);
        }

        .globe-dot {
          position: absolute;
          left: var(--x);
          top: var(--y);
          width: 5px;
          height: 5px;
          margin-left: -2.5px;
          margin-top: -2.5px;
          border-radius: 50%;
          background: #0071e3;
          opacity: 0;
          transform:
            translate(var(--sx), var(--sy))
            scale(.15);
          animation:
            assemble 1.55s
            var(--delay)
            cubic-bezier(.16,1,.3,1)
            forwards;
        }

        .intro-core {
          position: relative;
          z-index: 3;
          text-align: center;
        }

        .intro-symbol {
          width: 72px;
          height: 72px;
          margin: 0 auto 28px;
          border-radius: 22px;
          display: grid;
          place-items: center;
          background: rgba(255,255,255,.86);
          border: 1px solid rgba(0,0,0,.07);
          box-shadow:
            0 25px 70px
              rgba(0,0,0,.08);
          opacity: 0;
          animation:
            symbolAppear .8s
            1.35s
            cubic-bezier(.16,1,.3,1)
            forwards;
        }

        .symbol-inner {
          width: 28px;
          height: 28px;
          border: 2px solid #1d1d1f;
          border-radius: 50%;
          position: relative;
        }

        .symbol-inner::before {
          content: "";
          position: absolute;
          inset: 5px;
          border: 1px solid #0071e3;
          border-radius: 50%;
        }

        .symbol-inner::after {
          content: "";
          position: absolute;
          inset: 10px;
          border-radius: 50%;
          background: #0071e3;
        }

        .intro-name {
          margin: 0;
          font-size:
            clamp(54px,8vw,92px);
          line-height: .95;
          letter-spacing: -.065em;
          font-weight: 700;
          opacity: 0;
          transform: translateY(20px);
          animation:
            titleAppear 1s
            1.55s
            cubic-bezier(.16,1,.3,1)
            forwards;
        }

        .intro-tagline {
          margin: 20px 0 0;
          color: #6e6e73;
          font-size:
            clamp(18px,2.4vw,28px);
          opacity: 0;
          transform: translateY(15px);
          animation:
            titleAppear .9s
            1.9s
            cubic-bezier(.16,1,.3,1)
            forwards;
        }

        /* NAV */

        .nav {
          height: 76px;
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 42px;
          background:
            rgba(255,255,255,.92);
          border-bottom:
            1px solid rgba(0,0,0,.055);
          backdrop-filter: blur(22px);
          position: relative;
          z-index: 100;
        }

        .brand {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 18px;
          font-weight: 650;
          white-space: nowrap;
        }

        .brand-dot {
          width: 9px;
          height: 9px;
          border-radius: 50%;
          background: #0071e3;
        }

        .nav-center {
          position: absolute;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          gap: 29px;
          color: #6e6e73;
          font-size: 13px;
        }

        .nav-item {
          cursor: pointer;
          white-space: nowrap;
        }

        .nav-right {
          color: #6e6e73;
          font-size: 12px;
        }

        /* HERO */

        .hero {
          width: 100%;
          min-height:
            calc(100vh - 76px);
          display: grid;
          grid-template-columns:
            minmax(440px,.82fr)
            minmax(0,1.18fr);
          padding: 24px;
          gap: 24px;
        }

        .hero-left {
          padding:
            8vw 3.5vw 8vw 5vw;
          display: flex;
          flex-direction: column;
          justify-content: center;
        }

        .eyebrow {
          font-size: 11px;
          font-weight: 700;
          letter-spacing: .1em;
          text-transform: uppercase;
          color: #0071e3;
        }

        .hero-title {
          margin: 16px 0 0;
          max-width: 700px;
          font-size:
            clamp(56px,6.4vw,90px);
          line-height: .96;
          letter-spacing: -.065em;
          font-weight: 700;
        }

        .hero-copy {
          max-width: 580px;
          margin-top: 25px;
          color: #6e6e73;
          font-size: 19px;
          line-height: 1.55;
        }

        .search-box {
          width: min(100%, 610px);
          margin-top: 34px;
          padding: 7px;
          display: flex;
          background: white;
          border:
            1px solid rgba(0,0,0,.07);
          border-radius: 19px;
          box-shadow:
            0 20px 55px
              rgba(0,0,0,.06);
        }

        .search-input {
          flex: 1;
          min-width: 0;
          height: 50px;
          border: 0;
          outline: 0;
          padding: 0 16px;
          background: transparent;
          font-family: inherit;
          font-size: 15px;
        }

        .search-button {
          min-width: 104px;
          height: 50px;
          border: 0;
          border-radius: 14px;
          background: #0071e3;
          color: white;
          font-family: inherit;
          font-size: 13px;
          font-weight: 650;
          cursor: pointer;
        }

        .results {
          width: min(100%,610px);
          margin-top: 10px;
          overflow: hidden;
          border-radius: 16px;
          background: rgba(255,255,255,.97);
          border:
            1px solid rgba(0,0,0,.07);
          box-shadow:
            0 25px 55px
              rgba(0,0,0,.1);
        }

        .result-item {
          width: 100%;
          display: block;
          padding: 15px 17px;
          border: 0;
          border-bottom:
            1px solid #efefef;
          background: white;
          text-align: left;
          cursor: pointer;
          font-family: inherit;
        }

        .result-item:hover {
          background: #f7f7f8;
        }

        .result-name {
          font-size: 13px;
          font-weight: 650;
        }

        .result-address {
          margin-top: 4px;
          color: #6e6e73;
          font-size: 11px;
        }

        .hero-map {
          position: relative;
          min-width: 0;
          min-height: 0;
          overflow: hidden;
          border-radius: 30px;
          background: #dce5e8;
          box-shadow:
            inset 0 0 0 1px
              rgba(0,0,0,.05);
        }

        .map {
          width: 100%;
          height: 100%;
        }

        .map-label {
          position: absolute;
          top: 22px;
          left: 22px;
          z-index: 500;
          padding: 11px 14px;
          border-radius: 13px;
          background:
            rgba(255,255,255,.91);
          border:
            1px solid rgba(0,0,0,.06);
          box-shadow:
            0 12px 30px
              rgba(0,0,0,.07);
          font-size: 12px;
          font-weight: 650;
          pointer-events: none;
        }

        .map-sub {
          position: absolute;
          right: 22px;
          top: 22px;
          z-index: 500;
          padding: 10px 13px;
          border-radius: 12px;
          background:
            rgba(255,255,255,.87);
          color: #6e6e73;
          font-size: 11px;
          pointer-events: none;
        }

        /* GLOBAL SECTIONS */

        .section {
          padding: 110px 7vw;
        }

        .section-heading {
          max-width: 800px;
          font-size:
            clamp(46px,5.2vw,76px);
          line-height: .98;
          letter-spacing: -.06em;
          margin: 0;
        }

        .section-copy {
          max-width: 650px;
          margin-top: 18px;
          color: #6e6e73;
          font-size: 18px;
          line-height: 1.55;
        }

        .category-grid {
          margin-top: 52px;
          display: grid;
          grid-template-columns:
            repeat(3,minmax(0,1fr));
          gap: 14px;
        }

        .category-card {
          min-height: 210px;
          padding: 26px;
          border: 0;
          border-radius: 23px;
          background: white;
          text-align: left;
          cursor: pointer;
          font-family: inherit;
          border:
            1px solid rgba(0,0,0,.055);
          transition:
            transform .22s ease,
            box-shadow .22s ease;
        }

        .category-card:hover {
          transform: translateY(-5px);
          box-shadow:
            0 25px 55px
              rgba(0,0,0,.07);
        }

        .category-icon {
          width: 42px;
          height: 42px;
          display: grid;
          place-items: center;
          border-radius: 13px;
          background: #f0f4f8;
          color: #0071e3;
          font-size: 18px;
        }

        .category-name {
          margin-top: 28px;
          font-size: 18px;
          font-weight: 700;
        }

        .category-description {
          margin-top: 7px;
          color: #6e6e73;
          font-size: 12px;
          line-height: 1.5;
        }

        .category-arrow {
          margin-top: 25px;
          color: #0071e3;
          font-size: 17px;
        }

        .dark-section {
          background: #111214;
          color: white;
        }

        .dark-section .section-copy {
          color: #a1a1a6;
        }

        /* PLACE */

        .place-layout {
          min-height:
            calc(100vh - 76px);
          display:
            grid;
          grid-template-columns:
            minmax(430px,.75fr)
            minmax(0,1.25fr);
        }

        .place-panel {
          padding: 48px;
          overflow-y: auto;
          background: #f5f5f7;
        }

        .back {
          height: 40px;
          padding: 0 13px;
          border: 0;
          border-radius: 11px;
          background: #e9e9eb;
          font-family: inherit;
          cursor: pointer;
          color: #3a3a3c;
        }

        .place-name {
          margin-top: 40px;
          font-size:
            clamp(44px,4.5vw,68px);
          line-height: 1;
          letter-spacing: -.055em;
        }

        .place-address {
          margin-top: 11px;
          color: #6e6e73;
          font-size: 14px;
          line-height: 1.5;
        }

        .place-info {
          margin-top: 28px;
          padding: 17px;
          background: white;
          border-radius: 16px;
          border:
            1px solid rgba(0,0,0,.06);
        }

        .mini-label {
          color: #0071e3;
          font-size: 9px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: .07em;
        }

        .mini-value {
          margin-top: 5px;
          font-size: 14px;
          font-weight: 650;
        }

        .experiment-heading {
          margin-top: 35px;
          font-size: 14px;
          font-weight: 650;
        }

        .experiment-grid {
          margin-top: 12px;
          display: grid;
          grid-template-columns:
            repeat(2,minmax(0,1fr));
          gap: 9px;
        }

        .experiment-card {
          padding: 15px;
          border:
            1px solid rgba(0,0,0,.07);
          border-radius: 15px;
          background: white;
          text-align: left;
          font-family: inherit;
          cursor: pointer;
        }

        .experiment-card.selected {
          border-color:
            rgba(0,113,227,.38);
          box-shadow:
            0 0 0 3px
              rgba(0,113,227,.07);
        }

        .experiment-title {
          font-size: 13px;
          font-weight: 650;
        }

        .experiment-copy {
          margin-top: 6px;
          color: #6e6e73;
          font-size: 10px;
          line-height: 1.45;
        }

        .run {
          width: 100%;
          height: 52px;
          margin-top: 13px;
          border: 0;
          border-radius: 14px;
          background: #0071e3;
          color: white;
          font-family: inherit;
          font-weight: 700;
          cursor: pointer;
        }

        /* RUNNING */

        .running {
          min-height:
            calc(100vh - 76px);
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
          padding: 50px;
        }

        .running-title {
          max-width: 900px;
          margin: 14px auto 0;
          font-size:
            clamp(54px,6vw,88px);
          line-height: .97;
          letter-spacing: -.06em;
        }

        .running-copy {
          max-width: 650px;
          margin: 20px auto 0;
          color: #6e6e73;
          font-size: 18px;
          line-height: 1.5;
        }

        .running-bar {
          width: 300px;
          height: 5px;
          margin: 35px auto 0;
          overflow: hidden;
          border-radius: 999px;
          background: #e7eaee;
        }

        .running-bar::before {
          content: "";
          display: block;
          width: 35%;
          height: 100%;
          background: #0071e3;
          animation:
            slide 1.2s
            infinite
            ease-in-out;
        }

        /* RESULT */

        .result {
          padding: 90px 8vw;
        }

        .result-title {
          max-width: 900px;
          margin-top: 16px;
          font-size:
            clamp(56px,6.5vw,94px);
          line-height: .96;
          letter-spacing: -.065em;
        }

        .result-copy {
          max-width: 720px;
          margin-top: 20px;
          color: #6e6e73;
          font-size: 19px;
          line-height: 1.55;
        }

        .result-grid {
          max-width: 900px;
          margin-top: 42px;
          display:
            grid;
          grid-template-columns:
            repeat(2,minmax(0,1fr));
          gap: 14px;
        }

        .result-card {
          padding: 28px;
          background: white;
          border-radius: 20px;
          border:
            1px solid rgba(0,0,0,.06);
        }

        .result-card.highlight {
          border-color:
            rgba(0,113,227,.22);
          box-shadow:
            0 20px 45px
              rgba(0,113,227,.06);
        }

        .result-label {
          color: #86868b;
          font-size: 9px;
          text-transform: uppercase;
          letter-spacing: .07em;
        }

        .result-heading {
          margin-top: 6px;
          font-size: 17px;
          font-weight: 700;
        }

        .result-number {
          margin-top: 22px;
          font-size: 46px;
          line-height: 1;
          letter-spacing: -.04em;
          font-weight: 700;
        }

        .result-unit {
          margin-top: 5px;
          color: #86868b;
          font-size: 10px;
        }

        .result-metrics {
          max-width: 900px;
          margin-top: 12px;
          display: grid;
          grid-template-columns:
            repeat(4,minmax(0,1fr));
          gap: 9px;
        }

        .metric {
          padding: 15px;
          background: white;
          border-radius: 13px;
        }

        .metric-label {
          color: #86868b;
          font-size: 8px;
          text-transform: uppercase;
          letter-spacing: .05em;
        }

        .metric-value {
          margin-top: 5px;
          font-size: 19px;
          font-weight: 700;
        }

        .result-note {
          max-width: 900px;
          margin-top: 18px;
          padding: 15px;
          border-radius: 13px;
          background: #edf5ff;
          color: #546575;
          font-size: 11px;
          line-height: 1.5;
        }

        /* MAP */

        .side-map {
          position: relative;
          min-height: 100%;
        }

        .side-map .map {
          width: 100%;
          height: 100%;
        }

        .map-caption {
          position: absolute;
          left: 22px;
          top: 22px;
          z-index: 500;
          padding: 11px 14px;
          border-radius: 13px;
          background:
            rgba(255,255,255,.9);
          border:
            1px solid rgba(0,0,0,.06);
          box-shadow:
            0 12px 28px
              rgba(0,0,0,.07);
          font-size: 12px;
          font-weight: 650;
          pointer-events: none;
        }

        @keyframes assemble {
          0% {
            opacity: 0;
            transform:
              translate(var(--sx),var(--sy))
              scale(.15);
          }

          65% {
            opacity: 1;
          }

          100% {
            opacity: 1;
            transform:
              translate(0,0)
              scale(1);
          }
        }

        @keyframes symbolAppear {
          from {
            opacity: 0;
            transform: scale(.6);
          }

          to {
            opacity: 1;
            transform: scale(1);
          }
        }

        @keyframes titleAppear {
          from {
            opacity: 0;
            transform:
              translateY(22px)
              scale(.97);
          }

          to {
            opacity: 1;
            transform:
              translateY(0)
              scale(1);
          }
        }

        @keyframes slide {
          from {
            transform: translateX(-140%);
          }

          to {
            transform: translateX(330%);
          }
        }

        @media (max-width: 1050px) {
          .hero,
          .place-layout {
            grid-template-columns: 1fr;
          }

          .hero-map {
            min-height: 520px;
          }

          .place-panel {
            min-height: auto;
          }

          .category-grid {
            grid-template-columns:
              repeat(2,minmax(0,1fr));
          }
        }

        @media (max-width: 700px) {
          .nav {
            padding: 0 18px;
          }

          .nav-center {
            display: none;
          }

          .nav-right {
            display: none;
          }

          .hero {
            padding: 10px;
            gap: 10px;
          }

          .hero-left {
            padding:
              65px 25px;
          }

          .section,
          .result {
            padding:
              70px 24px;
          }

          .category-grid,
          .experiment-grid,
          .result-grid {
            grid-template-columns: 1fr;
          }

          .result-metrics {
            grid-template-columns:
              repeat(2,1fr);
          }

          .place-panel {
            padding: 28px 22px;
          }

          .running {
            padding: 30px 20px;
          }
        }
      `}</style>

      {/* OPENING */}

      <div
        className={`intro ${
          intro ? "" : "off"
        }`}
      >
        <div className="globe-stage">
          <div className="globe-ring" />
          <div className="globe-line-a" />
          <div className="globe-line-b" />

          {introDots.map(
            (
              dot,
              index
            ) => (
              <span
                key={index}
                className="globe-dot"
                style={{
                  "--x": dot[0],
                  "--y": dot[1],
                  "--sx": dot[2],
                  "--sy": dot[3],
                  "--delay": dot[4],
                }}
              />
            )
          )}
        </div>

        <div className="intro-core">
          <div className="intro-symbol">
            <div className="symbol-inner" />
          </div>

          <h1 className="intro-name">
            AegisTwin
          </h1>

          <p className="intro-tagline">
            Test emergencies before they happen.
          </p>
        </div>
      </div>

      {/* NAV */}

      <header className="nav">

        <div className="brand">
          <span className="brand-dot" />
          AegisTwin
        </div>

        <nav className="nav-center">
          <span
            className="nav-item"
            onClick={() =>
              setScreen("home")
            }
          >
            Explore
          </span>

          <span
            className="nav-item"
            onClick={() =>
              document
                .getElementById(
                  "places"
                )
                ?.scrollIntoView({
                  behavior:
                    "smooth",
                })
            }
          >
            Places
          </span>

          <span className="nav-item">
            Experiments
          </span>

          <span className="nav-item">
            Global map
          </span>
        </nav>

        <div className="nav-right">
          Global emergency intelligence
        </div>

      </header>

      {/* HOME */}

      {screen === "home" && (
        <>
          <section className="hero">

            <div className="hero-left">

              <div className="eyebrow">
                Global emergency intelligence
              </div>

              <h1 className="hero-title">
                What could happen here?
              </h1>

              <p className="hero-copy">
                Explore real places around the world,
                understand what surrounds them, and
                test emergency situations before they happen.
              </p>

              <form
                className="search-box"
                onSubmit={(event) => {
                  event.preventDefault();
                  searchPlace();
                }}
              >
                <input
                  className="search-input"
                  value={query}
                  onChange={(event) => {
                    setQuery(
                      event.target.value
                    );
                    setError("");
                  }}
                  placeholder="Search a school, hospital, airport, mall..."
                />

                <button
                  className="search-button"
                  type="submit"
                >
                  {searching
                    ? "Searching"
                    : "Explore"}
                </button>
              </form>

              {results.length > 0 && (
                <div className="results">
                  {results.map(
                    (item) => (
                      <button
                        key={
                          item.place_id
                        }
                        className="result-item"
                        onClick={() =>
                          choosePlace(
                            item
                          )
                        }
                      >
                        <div className="result-name">
                          {
                            item.name
                          }
                        </div>

                        <div className="result-address">
                          {item.address?.label ||
                            ""}
                        </div>
                      </button>
                    )
                  )}
                </div>
              )}

              {error && (
                <div
                  style={{
                    marginTop: 10,
                    color: "#9b3d35",
                    fontSize: 12,
                  }}
                >
                  {error}
                </div>
              )}

            </div>

            <div className="hero-map">

              <MapContainer
                className="map"
                center={[20, 0]}
                zoom={2}
                minZoom={2}
                maxZoom={18}
                worldCopyJump
              >

                <TileLayer
                  attribution="&copy; OpenStreetMap contributors"
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <CenterTracker
                  setCenter={setCenter}
                />

                <FlyToPlace
                  place={place}
                />

              </MapContainer>

              <div className="map-label">
                Explore the world
              </div>

              <div className="map-sub">
                Pan · Zoom · Search
              </div>

            </div>

          </section>

          <section
            className="section"
            id="places"
          >

            <div className="eyebrow">
              Explore every kind of place
            </div>

            <h2 className="section-heading">
              The world is not one environment.
            </h2>

            <p className="section-copy">
              Hospitals behave differently from universities.
              Airports behave differently from malls. AegisTwin
              lets the experience change with the place.
            </p>

            <div className="category-grid">
              {categories.map(
                (item) => (
                  <button
                    key={item[0]}
                    className="category-card"
                    onClick={() => {
                      setCategory(
                        item[0]
                      );
                      setQuery("");
                      window.scrollTo({
                        top: 0,
                        behavior:
                          "smooth",
                      });
                    }}
                  >
                    <div>
                      <div className="category-icon">
                        {item[3]}
                      </div>

                      <div className="category-name">
                        {item[1]}
                      </div>

                      <div className="category-description">
                        {item[2]}
                      </div>
                    </div>

                    <div className="category-arrow">
                      →
                    </div>
                  </button>
                )
              )}
            </div>

          </section>

          {category && (
            <section
              className="section dark-section"
            >

              <div className="eyebrow">
                {categories.find(
                  (x) =>
                    x[0] === category
                )?.[1] ||
                  "Explore"}
              </div>

              <h2 className="section-heading">
                Choose a real place.
              </h2>

              <p className="section-copy">
                Search anywhere in the world and AegisTwin
                will build the experience around that location.
              </p>

              <form
                className="search-box"
                style={{
                  marginTop: 35,
                  maxWidth: 650,
                }}
                onSubmit={(event) => {
                  event.preventDefault();
                  searchPlace();
                }}
              >
                <input
                  className="search-input"
                  value={query}
                  onChange={(event) =>
                    setQuery(
                      event.target.value
                    )
                  }
                  placeholder="Search a real location..."
                />

                <button
                  className="search-button"
                  type="submit"
                >
                  Search
                </button>
              </form>

              {results.length > 0 && (
                <div
                  className="results"
                  style={{
                    maxWidth: 650,
                  }}
                >
                  {results.map(
                    (item) => (
                      <button
                        key={
                          item.place_id
                        }
                        className="result-item"
                        onClick={() =>
                          choosePlace(
                            item
                          )
                        }
                      >
                        <div className="result-name">
                          {
                            item.name
                          }
                        </div>

                        <div className="result-address">
                          {
                            item.address
                              ?.label
                          }
                        </div>
                      </button>
                    )
                  )}
                </div>
              )}

            </section>
          )}
        </>
      )}

      {/* PLACE */}

      {screen === "place" &&
        place && (
          <section className="place-layout">

            <div className="place-panel">

              <button
                className="back"
                onClick={reset}
              >
                ← Explore another place
              </button>

              <div
                className="eyebrow"
                style={{
                  marginTop: 35,
                }}
              >
                Real place
              </div>

              <h1 className="place-name">
                {place.name}
              </h1>

              <div className="place-address">
                {placeAddress}
              </div>

              <div className="place-info">

                <div className="mini-label">
                  AegisTwin context
                </div>

                <div className="mini-value">
                  {categories.find(
                    (x) =>
                      x[0] ===
                      category
                  )?.[1] ||
                    "Global place"}
                </div>

                <div
                  style={{
                    marginTop: 6,
                    color:
                      "#6e6e73",
                    fontSize: 11,
                    lineHeight:
                      1.5,
                  }}
                >
                  Real geographic information is used for
                  context. Simulation results remain clearly
                  separated from mapped facts.
                </div>

              </div>

              {selectedRoad && (
                <div
                  className="place-info"
                  style={{
                    background:
                      "#edf5ff",
                  }}
                >
                  <div className="mini-label">
                    Selected mapped route
                  </div>

                  <div className="mini-value">
                    {selectedRoad.name}
                  </div>
                </div>
              )}

              <div className="experiment-heading">
                What do you want to understand?
              </div>

              <div className="experiment-grid">

                {(
                  experiments[
                    category
                  ] ||
                  experiments.default
                ).map(
                  (item) => (
                    <button
                      key={
                        item[0]
                      }
                      className={`experiment-card ${
                        experiment?.id ===
                        item[0]
                          ? "selected"
                          : ""
                      }`}
                      onClick={() =>
                        setExperiment({
                          id:
                            item[0],
                          title:
                            item[1],
                          description:
                            item[2],
                        })
                      }
                    >
                      <div className="experiment-title">
                        {item[1]}
                      </div>

                      <div className="experiment-copy">
                        {item[2]}
                      </div>
                    </button>
                  )
                )}

              </div>

              {experiment && (
                <button
                  className="run"
                  onClick={
                    runExperiment
                  }
                >
                  Test this situation
                </button>
              )}

            </div>

            <div className="side-map">

              <MapContainer
                className="map"
                center={[
                  Number(
                    place.position?.[1] ||
                      20
                  ),
                  Number(
                    place.position?.[0] ||
                      0
                  ),
                ]}
                zoom={16}
                maxZoom={19}
              >

                <TileLayer
                  attribution="&copy; OpenStreetMap contributors"
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <FlyToPlace
                  place={place}
                />

                {roads.map(
                  (road) => (
                    <Polyline
                      key={
                        road.id
                      }
                      positions={
                        road.coordinates
                      }
                      pathOptions={{
                        color:
                          selectedRoad?.id ===
                          road.id
                            ? "#0071e3"
                            : "#727880",
                        weight:
                          selectedRoad?.id ===
                          road.id
                            ? 7
                            : 3,
                        opacity:
                          selectedRoad?.id ===
                          road.id
                            ? .95
                            : .55,
                      }}
                      eventHandlers={{
                        click: () =>
                          setSelectedRoad(
                            road
                          ),
                      }}
                    />
                  )
                )}

                <CircleMarker
                  center={[
                    Number(
                      place.position?.[1] ||
                        20
                    ),
                    Number(
                      place.position?.[0] ||
                        0
                    ),
                  ]}
                  radius={11}
                  pathOptions={{
                    color:
                      "#ffffff",
                    fillColor:
                      "#0071e3",
                    fillOpacity:
                      .95,
                    weight: 4,
                  }}
                />

                {nearby.map(
                  (item) => (
                    <CircleMarker
                      key={
                        item.id
                      }
                      center={
                        item.coordinates
                      }
                      radius={4}
                      pathOptions={{
                        color:
                          "#6e6e73",
                        fillColor:
                          "#ffffff",
                        fillOpacity:
                          .85,
                        weight: 1,
                      }}
                    />
                  )
                )}

              </MapContainer>

              <div className="map-caption">
                Real mapped area
              </div>

            </div>

          </section>
        )}

      {/* RUNNING */}

      {screen === "running" && (
        <section className="running">

          <div>

            <div className="eyebrow">
              AegisTwin experiment
            </div>

            <h1 className="running-title">
              Testing what could happen.
            </h1>

            <p className="running-copy">
              AegisTwin is running the selected emergency
              situation for {place?.name}.
            </p>

            <div className="running-bar" />

            <div
              style={{
                marginTop: 22,
                color: "#86868b",
                fontSize: 12,
              }}
            >
              Real place → scenario → simulation → explanation
            </div>

          </div>

        </section>
      )}

      {/* RESULT */}

      {screen === "result" &&
        result && (
          <section className="result">

            <div className="eyebrow">
              Experiment complete
            </div>

            <h1 className="result-title">
              Here’s what happened.
            </h1>

            <p className="result-copy">
              AegisTwin tested{" "}
              <strong>
                {experiment?.title}
              </strong>{" "}
              at{" "}
              <strong>
                {place?.name}
              </strong>
              .
            </p>

            <div className="result-grid">

              <div className="result-card">
                <div className="result-label">
                  Simulation result
                </div>

                <div className="result-heading">
                  Average movement time
                </div>

                <div className="result-number">
                  {metrics.average}
                </div>

                <div className="result-unit">
                  simulated seconds
                </div>
              </div>

              <div className="result-card highlight">
                <div className="result-label">
                  What changed
                </div>

                <div className="result-heading">
                  People completed
                </div>

                <div className="result-number">
                  {metrics.completed}
                </div>

                <div className="result-unit">
                  out of {metrics.population}
                </div>
              </div>

            </div>

            <div className="result-metrics">

              <div className="metric">
                <div className="metric-label">
                  Longest
                </div>

                <div className="metric-value">
                  {metrics.maximum}
                </div>
              </div>

              <div className="metric">
                <div className="metric-label">
                  People
                </div>

                <div className="metric-value">
                  {metrics.population}
                </div>
              </div>

              <div className="metric">
                <div className="metric-label">
                  Completed
                </div>

                <div className="metric-value">
                  {metrics.completed}
                </div>
              </div>

              <div className="metric">
                <div className="metric-label">
                  Status
                </div>

                <div className="metric-value">
                  Complete
                </div>
              </div>

            </div>

            <div className="result-note">
              Real geographic data provides the context for the
              selected place. Emergency movement is produced by
              the current AegisTwin simulation prototype and is
              not a validated prediction of the real location.
            </div>

            <button
              className="back"
              style={{
                marginTop: 22,
              }}
              onClick={() =>
                setScreen("place")
              }
            >
              ← Test another situation
            </button>

          </section>
        )}
    </div>
  );
}

export default App;