import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  Building2,
  ChevronRight,
  Clock3,
  GitBranch,
  LayoutDashboard,
  Map,
  Play,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Users,
  Zap,
} from "lucide-react";
import "./App.css";

const stats = [
  {
    label: "Simulated population",
    value: "1,200",
    detail: "occupants",
    icon: Users,
  },
  {
    label: "Available exits",
    value: "04",
    detail: "operational",
    icon: ArrowUpRight,
  },
  {
    label: "Baseline evacuation",
    value: "07:42",
    detail: "simulation",
    icon: Clock3,
  },
  {
    label: "Critical bottlenecks",
    value: "02",
    detail: "detected",
    icon: AlertTriangle,
  },
];

const navigation = [
  { label: "Overview", icon: LayoutDashboard, active: true },
  { label: "Twin Studio", icon: Map },
  { label: "Scenario Lab", icon: SlidersHorizontal },
  { label: "Simulations", icon: Activity },
  { label: "Resilience", icon: ShieldCheck },
  { label: "What-if", icon: GitBranch },
];

function CampusMap() {
  return (
    <div className="campus-map">
      <div className="map-grid" />

      <div className="map-label label-a">NORTH BLOCK</div>
      <div className="map-label label-b">ACADEMIC BLOCK</div>
      <div className="map-label label-c">CAFETERIA</div>
      <div className="map-label label-d">SOUTH EXIT</div>

      <div className="building building-a">
        <div className="building-title">North Block</div>
        <div className="room-row">
          <span />
          <span />
          <span />
        </div>
        <div className="room-row">
          <span />
          <span />
          <span />
        </div>
      </div>

      <div className="building building-b">
        <div className="building-title">Academic Block</div>
        <div className="room-row">
          <span />
          <span />
          <span />
          <span />
        </div>
        <div className="room-row">
          <span />
          <span />
          <span />
          <span />
        </div>
      </div>

      <div className="building building-c">
        <div className="building-title">Cafeteria</div>
        <div className="cafeteria-core" />
      </div>

      <div className="corridor corridor-one" />
      <div className="corridor corridor-two" />
      <div className="corridor corridor-three" />

      <div className="stair stair-a">A</div>
      <div className="stair stair-b">B</div>

      <div className="exit exit-one">
        <span>EXIT</span>
      </div>

      <div className="exit exit-two">
        <span>EXIT</span>
      </div>

      <div className="agent agent-1" />
      <div className="agent agent-2" />
      <div className="agent agent-3" />
      <div className="agent agent-4" />
      <div className="agent agent-5" />
      <div className="agent agent-6" />
      <div className="agent agent-7" />
      <div className="agent agent-8" />

      <div className="map-status">
        <span className="live-dot" />
        Simulation-ready environment
      </div>
    </div>
  );
}

