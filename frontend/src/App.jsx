import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  ArrowUpRight,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Cloud,
  Database,
  Factory,
  Globe2,
  GraduationCap,
  HeartPulse,
  House,
  Landmark,
  Map,
  MapPin,
  Plane,
  RotateCcw,
  Route,
  Search,
  Server,
  ShieldCheck,
  ShoppingBag,
  Trees,
  Users,
} from "lucide-react";
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
  {
    id: "healthcare",
    name: "Healthcare",
    description: "Hospitals, clinics & medical centers",
    icon: HeartPulse,
  },
  {
    id: "education",
    name: "Education",
    description: "Schools, colleges & universities",
    icon: GraduationCap,
  },
  {
    id: "transport",
    name: "Transport",
    description: "Airports, railway & transit",
    icon: Plane,
  },
  {
    id: "commerce",
    name: "Commerce",
    description: "Malls, markets & business areas",
    icon: ShoppingBag,
  },
  {
    id: "entertainment",
    name: "Entertainment",
    description: "Theatres, stadiums & venues",
    icon: Activity,
  },
  {
    id: "public",
    name: "Public & Government",
    description: "Civic buildings & public services",
    icon: Landmark,
  },
  {
    id: "hospitality",
    name: "Hospitality",
    description: "Hotels, resorts & restaurants",
    icon: Cloud,
  },
  {
    id: "residential",
    name: "Residential",
    description: "Neighbourhoods & communities",
    icon: House,
  },
  {
    id: "infrastructure",
    name: "Infrastructure",
    description: "Utilities, industry & facilities",
    icon: Factory,
  },
  {
    id: "tourism",
    name: "Tourism & Public Spaces",
    description: "Parks, museums & landmarks",
    icon: Trees,
  },
  {
    id: "sports",
    name: "Sports",
    description: "Stadiums & sports complexes",
    icon: Activity,
  },
  {
    id: "community",
    name: "Community",
    description: "Community & gathering spaces",
    icon: Users,
  },
];

const experiments = {
  healthcare: [
    {
      id: "medical_access",
      title: "Emergency access changes",
      description:
        "Explore how access could change around a medical facility.",
    },
    {
      id: "evacuation",
      title: "People need to leave",
      description:
        "Explore movement when people need to leave quickly.",
    },
    {
      id: "crowd",
      title: "More people arrive",
      description:
        "Explore what happens when arrivals increase.",
    },
    {
      id: "road",
      title: "An access road closes",
      description:
        "See how a road closure could affect access.",
    },
  ],

  education: [
    {
      id: "evacuation",
      title: "People need to leave",
      description:
        "Explore how a large group could move out quickly.",
    },
    {
      id: "entrance",
      title: "An entrance becomes unavailable",
      description:
        "See how movement changes when an access point closes.",
    },
    {
      id: "crowd",
      title: "A crowd suddenly grows",
      description:
        "Explore movement when more people arrive.",
    },
    {
      id: "road",
      title: "A road becomes unavailable",
      description:
        "See how surrounding access could change.",
    },
  ],

  transport: [
    {
      id: "road",
      title: "An access route closes",
      description:
        "Explore how people could reach or leave the transport hub.",
    },
    {
      id: "crowd",
      title: "Passenger numbers increase",
      description:
        "Explore movement when the crowd becomes larger.",
    },
    {
      id: "evacuation",
      title: "People need to leave",
      description:
        "Explore movement during an emergency.",
    },
    {
      id: "access",
      title: "Emergency access changes",
      description:
        "See how emergency response access could change.",
    },
  ],

  commerce: [
    {
      id: "evacuation",
      title: "People need to leave",
      description:
        "Explore how a large visitor group could leave.",
    },
    {
      id: "entrance",
      title: "An entrance becomes unavailable",
      description:
        "See how access changes when an entrance closes.",
    },
    {
      id: "crowd",
      title: "Visitor numbers increase",
      description:
        "Explore movement with more visitors.",
    },
    {
      id: "road",
      title: "A surrounding road closes",
      description:
        "See how access to the area could change.",
    },
  ],

  entertainment: [
    {
      id: "evacuation",
      title: "Everyone needs to leave",
      description:
        "Explore how a large crowd could leave quickly.",
    },
    {
      id: "entrance",
      title: "An entrance becomes unavailable",
      description:
        "See how movement changes when access is reduced.",
    },
    {
      id: "crowd",
      title: "The crowd grows",
      description:
        "Explore what happens when more visitors arrive.",
    },
    {
      id: "road",
      title: "An access road closes",
      description:
        "See how surrounding movement could change.",
    },
  ],

  default: [
    {
      id: "evacuation",
      title: "People need to leave",
      description:
        "Explore movement when people need to leave quickly.",
    },
    {
      id: "road",
      title: "A road becomes unavailable",
      description:
        "See how access could change when a route closes.",
    },
    {
      id: "crowd",
      title: "More people arrive",
      description:
        "Explore how the area responds to a larger crowd.",
    },
    {
      id: "access",
      title: "Emergency access changes",
      description:
        "Explore how emergency access could change.",
    },
  ],
};

