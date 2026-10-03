import "./ELDLog.css";

const STATUS_ROWS = [
  {
    key: "OFF_DUTY",
    label: "OFF DUTY",
  },
  {
    key: "SLEEPER_BERTH",
    label: "SLEEPER",
  },
  {
    key: "DRIVING",
    label: "DRIVING",
  },
  {
    key: "ON_DUTY",
    label: "ON DUTY",
  },
];

const clamp = (value, min, max) =>
  Math.max(min, Math.min(max, value));

const formatHour = (hour) => {
  const safeHour = Number.isFinite(Number(hour))
    ? Number(hour)
    : 0;

  const totalMinutes = Math.round(
    safeHour * 60
  );

  const normalizedMinutes =
    ((totalMinutes % 1440) + 1440) % 1440;

  const hours = Math.floor(
    normalizedMinutes / 60
  );

  const minutes =
    normalizedMinutes % 60;

  const suffix = hours >= 12 ? "PM" : "AM";

  const displayHour =
    hours % 12 === 0
      ? 12
      : hours % 12;

  return `${displayHour}:${String(
    minutes
  ).padStart(2, "0")} ${suffix}`;
};

const getStatusKey = (event) => {
  const status = String(
    event?.status || ""
  ).toUpperCase();

  if (status === "OFF_DUTY") {
    return "OFF_DUTY";
  }

  if (status === "SLEEPER_BERTH") {
    return "SLEEPER_BERTH";
  }

  if (status === "DRIVING") {
    return "DRIVING";
  }

  if (status === "ON_DUTY") {
    return "ON_DUTY";
  }

  return "ON_DUTY";
};

const getEventType = (event) => {
  return String(
    event?.event_type ||
      event?.type ||
      ""
  ).toUpperCase();
};

const getEventLabel = (event) => {
  const type = getEventType(event);

  switch (type) {
    case "PICKUP":
      return "Pickup";

    case "DROPOFF":
      return "Dropoff";

    case "FUEL":
      return "Fuel";

    case "BREAK":
      return "Break";

    case "OFF_DUTY":
      return "Rest";

    case "CYCLE_RESTART":
      return "34h Restart";

    case "DRIVING":
      return "Driving";

    case "ON_DUTY":
      return "On Duty";

    default:
      return type
        ? type.replaceAll("_", " ")
        : "Event";
  }
};

const getEventClass = (event) => {
  const type = getEventType(event);

  switch (type) {
    case "PICKUP":
      return "pickup";

    case "DROPOFF":
      return "dropoff";

    case "FUEL":
      return "fuel";

    case "BREAK":
      return "break";

    case "OFF_DUTY":
      return "rest";

    case "CYCLE_RESTART":
      return "restart";

    default:
      return getStatusKey(event).toLowerCase();
  }
};

const getEventIcon = (event) => {
  const type = getEventType(event);

  switch (type) {
    case "PICKUP":
      return "P";

    case "DROPOFF":
      return "D";

    case "FUEL":
      return "F";

    case "BREAK":
      return "B";

    case "OFF_DUTY":
      return "R";

    case "CYCLE_RESTART":
      return "34";

    default:
      return "";
  }
};

const normalizeEvents = (events) => {
  if (!Array.isArray(events)) {
    return [];
  }

  return events
    .map((event, index) => {
      const rawStart = Number(
        event?.start ?? 0
      );

      const rawEnd = Number(
        event?.end ?? rawStart
      );

      const start = clamp(
        Number.isFinite(rawStart)
          ? rawStart
          : 0,
        0,
        24
      );

      const end = clamp(
        Number.isFinite(rawEnd)
          ? rawEnd
          : start,
        0,
        24
      );

      const duration = Math.max(
        0,
        Number(
          event?.duration ??
            end - start
        )
      );

      return {
        ...event,
        index,
        start,
        end,
        duration,
      };
    })
    .filter(
      (event) =>
        event.end > event.start ||
        event.duration > 0
    )
    .sort(
      (a, b) =>
        a.start - b.start
    );
};

const calculateSummary = (events) => {
  const summary = {
    driving: 0,
    onDuty: 0,
    offDuty: 0,
    sleeper: 0,
  };

  events.forEach((event) => {
    const duration = Math.max(
      0,
      Number(event.duration || 0)
    );

    const status = getStatusKey(event);

    if (status === "DRIVING") {
      summary.driving += duration;
    }

    if (status === "ON_DUTY") {
      summary.onDuty += duration;
    }

    if (status === "OFF_DUTY") {
      summary.offDuty += duration;
    }

    if (status === "SLEEPER_BERTH") {
      summary.sleeper += duration;
    }
  });

  return summary;
};

