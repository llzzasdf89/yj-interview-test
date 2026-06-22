const s = {
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
    gap: "14px",
  },
  card: {
    border: "1px solid #e8eaf0",
    borderRadius: "8px",
    padding: "16px",
    background: "#fafbff",
    marginTop: "8px",
  },
  label: {
    fontSize: "11px",
    fontWeight: "600",
    color: "#888",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
    marginBottom: "4px",
  },
  value: { fontSize: "14px", color: "#1a1a2e", fontWeight: "500" },
  badge: (co) => {
    const base = {
      display: "inline-block",
      padding: "2px 10px",
      borderRadius: "10px",
      fontSize: "12px",
      fontWeight: "600",
    };
    if (co === "StarTrack/AusPost")
      return { ...base, background: "#e8f5e9", color: "#2e7d32" };
    if (co === "AusPost")
      return { ...base, background: "#e3f2fd", color: "#1565c0" };
    if (co === "TNT")
      return { ...base, background: "#fff8e1", color: "#e65100" };
    return { ...base, background: "#f5f5f5", color: "#666" };
  },
  link: { color: "#4361ee", fontSize: "13px", wordBreak: "break-all" },
};

export default function TrackingCard({ tracking }) {
  if (!tracking || !Object.keys(tracking).length) {
    return <p style={{ color: "#999" }}>No tracking information available.</p>;
  }

  return (
    <div>
      {Object.entries(tracking).map(([ref, info]) => (
        <div key={ref} style={s.card}>
          <div style={{ marginBottom: "10px" }}>
            <div style={s.label}>Carrier</div>
            <span style={s.badge(info.company)}>
              {info.company || "Unknown"}
            </span>
          </div>
          <div style={{ marginBottom: "10px" }}>
            <div style={s.label}>Tracking No</div>
            <div style={s.value}>{info.tracking_no || "—"}</div>
          </div>
          <div style={{ marginBottom: "10px" }}>
            <div style={s.label}>Current Status</div>
            {info.tracking_url ? (
              <a
                href={info.tracking_url}
                target="_blank"
                rel="noreferrer"
                style={s.link}
              >
                {info.status}
              </a>
            ) : (
              <div style={s.value}>{info.status || "—"}</div>
            )}
          </div>
          <div>
            <div style={s.label}>Last Update</div>
            <div style={s.value}>{info.last_update || "Not Available"}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