function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <span />
            <span />
            <span />
          </div>

          <div>
            <div className="brand-name">AegisTwin</div>
            <div className="brand-caption">RESILIENCE INTELLIGENCE</div>
          </div>
        </div>

        <div className="workspace">
          <div className="workspace-label">WORKSPACE</div>

          <div className="workspace-card">
            <div className="workspace-icon">
              <Building2 size={16} />
            </div>

            <div>
              <div className="workspace-name">Campus Twin</div>
              <div className="workspace-status">
                <span className="status-dot" />
                Active environment
              </div>
            </div>

            <ChevronRight size={15} className="workspace-arrow" />
          </div>
        </div>

        <nav className="navigation">
          <div className="navigation-label">OPERATIONS</div>

          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.label}
                className={`nav-item ${item.active ? "active" : ""}`}
              >
                <Icon size={18} strokeWidth={1.8} />
                <span>{item.label}</span>

                {item.label === "Simulations" && (
                  <span className="nav-count">3</span>
                )}
              </button>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <button className="nav-item">
            <Settings size={18} strokeWidth={1.8} />
            <span>Settings</span>
          </button>

          <div className="system-card">
            <div className="system-icon">
              <Zap size={16} />
            </div>

            <div>
              <div className="system-title">Simulation engine</div>
              <div className="system-status">
                <span className="status-dot" />
                Operational
              </div>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="breadcrumb">
              Operations <ChevronRight size={13} /> Overview
            </div>

            <h1>Campus Resilience Twin</h1>
            <p>
              Stress-test your environment before reality tests it.
            </p>
          </div>

          <div className="topbar-actions">
            <div className="system-live">
              <span className="live-dot" />
              SYSTEM LIVE
            </div>

            <button className="simulation-button">
              <Play size={16} fill="currentColor" />
              Run simulation
            </button>
          </div>
        </header>

        <section className="stats-grid">
          {stats.map((stat) => {
            const Icon = stat.icon;

            return (
              <div className="stat-card" key={stat.label}>
                <div className="stat-top">
                  <div className="stat-icon">
                    <Icon size={17} />
                  </div>

                  <span className="stat-detail">{stat.detail}</span>
                </div>

                <div className="stat-value">{stat.value}</div>
                <div className="stat-label">{stat.label}</div>
              </div>
            );
          })}
        </section>

        <section className="main-grid">
          <div className="panel map-panel">
            <div className="panel-header">
              <div>
                <div className="eyebrow">DIGITAL TWIN</div>
                <h2>Campus environment</h2>
              </div>

              <button className="panel-action">
                <Map size={15} />
                Open twin studio
              </button>
            </div>

            <CampusMap />
          </div>

          <div className="panel scenario-panel">
            <div className="panel-header">
              <div>
                <div className="eyebrow">ACTIVE SCENARIO</div>
                <h2>Baseline environment</h2>
              </div>

              <span className="scenario-ready">READY</span>
            </div>

            <div className="scenario-description">
              No disruption is currently being simulated. Run a scenario to
              observe how the modeled environment responds.
            </div>

            <div className="scenario-divider" />

            <div className="scenario-row">
              <span>Population</span>
              <strong>1,200</strong>
            </div>

            <div className="scenario-row">
              <span>Available exits</span>
              <strong>4</strong>
            </div>

            <div className="scenario-row">
              <span>Environment status</span>
              <strong className="healthy">Stable</strong>
            </div>

            <button className="scenario-button">
              <Play size={16} fill="currentColor" />
              Start baseline simulation
            </button>
          </div>
        </section>

        <section className="bottom-grid">
          <div className="panel bottleneck-panel">
            <div className="panel-header">
              <div>
                <div className="eyebrow">RESILIENCE ANALYSIS</div>
                <h2>Known pressure points</h2>
              </div>

              <button className="text-button">
                View analysis <ArrowUpRight size={14} />
              </button>
            </div>

            <div className="bottleneck-list">
              <div className="bottleneck-item">
                <div className="risk-indicator high" />

                <div className="bottleneck-content">
                  <strong>Corridor C</strong>
                  <span>Modeled utilization</span>
                </div>

                <div className="utilization">
                  <strong>92%</strong>
                  <div className="utilization-bar">
                    <div style={{ width: "92%" }} />
                  </div>
                </div>
              </div>

              <div className="bottleneck-item">
                <div className="risk-indicator medium" />

                <div className="bottleneck-content">
                  <strong>Exit B</strong>
                  <span>Modeled utilization</span>
                </div>

                <div className="utilization">
                  <strong>87%</strong>
                  <div className="utilization-bar">
                    <div style={{ width: "87%" }} />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="panel whatif-panel">
            <div className="panel-header">
              <div>
                <div className="eyebrow">WHAT-IF</div>
                <h2>Test a disruption</h2>
              </div>

              <GitBranch size={18} />
            </div>

            <p>
              Change one condition and see how the simulated environment
              responds.
            </p>

            <button className="whatif-button">
              Open scenario lab
              <ArrowUpRight size={15} />
            </button>
          </div>
        </section>

        <footer className="footer">
          <span>AegisTwin</span>
          <span>Digital twin · Agent simulation · Resilience intelligence</span>
          <span>v0.1.0</span>
        </footer>
      </main>
    </div>
  );
}

export default App;