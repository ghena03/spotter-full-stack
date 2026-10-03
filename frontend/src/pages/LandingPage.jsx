import { useNavigate } from "react-router-dom";
import {
  ArrowRight,
  MapPin,
  Route,
  ShieldCheck,
  Zap,
} from "lucide-react";
import spotterLogo from "../assets/spotter.png";
import "./LandingPage.css";

const HOW_IT_WORKS = [
  {
    number: "01",
    icon: MapPin,
    title: "Enter your trip",
    description:
      "Add your current location, pickup, dropoff and cycle hours.",
  },
  {
    number: "02",
    icon: Route,
    title: "Build the route",
    description:
      "Spotter calculates the route, distance and estimated driving time.",
  },
  {
    number: "03",
    icon: ShieldCheck,
    title: "Plan your hours",
    description:
      "HOS rules determine breaks, rest, fuel stops and daily logs.",
  },
];

export default function LandingPage() {
  const navigate = useNavigate();

  const goToPlanner = () => navigate("/planner");

  const goToHowItWorks = () => {
    document
      .getElementById("how-it-works")
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <main className="spotter-landing">
      {/* HEADER */}
      <header className="spotter-header">
        <div className="spotter-brand">
          <img src={spotterLogo} alt="" className="spotter-logo-image" />
          <strong className="spotter-wordmark">SPOTTER</strong>
        </div>
      </header>

      {/* HERO */}
      <section className="spotter-hero">
        <div className="hero-glow hero-glow-pink"></div>
        <div className="hero-glow hero-glow-teal"></div>
        <div className="hero-grid"></div>

        <div className="hero-content">
          <h1>
            Plan smarter.
            <br />
            <span>Drive safer.</span>
          </h1>

          <p className="hero-description">
            Plan your truck trip with intelligent routing and FMCSA
            Hours-of-Service compliance built into every mile.
          </p>

          <div className="hero-actions">
            <button
              className="primary-button"
              onClick={goToPlanner}
              type="button"
            >
              Start Planning
              <ArrowRight size={20} />
            </button>

            <button
              className="secondary-button"
              onClick={goToHowItWorks}
              type="button"
            >
              See how it works
            </button>
          </div>

          <div className="hero-features">
            <div>
              <Route size={18} />
              <span>Smart Routing</span>
            </div>
            <div>
              <ShieldCheck size={18} />
              <span>HOS Compliant</span>
            </div>
            <div>
              <Zap size={18} />
              <span>Fast Planning</span>
            </div>
          </div>
        </div>

        {/* TRUCK ILLUSTRATION */}
        <div className="hero-art" aria-hidden="true">
          <svg viewBox="0 0 560 520" className="hero-art-svg">
            <defs>
              <clipPath id="scene-clip">
                <circle cx="280" cy="260" r="220" />
              </clipPath>
              <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stopColor="#0f2f4d" />
                <stop offset="1" stopColor="#0a2038" />
              </linearGradient>
            </defs>

            {/* scene */}
            <circle
              cx="280"
              cy="260"
              r="220"
              fill="url(#sky)"
              stroke="rgba(187,222,222,0.14)"
            />

            <g clipPath="url(#scene-clip)">
              {/* skyline */}
              <g fill="#0c2640">
                <rect x="70" y="300" width="34" height="70" />
                <rect x="108" y="268" width="28" height="102" />
                <rect x="140" y="310" width="30" height="60" />
                <rect x="396" y="288" width="30" height="82" />
                <rect x="430" y="258" width="34" height="112" />
                <rect x="468" y="304" width="30" height="66" />
              </g>

              {/* soft sun in logo teal */}
              <circle cx="360" cy="150" r="44" fill="rgba(0,128,128,0.35)" />

              {/* road */}
              <rect x="40" y="362" width="480" height="140" fill="#08192c" />
              <line
                className="road-dash"
                x1="40"
                y1="420"
                x2="520"
                y2="420"
                stroke="#bbdede"
                strokeOpacity="0.55"
                strokeWidth="4"
              />

              {/* truck */}
              <g>
                <rect x="150" y="268" width="172" height="82" rx="8" fill="#008080" />
                <rect x="150" y="268" width="172" height="12" rx="6" fill="#00a7a7" />
                <circle cx="182" cy="304" r="8" fill="#ff4d6d" />
                <circle cx="182" cy="328" r="8" fill="#06182d" />
                <circle cx="206" cy="328" r="8" fill="#bbdede" />
                <circle cx="230" cy="328" r="8" fill="#bbdede" />

                <path
                  d="M328 298 h38 l30 26 h18 a6 6 0 0 1 6 6 v20 h-92 z"
                  fill="#ff4d6d"
                />
                <path d="M340 306 h22 l20 18 h-42 z" fill="#06182d" />
                <rect x="150" y="346" width="262" height="7" fill="#0b1a2b" />

                {[190, 240, 366].map((cx) => (
                  <g key={cx}>
                    <circle cx={cx} cy="356" r="17" fill="#06111f" stroke="#172b3d" strokeWidth="5" />
                    <circle cx={cx} cy="356" r="5" fill="#bbdede" />
                  </g>
                ))}
              </g>
            </g>

            {/* floating logo dots */}
            <circle cx="478" cy="108" r="26" fill="#ff4d6d" />
            <circle cx="82" cy="400" r="17" fill="#008080" />
            <circle cx="508" cy="338" r="12" fill="#bbdede" />
            <circle cx="112" cy="96" r="9" fill="#bbdede" fillOpacity="0.6" />
          </svg>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how-it-works" className="how-it-works">
        <div className="section-inner">
          <div className="section-label">HOW IT WORKS</div>

          <h2 className="section-title">
            From starting point
            <br />
            to <span>destination.</span>
          </h2>

          <div className="steps-grid">
            {HOW_IT_WORKS.map((step) => {
              const Icon = step.icon;

              return (
                <article className="step-card" key={step.number}>
                  <div className="step-top">
                    <div className="step-icon">
                      <Icon size={23} />
                    </div>
                    <span className="step-number">{step.number}</span>
                  </div>

                  <div className="step-content">
                    <h3>{step.title}</h3>
                    <p>{step.description}</p>
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      </section>
    </main>
  );
}