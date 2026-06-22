const PLACEHOLDER =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' fill='%23f0f2f5' rx='6'/%3E%3Crect x='16' y='14' width='32' height='24' rx='3' fill='%23d0d4dc'/%3E%3Ccircle cx='24' cy='22' r='4' fill='%23b0b8c8'/%3E%3Cpolygon points='16,38 28,26 36,34 44,24 48,38' fill='%23b0b8c8'/%3E%3Crect x='16' y='44' width='20' height='4' rx='2' fill='%23d0d4dc'/%3E%3Crect x='16' y='52' width='32' height='3' rx='1.5' fill='%23e0e3e8'/%3E%3C/svg%3E";

const s = {
  table: { width: "100%", borderCollapse: "collapse", fontSize: "14px" },
  th: {
    background: "#f8f9fb",
    padding: "10px 14px",
    textAlign: "left",
    fontWeight: "600",
    color: "#555",
    borderBottom: "1px solid #eee",
    fontSize: "13px",
  },
  td: {
    padding: "12px 14px",
    borderBottom: "1px solid #f5f5f5",
    verticalAlign: "middle",
  },
  right: { textAlign: "right" },
  img: {
    width: "56px",
    height: "56px",
    objectFit: "cover",
    borderRadius: "6px",
    border: "1px solid #eee",
    display: "block",
  },
  skuCode: {
    background: "#f0f0f0",
    padding: "2px 6px",
    borderRadius: "4px",
    fontFamily: "monospace",
    fontSize: "12px",
  },
  productName: { fontWeight: "500", color: "#1a1a2e", marginBottom: "2px" },
  trackingRef: { color: "#666", fontSize: "12px" },
};

export default function SKUTable({ lineItems }) {
  if (!lineItems?.length) return <p style={{ color: "#999" }}>No items.</p>;

  return (
    <table style={s.table}>
      <thead>
        <tr>
          <th style={s.th}>Image</th>
          <th style={s.th}>SKU</th>
          <th style={s.th}>Name / Description</th>
          <th style={{ ...s.th, ...s.right }}>Unit Price</th>
          <th style={{ ...s.th, ...s.right }}>Quantity</th>
          <th style={{ ...s.th, ...s.right }}>Line Total</th>
        </tr>
      </thead>
      <tbody>
        {lineItems.map((item, i) => (
          <tr key={i}>
            {/* Image */}
            <td style={s.td}>
              <img
                src={item.image_url || PLACEHOLDER}
                alt={item.product_name || item.sku}
                style={s.img}
                onError={(e) => {
                  e.target.src = PLACEHOLDER;
                }}
              />
            </td>

            {/* SKU code */}
            <td style={s.td}>
              <code style={s.skuCode}>{item.sku}</code>
            </td>

            {/* Name + tracking ref sub-line */}
            <td style={s.td}>
              <div style={s.productName}>{item.product_name}</div>
              {item.tracking_no && (
                <div style={s.trackingRef}>Tracking: {item.tracking_no}</div>
              )}
            </td>

            {/* Unit price */}
            <td style={{ ...s.td, ...s.right }}>
              ${item.unit_price?.toFixed(2)}
            </td>

            {/* Qty */}
            <td style={{ ...s.td, ...s.right }}>{item.qty}</td>

            {/* Line total */}
            <td style={{ ...s.td, ...s.right }}>
              <strong>${item.line_total?.toFixed(2)}</strong>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
