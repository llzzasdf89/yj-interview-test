const s = {
  box: {
    background: "#fafbff",
    border: "1px solid #e8eaf0",
    borderRadius: "8px",
    padding: "20px",
    maxWidth: "360px",
    margin: "auto",
  },
  row: {
    display: "flex",
    justifyContent: "space-between",
    padding: "7px 0",
    fontSize: "14px",
    color: "#444",
  },
  divider: { borderTop: "1px solid #e0e0e0", margin: "10px 0" },
  totalRow: {
    display: "flex",
    justifyContent: "space-between",
    padding: "10px 0 0",
    fontSize: "16px",
    fontWeight: "700",
    color: "#1a1a2e",
  },
  note: {
    fontSize: "11px",
    color: "#aaa",
    marginTop: "8px",
    textAlign: "right",
  },
};

export default function PriceSummary({
  subtotal,
  gst,
  shipmentFee,
  shipmentFeeMethod,
  total,
}) {
  return (
    <div style={s.box}>
      <div style={s.row}>
        <span>Subtotal</span>
        <span>${subtotal?.toFixed(2)}</span>
      </div>
      <div style={s.row}>
        <span>GST (10%)</span>
        <span>${gst?.toFixed(2)}</span>
      </div>
      <div style={s.row}>
        <span>Shipment Fee</span>
        <span>${shipmentFee?.toFixed(2)}</span>
      </div>
      <div style={s.divider} />
      <div style={s.totalRow}>
        <span>Total (AUD)</span>
        <span>${total?.toFixed(2)}</span>
      </div>
      {shipmentFeeMethod === "formula" && (
        <div style={s.note}>
          * Shipment fee estimated (weight-based formula)
        </div>
      )}
    </div>
  );
}