function ELDLog({ dailyLogs = [] }) {
  if (
    !Array.isArray(dailyLogs) ||
    dailyLogs.length === 0
  ) {
    return null;
  }

  return (
    <section className="eld-section">

      {/* =========================
          SECTION HEADER
          ========================= */}

      <div className="eld-section-header">

        <div>
          <span className="eld-section-label">
            DRIVER LOGS
          </span>

          <h2>
            ELD Daily Logs
          </h2>

          <p>
            Generated daily driver logs
            based on the planned HOS
            schedule.
          </p>
        </div>

        <div className="eld-day-count">
          {dailyLogs.length}{" "}
          {dailyLogs.length === 1
            ? "DAY"
            : "DAYS"}
        </div>

      </div>


      {/* =========================
          DAILY LOGS
          ========================= */}

      <div className="eld-days">

        {dailyLogs.map(
          (day, dayIndex) => {
            const events =
              normalizeEvents(
                day?.events
              );

            const summary =
              calculateSummary(
                events
              );

            const dayNumber =
              day?.day ??
              dayIndex + 1;

            return (
              <div
                className="eld-day"
                key={
                  day?.day ??
                  dayIndex
                }
              >

                {/* DAY HEADER */}

                <div className="eld-day-header">

                  <div>
                    <span className="eld-day-label">
                      DRIVER LOG
                    </span>

                    <h3>
                      Day {dayNumber}
                    </h3>
                  </div>

                  <span className="eld-total">
                    24 HOURS
                  </span>

                </div>


                {/* DAILY SUMMARY */}

                <div className="eld-summary">

                  <div className="eld-summary-item">
                    <span className="eld-summary-label">
                      DRIVING
                    </span>

                    <strong>
                      {summary.driving.toFixed(
                        1
                      )}
                      h
                    </strong>
                  </div>

                  <div className="eld-summary-item">
                    <span className="eld-summary-label">
                      ON DUTY
                    </span>

                    <strong>
                      {summary.onDuty.toFixed(
                        1
                      )}
                      h
                    </strong>
                  </div>

                  <div className="eld-summary-item">
                    <span className="eld-summary-label">
                      OFF DUTY
                    </span>

                    <strong>
                      {summary.offDuty.toFixed(
                        1
                      )}
                      h
                    </strong>
                  </div>

                  {summary.sleeper > 0 && (
                    <div className="eld-summary-item">
                      <span className="eld-summary-label">
                        SLEEPER
                      </span>

                      <strong>
                        {summary.sleeper.toFixed(
                          1
                        )}
                        h
                      </strong>
                    </div>
                  )}

                </div>


                {/* ELD GRID */}

                <div className="eld-chart">

                  {/* TIME LABELS */}

                  <div className="eld-hours">

                    {Array.from(
                      { length: 25 },
                      (_, hour) => (
                        <span
                          key={hour}
                          style={{
                            left: `${
                              (hour / 24) *
                              100
                            }%`,
                          }}
                        >
                          {hour === 24
                            ? "12 AM"
                            : formatHour(
                                hour
                              )}
                        </span>
                      )
                    )}

                  </div>


                  {/* STATUS ROWS */}

                  <div className="eld-grid">

                    {STATUS_ROWS.map(
                      (row) => {
                        const rowEvents =
                          events.filter(
                            (event) =>
                              getStatusKey(
                                event
                              ) ===
                              row.key
                          );

                        return (
                          <div
                            className="eld-row"
                            key={row.key}
                          >

                            <div className="eld-row-label">
                              {row.label}
                            </div>

                            <div className="eld-row-track">

                              {/* HOUR GRID */}

                              {Array.from(
                                { length: 25 },
                                (_, hour) => (
                                  <span
                                    key={hour}
                                    className="eld-hour-line"
                                    style={{
                                      left: `${
                                        (hour /
                                          24) *
                                        100
                                      }%`,
                                    }}
                                  />
                                )
                              )}


                              {/* EVENT BARS */}

                              {rowEvents.map(
                                (
                                  event,
                                  eventIndex
                                ) => {
                                  const start =
                                    clamp(
                                      event.start,
                                      0,
                                      24
                                    );

                                  const end =
                                    clamp(
                                      event.end,
                                      0,
                                      24
                                    );

                                  const width =
                                    Math.max(
                                      0.3,
                                      end -
                                        start
                                    );

                                  return (
                                    <div
                                      key={`${row.key}-${eventIndex}`}
                                      className={`eld-event eld-event-${getEventClass(
                                        event
                                      )}`}
                                      title={`${getEventLabel(
                                        event
                                      )}: ${formatHour(
                                        start
                                      )} - ${formatHour(
                                        end
                                      )}`}
                                      style={{
                                        left: `${
                                          (start /
                                            24) *
                                          100
                                        }%`,
                                        width: `${
                                          (width /
                                            24) *
                                          100
                                        }%`,
                                      }}
                                    />
                                  );
                                }
                              )}

                            </div>

                          </div>
                        );
                      }
                    )}

                  </div>

                </div>


                {/* EVENT DETAILS */}

                {events.length > 0 && (
                  <div className="eld-events">

                    {events.map(
                      (
                        event,
                        eventIndex
                      ) => {
                        const eventClass =
                          getEventClass(
                            event
                          );

                        return (
                          <div
                            className="eld-event-item"
                            key={
                              `${eventIndex}-${event.start}-${event.end}`
                            }
                          >

                            <span
                              className={`eld-dot eld-dot-${eventClass}`}
                            >
                              {getEventIcon(
                                event
                              )}
                            </span>

                            <span className="eld-event-type">
                              {getEventLabel(
                                event
                              )}
                            </span>

                            <span className="eld-event-time">
                              {formatHour(
                                event.start
                              )}
                              {" – "}
                              {formatHour(
                                event.end
                              )}
                            </span>

                            <span className="eld-event-duration">
                              {event.duration.toFixed(
                                1
                              )}
                              h
                            </span>

                          </div>
                        );
                      }
                    )}

                  </div>
                )}

              </div>
            );
          }
        )}

      </div>

    </section>
  );
}

export default ELDLog;