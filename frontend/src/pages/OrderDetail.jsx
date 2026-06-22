import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchOrderDetail } from "../services/api";
import SKUTable from "../components/SKUTable";
import TrackingCard from "../components/TrackingCard";
import PriceSummary from "../components/PriceSummary";

const s = {
  page: { padding: "32px", maxWidth: "1100px", margin: "0 auto" },
  backBtn: {
    display: "inline-flex",
    alignItems: "center",
    gap: "6px",
    marginBottom: "20px",
    padding: "7px 16px",
    borderRadius: "6px",
    border: "1px solid #ddd",
    background: "#fff",
    color: "#333",
    fontSize: "14px",
    cursor: "pointer",
    fontWeight: "500",
  },
  headerCard: {
    background: "#fff",
    borderRadius: "10px",
    boxShadow: "0 1px 4px rgba(0,0,0,.08)",
    padding: "24px",
    marginBottom: "24px",
  },
  orderNo: {
    fontSize: "20px",
    fontWeight: "700",
    color: "#1a1a2e",
    marginBottom: "4px",
  },
  metaGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
    gap: "14px",
    marginTop: "16px",
  },
  metaItem: {},
  metaLabel: {
    fontSize: "11px",
    fontWeight: "600",
    color: "#888",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
  },
  metaValue: { fontSize: "14px", color: "#333", marginTop: "2px" },
  statusBadge: (status) => ({
    display: "inline-block",
    padding: "3px 12px",
    borderRadius: "12px",
    fontSize: "12px",
    fontWeight: "600",
    marginTop: "2px",
    background: status === "Completed" ? "#e6f7ee" : "#fff3e0",
    color: status === "Completed" ? "#2e7d32" : "#e65100",
  }),
  section: {
    background: "#fff",
    borderRadius: "10px",
    boxShadow: "0 1px 4px rgba(0,0,0,.08)",
    padding: "24px",
    marginBottom: "24px",
  },
  sectionTitle: {
    fontSize: "16px",
    fontWeight: "700",
    color: "#1a1a2e",
    marginBottom: "16px",
  },
  error: { color: "#c0392b", padding: "16px" },
  loading: { color: "#666", padding: "40px", textAlign: "center" },
};

export default function OrderDetail() {
  const { orderNo } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOrderDetail(orderNo)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [orderNo]);

  if (loading)
    return (
      <div style={s.page}>
        <p style={s.loading}>Loading order details…</p>
      </div>
    );
  if (error)
    return (
      <div style={s.page}>
        <p style={s.error}>Error: {error}</p>
      </div>
    );

  const {
    order,
    line_items,
    tracking,
    subtotal,
    gst,
    shipment_fee,
    shipment_fee_method,
    total,
  } = data;

  return (
    <div style={s.page}>
      <button style={s.backBtn} onClick={() => navigate("/")}>
        ← Back to Orders
      </button>

      {/* Order Header */}
      <div style={s.headerCard}>
        <div style={s.metaGrid}>
          <div style={s.metaItem}>
            <div style={s.metaLabel}>Order No</div>
            <div
              style={{
                ...s.metaValue,
                fontWeight: "700",
                fontSize: "16px",
                color: "#1a1a2e",
              }}
            >
              {order.OrderNo}
            </div>
          </div>
          <div style={s.metaItem}>
            <div style={s.metaLabel}>Order Date</div>
            <div style={s.metaValue}>{order.OrderDate}</div>
          </div>
          <div style={s.metaItem}>
            <div style={s.metaLabel}>Status</div>
            <span style={s.statusBadge(order.Status)}>{order.Status}</span>
          </div>
          <div style={s.metaItem}>
            <div style={s.metaLabel}>Company Name</div>
            <div style={s.metaValue}>{order.CompanyName}</div>
          </div>
          <div style={s.metaItem}>
            <div style={s.metaLabel}>Customer Name</div>
            <div style={s.metaValue}>{order.CustomerName}</div>
          </div>
          <div style={s.metaItem}>
            <div style={s.metaLabel}>Phone Number</div>
            <div style={s.metaValue}>{order.PhoneNumber}</div>
          </div>
          <div style={s.metaItem}>
            <div style={s.metaLabel}>Email</div>
            <div style={s.metaValue}>{order.Email}</div>
          </div>
          <div style={{ ...s.metaItem, gridColumn: "span 2" }}>
            <div style={s.metaLabel}>Address</div>
            <div style={s.metaValue}>{order.Address}</div>
          </div>
        </div>
      </div>

      {/* SKU Line Items */}
      <div style={s.section}>
        <div style={s.sectionTitle}>Order Items</div>
        <SKUTable lineItems={line_items} />
      </div>

      {/* Price Summary */}
      <div style={s.section}>
        <div style={s.sectionTitle}>Price Summary</div>
        <PriceSummary
          subtotal={subtotal}
          gst={gst}
          shipmentFee={shipment_fee}
          shipmentFeeMethod={shipment_fee_method}
          total={total}
        />
      </div>

      {/* Tracking */}
      <div style={s.section}>
        <div style={s.sectionTitle}>Tracking Information</div>
        <TrackingCard tracking={tracking} />
      </div>
    </div>
  );
}