const introDots = [
  ["18%", "25%", "-210px", "-110px", "0s"],
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

const awsArchitecture = [
  {
    name: "React Web App",
    detail: "Interactive product experience",
    icon: Globe2,
  },
  {
    name: "Amazon Location",
    detail: "Real place & geographic context",
    icon: Map,
  },
  {
    name: "API Gateway",
    detail: "Public API entry point",
    icon: Route,
  },
  {
    name: "AWS Lambda",
    detail: "API & simulation processing",
    icon: Server,
  },
  {
    name: "Amazon SQS",
    detail: "Asynchronous simulation jobs",
    icon: Activity,
  },
  {
    name: "DynamoDB",
    detail: "Run results & state",
    icon: Database,
  },
  {
    name: "CloudWatch",
    detail: "Operational logs",
    icon: ShieldCheck,
  },
];

function FlyToPlace({ place }) {
  const map = useMap();

  useEffect(() => {
    if (!place?.position) return;

    const [lng, lat] = place.position;

    if (!Number.isFinite(Number(lat))) return;
    if (!Number.isFinite(Number(lng))) return;

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
      const center = event.target.getCenter();
      setCenter([center.lat, center.lng]);
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

  const [center, setCenter] = useState([20, 0]);

  const [place, setPlace] = useState(null);
  const [roads, setRoads] = useState([]);
  const [nearby, setNearby] = useState([]);
  const [selectedRoad, setSelectedRoad] = useState(null);

  const [experiment, setExperiment] = useState(null);
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);

  const [error, setError] = useState("");

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setIntro(false);
    }, 3100);

    return () => window.clearTimeout(timer);
  }, []);

  const selectedCategory = useMemo(
    () =>
      categories.find(
        (item) => item.id === category
      ),
    [category]
  );

  const currentExperiments =
    experiments[category] || experiments.default;

  function scrollToId(id) {
    window.requestAnimationFrame(() => {
      document
        .getElementById(id)
        ?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
    });
  }

  function chooseCategory(id) {
    setCategory(id);
    setExperiment(null);
    setError("");
    scrollToId("search-area");
  }

  async function searchPlace() {
    const trimmed = query.trim();

    if (!trimmed) {
      setError(
        "Enter a real place, address, school, hospital, airport or landmark."
      );
      return;
    }

    setSearching(true);
    setResults([]);
    setError("");

    try {
      const [lat, lng] = center;

      const response = await fetch(
        `${API_BASE}/places/search?q=${encodeURIComponent(
          trimmed
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

      const places = Array.isArray(data.places)
        ? data.places
        : [];

      if (!places.length) {
        setError(
          "No matching place was found. Try a more specific name."
        );
      }

      setResults(places);
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

    const [lng, lat] = selectedPlace.position;

    if (
      !Number.isFinite(Number(lat)) ||
      !Number.isFinite(Number(lng))
    ) {
      return;
    }

    try {
      const queryText = `
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
          body: `data=${encodeURIComponent(
            queryText
          )}`,
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
              tags.name || "Unnamed road",
            type: tags.highway,
            coordinates:
              element.geometry.map((point) => [
                Number(point.lat),
                Number(point.lon),
              ]),
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

        let coordinates = null;

        if (
          Number.isFinite(Number(element.lat)) &&
          Number.isFinite(Number(element.lon))
        ) {
          coordinates = [
            Number(element.lat),
            Number(element.lon),
          ];
        } else if (element.center) {
          coordinates = [
            Number(element.center.lat),
            Number(element.center.lon),
          ];
        }

        if (name && coordinates) {
          nearbyList.push({
            id: `${element.type}-${element.id}`,
            name,
            coordinates,
          });
        }
      }

      const uniqueRoads = [];
      const roadNames = new Set();

      for (const road of roadList) {
        const normalized = road.name
          .trim()
          .toLowerCase();

        if (roadNames.has(normalized)) {
          continue;
        }

        roadNames.add(normalized);
        uniqueRoads.push(road);
      }

      setRoads(uniqueRoads.slice(0, 50));
      setNearby(nearbyList.slice(0, 35));
    } catch {
      // Geographic enrichment is optional.
      // The selected place remains usable.
    }
  }

  function detectCategory(selectedPlace) {
    const text = `
      ${selectedPlace?.name || ""}
      ${selectedPlace?.type || ""}
      ${selectedPlace?.address?.label || ""}
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
      /mall|market|shopping|retail/.test(text)
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

  function choosePlace(selectedPlace) {
    const detectedCategory =
      detectCategory(selectedPlace);

    setPlace(selectedPlace);
    setResults([]);
    setQuery(selectedPlace.name || "");
    setSelectedRoad(null);
    setExperiment(null);
    setResult(null);
    setError("");

    if (detectedCategory) {
      setCategory(detectedCategory);
    }

    setScreen("place");

    loadNearby(selectedPlace);
  }

  async function runExperiment() {
    if (!place || !experiment) return;

    setRunning(true);
    setScreen("running");
    setError("");
    setResult(null);

    try {
      const populationSize =
        experiment.id === "crowd"
          ? 1000
          : 500;

      const response = await fetch(
        `${API_BASE}/simulate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            project_id: "aegistwin-live",

            environment: {
              type: "real-world-place",

              place_name:
                place.name || "",

              address:
                place.address?.label || "",

              coordinates:
                place.position || [],

              selected_road:
                selectedRoad?.name || null,

              mapped_roads:
                roads.slice(0, 20).map(
                  (road) => ({
                    name: road.name,
                    type: road.type,
                  })
                ),

              population_size:
                populationSize,
            },

            scenario: {
              name: experiment.title,
              hazard: "blocked_exit",
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
                multiplier: 0.75,
              },
            ],
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "The simulation request failed."
        );
      }

      await waitForRun();

      setScreen("result");
    } catch {
      setError(
        "The experiment could not be completed. Please try again."
      );
      setScreen("place");
    } finally {
      setRunning(false);
    }
  }

  async function waitForRun() {
    for (let attempt = 0; attempt < 20; attempt += 1) {
      await new Promise((resolve) =>
        window.setTimeout(resolve, 2000)
      );

      const response = await fetch(
        `${API_BASE}/runs`
      );

      if (!response.ok) {
        continue;
      }

      const data = await response.json();

      if (
        Array.isArray(data.runs) &&
        data.runs.length
      ) {
        setResult(data.runs[0]);
        return;
      }
    }

    throw new Error(
      "The simulation result timed out."
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
    setError("");

    window.setTimeout(() => {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    }, 50);
  }

  const metrics = {
    average:
      result?.average_evacuation_time ??
      result?.metrics
        ?.average_evacuation_time ??
      null,

    maximum:
      result?.maximum_evacuation_time ??
      result?.metrics
        ?.maximum_evacuation_time ??
      null,

    minimum:
      result?.minimum_evacuation_time ??
      result?.metrics
        ?.minimum_evacuation_time ??
      null,

    completed:
      result?.completed ??
      result?.metrics?.completed ??
      null,

    failed:
      result?.failed ??
      result?.metrics?.failed ??
      0,

    remaining:
      result?.remaining ??
      result?.metrics?.remaining ??
      0,

    population:
      result?.population ??
      result?.metrics?.population ??
      null,

    reroutes:
      result?.reroute_count ??
      result?.metrics?.reroutes ??
      null,

    completionRate:
      result?.completion_rate ??
      result?.metrics?.completion_rate ??
      null,

    simulationTime:
      result?.simulation_time ??
      result?.metrics?.simulation_duration ??
      null,
  };

  const normalizedCompletionRate =
    typeof metrics.completionRate === "number"
      ? metrics.completionRate <= 1
        ? metrics.completionRate * 100
        : metrics.completionRate
      : metrics.completed != null &&
          metrics.population
        ? (Number(metrics.completed) /
            Number(metrics.population)) *
          100
        : null;

  const placeAddress =
    place?.address?.label ||
    [
      place?.address?.locality,
      place?.address?.region,
      place?.address?.country,
    ]
      .filter(Boolean)
      .join(", ");

  const outcomeComplete =
    metrics.completed != null &&
    metrics.population != null &&
    Number(metrics.completed) ===
      Number(metrics.population) &&
    Number(metrics.failed || 0) === 0 &&
    Number(metrics.remaining || 0) === 0;

  const resultHeadline =
    outcomeComplete
      ? "The simulated population completed the run."
      : "The simulation ended with measurable constraints.";

  const resultExplanation =
    outcomeComplete
      ? "Every modeled person reached a completion state in this run. Movement time is the primary response metric shown here."
      : "The run exposes where simulated movement did not complete. Completion, failure, remaining population and movement time describe the outcome.";

  return (
    <div className="aegis">
      <div
        className={`intro ${intro ? "" : "intro-off"}`}
      >
        <div className="globe-stage">
          <div className="globe-ring" />
          <div className="globe-line globe-line-a" />
          <div className="globe-line globe-line-b" />

          {introDots.map((dot, index) => (
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
          ))}
        </div>

        <div className="intro-core">
          <div className="intro-symbol">
            <div className="symbol-inner" />
          </div>

          <h1>AegisTwin</h1>

          <p>
            Test emergencies before they happen.
          </p>
        </div>
      </div>

      {screen === "home" && (
        <>
          <header className="nav">
            <button
              className="brand"
              onClick={reset}
              aria-label="AegisTwin home"
            >
              <span className="brand-mark">
                <span />
              </span>

              <span>AegisTwin</span>
            </button>

            <nav className="nav-links">
              <button
                onClick={() =>
                  scrollToId("places")
                }
              >
                Explore
              </button>

              <button
                onClick={() =>
                  scrollToId("search-area")
                }
              >
                Places
              </button>

              <button
                onClick={() =>
                  scrollToId("architecture")
                }
              >
                Architecture
              </button>
            </nav>

            <button
              className="nav-action"
              onClick={() =>
                scrollToId("search-area")
              }
            >
              Start exploring
              <ArrowUpRight size={15} />
            </button>
          </header>

          <main>
            <section className="hero">
              <div className="hero-copy">
                <div className="eyebrow">
                  GLOBAL EMERGENCY INTELLIGENCE
                </div>

                <h1>
                  What could happen
                  <br />
                  <span>here?</span>
                </h1>

                <p className="hero-subtitle">
                  Explore real places, introduce a
                  hypothetical emergency and understand
                  what a simulated response looks like.
                </p>

                <div
                  className="search-shell"
                  id="search-area"
                >
                  <div className="search-icon">
                    <Search size={19} />
                  </div>

                  <input
                    value={query}
                    onChange={(event) => {
                      setQuery(event.target.value);
                      setError("");
                    }}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        event.preventDefault();
                        searchPlace();
                      }
                    }}
                    placeholder={
                      selectedCategory
                        ? `Search a ${selectedCategory.name.toLowerCase()} location...`
                        : "Search a school, hospital, airport, mall..."
                    }
                    aria-label="Search a real place"
                  />

                  <button
                    onClick={searchPlace}
                    disabled={searching}
                  >
                    {searching
                      ? "Searching..."
                      : "Search"}
                  </button>
                </div>

                {selectedCategory && (
                  <div className="selected-context">
                    <span className="selected-dot" />
                    <strong>
                      {selectedCategory.name}
                    </strong>
                    <span>
                      category selected
                    </span>

                    <button
                      onClick={() => {
                        setCategory(null);
                        setQuery("");
                      }}
                    >
                      Clear
                    </button>
                  </div>
                )}

                {results.length > 0 && (
                  <div className="search-results">
                    <div className="search-results-head">
                      <span>
                        Real places found
                      </span>
                      <span>
                        {results.length}
                      </span>
                    </div>

                    {results.map((item) => (
                      <button
                        key={
                          item.place_id ||
                          `${item.name}-${item.position?.join("-")}`
                        }
                        className="search-result"
                        onClick={() =>
                          choosePlace(item)
                        }
                      >
                        <div className="result-pin">
                          <MapPin size={17} />
                        </div>

                        <div className="result-main">
                          <strong>
                            {item.name}
                          </strong>

                          <span>
                            {item.address?.label ||
                              "Location details unavailable"}
                          </span>
                        </div>

                        <ChevronRight
                          size={18}
                        />
                      </button>
                    ))}
                  </div>
                )}

                {error && (
                  <div className="inline-error">
                    <AlertTriangle size={15} />
                    <span>{error}</span>
                  </div>
                )}

                <div className="hero-proof">
                  <div>
                    <CheckCircle2 size={16} />
                    <span>
                      Real place search
                    </span>
                  </div>

                  <div>
                    <CheckCircle2 size={16} />
                    <span>
                      AWS-powered simulation
                    </span>
                  </div>

                  <div>
                    <CheckCircle2 size={16} />
                    <span>
                      Explainable outcomes
                    </span>
                  </div>
                </div>
              </div>

              <div className="hero-map-wrap">
                <MapContainer
                  className="map"
                  center={[20, 0]}
                  zoom={2}
                  minZoom={2}
                  maxZoom={18}
                  worldCopyJump
                  scrollWheelZoom
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

                <div className="map-overlay map-overlay-top">
                  <span>REAL WORLD CONTEXT</span>
                  <strong>
                    Explore anywhere
                  </strong>
                </div>

                <div className="map-overlay map-overlay-bottom">
                  <MapPin size={14} />
                  Pan · zoom · search
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

              <div className="section-heading-row">
                <div>
                  <h2 className="section-heading">
                    The world is not one
                    environment.
                  </h2>

                  <p className="section-copy">
                    Hospitals behave differently from
                    universities. Airports behave
                    differently from malls. AegisTwin
                    changes the exploration around the
                    type of place you choose.
                  </p>
                </div>

                {category && (
                  <div className="selection-pill">
                    <span />
                    {
                      selectedCategory?.name
                    }{" "}
                    selected
                  </div>
                )}
              </div>

              <div className="category-grid">
                {categories.map((item) => {
                  const Icon = item.icon;
                  const selected =
                    category === item.id;

                  return (
                    <button
                      key={item.id}
                      className={`category-card ${
                        selected
                          ? "category-card-selected"
                          : ""
                      }`}
                      onClick={() =>
                        chooseCategory(
                          item.id
                        )
                      }
                    >
                      <div className="category-top">
                        <div className="category-icon">
                          <Icon size={19} />
                        </div>

                        {selected && (
                          <div className="category-selected">
                            Selected
                          </div>
                        )}
                      </div>

                      <div className="category-name">
                        {item.name}
                      </div>

                      <div className="category-description">
                        {item.description}
                      </div>

                      <div className="category-arrow">
                        <ArrowRight size={17} />
                      </div>
                    </button>
                  );
                })}
              </div>
            </section>

            <section
              className="section category-search-section"
            >
              <div className="category-search-card">
                <div>
                  <div className="eyebrow">
                    PLACE EXPLORER
                  </div>

                  <h2 className="section-heading compact">
                    Choose a real place.
                  </h2>

                  <p className="section-copy compact-copy">
                    Search for a location anywhere in the
                    world and use its geographic context
                    as the starting point for an emergency
                    experiment.
                  </p>
                </div>

                <button
                  className="secondary-button"
                  onClick={() =>
                    scrollToId("search-area")
                  }
                >
                  Search a place
                  <ArrowUpRight size={15} />
                </button>
              </div>
            </section>

            <section
              className="section architecture-section"
              id="architecture"
            >
              <div className="eyebrow">
                BUILT ON AWS
              </div>

              <div className="architecture-heading">
                <div>
                  <h2 className="section-heading">
                    From real place to simulation.
                  </h2>

                  <p className="section-copy">
                    The product separates geographic context
                    from the simulation engine and routes
                    the experiment through an asynchronous
                    AWS pipeline.
                  </p>
                </div>

                <div className="architecture-badge">
                  <ShieldCheck size={17} />
                  <span>
                    AWS-powered workflow
                  </span>
                </div>
              </div>

              <div className="architecture-flow">
                {awsArchitecture.map(
                  (service, index) => {
                    const Icon = service.icon;

                    return (
                      <div
                        className="architecture-step"
                        key={service.name}
                      >
                        <div className="architecture-icon">
                          <Icon size={20} />
                        </div>

                        <div className="architecture-index">
                          {String(
                            index + 1
                          ).padStart(2, "0")}
                        </div>

                        <strong>
                          {service.name}
                        </strong>

                        <span>
                          {service.detail}
                        </span>

                        {index <
                          awsArchitecture.length -
                            1 && (
                          <div className="architecture-arrow">
                            <ArrowRight size={15} />
                          </div>
                        )}
                      </div>
                    );
                  }
                )}
              </div>
            </section>

            <section className="section philosophy-section">
              <div className="philosophy-grid">
                <div>
                  <div className="eyebrow">
                    THE IDEA
                  </div>

                  <h2 className="section-heading">
                    Don't wait for the
                    emergency to learn
                    what breaks.
                  </h2>
                </div>

                <div className="philosophy-card">
                  <div className="philosophy-icon">
                    <Activity size={20} />
                  </div>

                  <h3>
                    Experiment first.
                  </h3>

                  <p>
                    Introduce a hypothetical
                    disruption, run the simulation,
                    inspect measurable outcomes and
                    understand what the experiment
                    exposed.
                  </p>
                </div>

                <div className="philosophy-card">
                  <div className="philosophy-icon">
                    <Map size={20} />
                  </div>

                  <h3>
                    Keep context real.
                  </h3>

                  <p>
                    Real location information is kept
                    separate from the current
                    simulation prototype so the product
                    stays clear about what is measured
                    and what is mapped.
                  </p>
                </div>
              </div>
            </section>
          </main>

          <footer className="footer">
            <div>
              <span className="brand-mark small">
                <span />
              </span>
              <strong>AegisTwin</strong>
            </div>

            <span>
              Test emergencies before they happen.
            </span>

            <button
              onClick={() =>
                window.scrollTo({
                  top: 0,
                  behavior: "smooth",
                })
              }
            >
              Back to top
              <ArrowUpRight size={14} />
            </button>
          </footer>
        </>
      )}

      {screen === "place" && place && (
        <section className="place-screen">
          <div className="place-panel">
            <button
              className="back-button"
              onClick={reset}
            >
              ← Explore another place
            </button>

            <div className="place-category">
              <span />
              REAL PLACE
            </div>

            <h1 className="place-title">
              {place.name}
            </h1>

            <div className="place-address-large">
              <MapPin size={16} />
              <span>
                {placeAddress ||
                  "Location details available from place data"}
              </span>
            </div>

            <div className="place-context-card">
              <div className="context-title">
                <div>
                  <span className="context-label">
                    AEGISTWIN CONTEXT
                  </span>

                  <strong>
                    {selectedCategory?.name ||
                      "Global place"}
                  </strong>
                </div>

                <Globe2 size={18} />
              </div>

              <p>
                Real geographic information is used
                for context. The emergency movement
                remains a simulated experiment.
              </p>
            </div>

            <div className="place-context-stats">
              <div>
                <span>
                  Mapped roads
                </span>
                <strong>
                  {roads.length || 0}
                </strong>
              </div>

              <div>
                <span>
                  Nearby mapped places
                </span>
                <strong>
                  {nearby.length || 0}
                </strong>
              </div>

              <div>
                <span>
                  Category
                </span>
                <strong>
                  {selectedCategory?.name ||
                    "Global"}
                </strong>
              </div>
            </div>

            {selectedRoad && (
              <div className="selected-road-card">
                <Route size={17} />

                <div>
                  <span>
                    SELECTED MAPPED ROUTE
                  </span>

                  <strong>
                    {selectedRoad.name}
                  </strong>
                </div>
              </div>
            )}

            <div className="experiment-heading">
              <div>
                <span>
                  STEP 1
                </span>

                <h2>
                  What do you want to
                  understand?
                </h2>
              </div>

              <p>
                Select one experiment to send to the
                simulation backend.
              </p>
            </div>

            <div className="experiment-grid">
              {currentExperiments.map(
                (item) => {
                  const selected =
                    experiment?.id ===
                    item.id;

                  return (
                    <button
                      key={item.id}
                      className={`experiment-card ${
                        selected
                          ? "experiment-selected"
                          : ""
                      }`}
                      onClick={() => {
                        setExperiment(item);
                        setError("");
                      }}
                    >
                      <div className="experiment-card-top">
                        <div className="experiment-radio">
                          {selected && (
                            <span />
                          )}
                        </div>

                        {selected && (
                          <div className="experiment-selected-label">
                            Selected
                          </div>
                        )}
                      </div>

                      <strong>
                        {item.title}
                      </strong>

                      <p>
                        {item.description}
                      </p>

                      <ChevronRight
                        size={18}
                        className="experiment-chevron"
                      />
                    </button>
                  );
                }
              )}
            </div>

            {experiment && (
              <div className="run-panel">
                <div>
                  <span className="context-label">
                    READY TO TEST
                  </span>

                  <strong>
                    {experiment.title}
                  </strong>

                  <p>
                    The selected experiment will be
                    submitted to the AegisTwin AWS
                    simulation pipeline.
                  </p>
                </div>

                <button
                  className="primary-button"
                  onClick={runExperiment}
                >
                  Test this situation
                  <ArrowRight size={16} />
                </button>
              </div>
            )}

            {error && (
              <div className="inline-error place-error">
                <AlertTriangle size={15} />
                <span>{error}</span>
              </div>
            )}
          </div>

          <div className="place-map-column">
            <MapContainer
              className="map"
              center={[
                Number(
                  place.position?.[1] || 20
                ),
                Number(
                  place.position?.[0] || 0
                ),
              ]}
              zoom={16}
              maxZoom={19}
              scrollWheelZoom
            >
              <TileLayer
                attribution="&copy; OpenStreetMap contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              <FlyToPlace
                place={place}
              />

              {roads.map((road) => {
                const selected =
                  selectedRoad?.id ===
                  road.id;

                return (
                  <Polyline
                    key={road.id}
                    positions={
                      road.coordinates
                    }
                    pathOptions={{
                      color: selected
                        ? "#0071e3"
                        : "#737780",
                      weight: selected
                        ? 7
                        : 3,
                      opacity: selected
                        ? 0.96
                        : 0.5,
                    }}
                    eventHandlers={{
                      click: () =>
                        setSelectedRoad(
                          road
                        ),
                    }}
                  />
                );
              })}

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
                  color: "#ffffff",
                  fillColor: "#0071e3",
                  fillOpacity: 0.95,
                  weight: 4,
                }}
              />

              {nearby.map((item) => (
                <CircleMarker
                  key={item.id}
                  center={
                    item.coordinates
                  }
                  radius={4}
                  pathOptions={{
                    color: "#6e6e73",
                    fillColor:
                      "#ffffff",
                    fillOpacity: 0.9,
                    weight: 1,
                  }}
                />
              ))}
            </MapContainer>

            <div className="map-caption-card">
              <div>
                <span>
                  REAL GEOGRAPHIC CONTEXT
                </span>

                <strong>
                  {place.name}
                </strong>
              </div>

              <MapPin size={16} />
            </div>

            <div className="map-context-note">
              Click a mapped road to select it.
              This geographic context is kept
              separate from the current simulation
              model.
            </div>
          </div>
        </section>
      )}

      {screen === "running" && (
        <section className="running-screen">
          <div className="running-orb">
            <div />
          </div>

          <div className="running-content">
            <div className="eyebrow">
              AEGISTWIN EXPERIMENT
            </div>

            <h1>
              Testing what could
              <br />
              happen.
            </h1>

            <p>
              The selected emergency situation is
              being processed through the AWS
              simulation pipeline.
            </p>

            <div className="running-place">
              <MapPin size={15} />
              <span>
                {place?.name}
              </span>
            </div>

            <div className="running-progress">
              <span />
            </div>

            <div className="running-stages">
              <div className="running-stage active">
                <CheckCircle2 size={15} />
                Request accepted
              </div>

              <div className="running-stage active">
                <Activity size={15} />
                Simulation running
              </div>

              <div className="running-stage">
                <Clock3 size={15} />
                Reading outcome
              </div>
            </div>

            <span className="running-note">
              Real place → scenario → simulation →
              measurable outcome
            </span>
          </div>
        </section>
      )}

      {screen === "result" && result && (
        <section className="result-screen">
          <div className="result-shell">
            <button
              className="back-button"
              onClick={() =>
                setScreen("place")
              }
            >
              ← Test another situation
            </button>

            <div className="result-top">
              <div>
                <div className="place-category">
                  <span />
                  EXPERIMENT COMPLETE
                </div>

                <h1>
                  Here's what happened.
                </h1>

                <p>
                  AegisTwin tested{" "}
                  <strong>
                    {experiment?.title ||
                      "the selected situation"}
                  </strong>{" "}
                  at{" "}
                  <strong>
                    {place?.name}
                  </strong>
                  .
                </p>
              </div>

              <div className="result-status">
                <CheckCircle2 size={18} />
                <span>
                  Simulation complete
                </span>
              </div>
            </div>

            <div className="response-tested-card">
              <div className="response-icon">
                <AlertTriangle size={20} />
              </div>

              <div>
                <span>
                  RESPONSE TESTED
                </span>

                <strong>
                  {experiment?.title ||
                    "Selected emergency response"}
                </strong>

                <p>
                  The experiment was submitted to
                  the AWS simulation pipeline and the
                  returned metrics are shown below.
                </p>
              </div>
            </div>

            <div className="result-outcome-heading">
              <div>
                <span>
                  SIMULATION OUTCOME
                </span>

                <h2>
                  The numbers describe
                  the run.
                </h2>
              </div>

              {normalizedCompletionRate != null && (
                <div className="completion-pill">
                  <CheckCircle2 size={15} />
                  {normalizedCompletionRate.toFixed(
                    0
                  )}
                  % completed
                </div>
              )}
            </div>

            <div className="result-primary-grid">
              <div className="result-primary-card large">
                <span>
                  AVERAGE MOVEMENT TIME
                </span>

                <strong>
                  {metrics.average ??
                    "—"}
                </strong>

                <small>
                  simulated seconds
                </small>

                <div className="primary-card-footer">
                  <Clock3 size={15} />
                  The average movement time for
                  the modeled population.
                </div>
              </div>

              <div className="result-primary-card">
                <span>
                  PEOPLE COMPLETED
                </span>

                <strong>
                  {metrics.completed ??
                    "—"}
                </strong>

                <small>
                  out of{" "}
                  {metrics.population ??
                    "—"}
                </small>

                <div className="primary-card-footer">
                  <Users size={15} />
                  Completed agents in this run.
                </div>
              </div>
            </div>

            <div className="result-metric-grid">
              <div className="result-metric">
                <span>
                  LONGEST
                </span>

                <strong>
                  {metrics.maximum ??
                    "—"}
                </strong>

                <small>
                  simulated seconds
                </small>
              </div>

              <div className="result-metric">
                <span>
                  FASTEST
                </span>

                <strong>
                  {metrics.minimum ??
                    "—"}
                </strong>

                <small>
                  simulated seconds
                </small>
              </div>

              <div className="result-metric">
                <span>
                  REROUTES
                </span>

                <strong>
                  {metrics.reroutes ??
                    "—"}
                </strong>

                <small>
                  route changes
                </small>
              </div>

              <div className="result-metric">
                <span>
                  SIMULATION TIME
                </span>

                <strong>
                  {metrics.simulationTime ??
                    "—"}
                </strong>

                <small>
                  simulated seconds
                </small>
              </div>
            </div>

            <div className="result-meaning-card">
              <div className="meaning-icon">
                <Activity size={19} />
              </div>

              <div>
                <span>
                  WHAT THIS MEANS
                </span>

                <h3>
                  {resultHeadline}
                </h3>

                <p>
                  {resultExplanation}
                </p>
              </div>
            </div>

            <div className="result-context-grid">
              <div className="result-context-card">
                <div className="context-card-icon">
                  <MapPin size={18} />
                </div>

                <span>
                  REAL PLACE
                </span>

                <strong>
                  {place?.name}
                </strong>

                <p>
                  The selected place provides the
                  geographic context shown in the
                  interface.
                </p>
              </div>

              <div className="result-context-card">
                <div className="context-card-icon">
                  <Database size={18} />
                </div>

                <span>
                  AWS RESULT
                </span>

                <strong>
                  Persisted simulation run
                </strong>

                <p>
                  The result is returned from the
                  AegisTwin AWS processing pipeline.
                </p>
              </div>

              <div className="result-context-card">
                <div className="context-card-icon">
                  <ShieldCheck size={18} />
                </div>

                <span>
                  MODEL SCOPE
                </span>

                <strong>
                  Simulation prototype
                </strong>

                <p>
                  Movement values are simulated
                  outputs, not validated real-world
                  predictions.
                </p>
              </div>
            </div>

            <div className="result-disclaimer">
              <AlertTriangle size={15} />

              <span>
                Real geographic data provides the
                context for the selected place.
                Emergency movement is produced by the
                current AegisTwin simulation prototype
                and does not claim to reproduce the
                exact interior layout, real traffic
                state or validated evacuation behavior
                of the selected location.
              </span>
            </div>

            <div className="result-actions">
              <button
                className="primary-button"
                onClick={() =>
                  setScreen("place")
                }
              >
                Test another situation
                <ArrowRight size={16} />
              </button>

              <button
                className="secondary-button"
                onClick={reset}
              >
                Explore another place
                <RotateCcw size={15} />
              </button>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

export default App;