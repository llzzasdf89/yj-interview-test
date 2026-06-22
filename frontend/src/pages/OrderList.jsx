import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchOrders } from '../services/api'

const styles = {
  page: { padding: '32px', maxWidth: '1100px', margin: '0 auto' },
  header: { marginBottom: '24px' },
  title: { fontSize: '24px', fontWeight: '700', color: '#1a1a2e' },
  subtitle: { color: '#666', marginTop: '4px', fontSize: '14px' },
  card: { background: '#fff', borderRadius: '10px', boxShadow: '0 1px 4px rgba(0,0,0,.1)', overflow: 'hidden' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { background: '#f8f9fb', padding: '12px 16px', textAlign: 'left', fontSize: '13px', fontWeight: '600', color: '#555', borderBottom: '1px solid #eee' },
  td: { padding: '14px 16px', fontSize: '14px', borderBottom: '1px solid #f0f0f0' },
  statusBadge: (status) => ({
    display: 'inline-block',
    padding: '3px 10px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '600',
    background: status === 'Completed' ? '#e6f7ee' : '#fff3e0',
    color: status === 'Completed' ? '#2e7d32' : '#e65100',
  }),
  viewBtn: {
    padding: '6px 16px',
    borderRadius: '6px',
    border: 'none',
    background: '#4361ee',
    color: '#fff',
    fontSize: '13px',
    cursor: 'pointer',
    fontWeight: '500',
  },
  error: { color: '#c0392b', padding: '16px' },
  loading: { color: '#666', padding: '16px' },
}

export default function OrderList() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchOrders()
      .then(setOrders)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <h1 style={styles.title}>Order Management</h1>
        <p style={styles.subtitle}>All orders — click View to see full details</p>
      </div>

      <div style={styles.card}>
        {loading && <p style={styles.loading}>Loading orders…</p>}
        {error && <p style={styles.error}>Error: {error}</p>}
        {!loading && !error && (
          <table style={styles.table}>
            <thead>
              <tr>
                {['Order No', 'Order Date', 'Customer', 'Company', 'Status', 'Action'].map((h) => (
                  <th key={h} style={styles.th}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.OrderNo}>
                  <td style={styles.td}><strong>{o.OrderNo}</strong></td>
                  <td style={styles.td}>{o.OrderDate}</td>
                  <td style={styles.td}>{o.CustomerName}</td>
                  <td style={styles.td}>{o.CompanyName}</td>
                  <td style={styles.td}>
                    <span style={styles.statusBadge(o.Status)}>{o.Status}</span>
                  </td>
                  <td style={styles.td}>
                    <button
                      style={styles.viewBtn}
                      onClick={() => navigate(`/orders/${encodeURIComponent(o.OrderNo)}`)}
                    >
                      View →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
