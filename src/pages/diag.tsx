import { useState, useEffect } from 'react'
import { api } from '../lib/api'

interface DiagResult {
  endpoint: string
  status: 'success' | 'error'
  statusCode?: number
  latency?: number
  headers?: Record<string, string>
  error?: string
}

export default function DiagPage() {
  const [results, setResults] = useState<DiagResult[]>([])
  const [loading, setLoading] = useState(true)

  // Gate to dev/preview only
  if (process.env.NODE_ENV === 'production') {
    return <div>Not available in production</div>
  }

  useEffect(() => {
    const runDiagnostics = async () => {
      setLoading(true)
      const diagnostics: DiagResult[] = []

      // Test /api/health
      try {
        const start = Date.now()
        const response = await fetch('/api/health', { 
          method: 'GET',
          credentials: 'include'
        })
        const latency = Date.now() - start
        const headers: Record<string, string> = {}
        
        // Extract CORS headers
        response.headers.forEach((value, key) => {
          if (key.toLowerCase().includes('access-control') || key === 'x-request-id') {
            headers[key] = value
          }
        })

        diagnostics.push({
          endpoint: '/api/health',
          status: response.ok ? 'success' : 'error',
          statusCode: response.status,
          latency,
          headers
        })
      } catch (error) {
        diagnostics.push({
          endpoint: '/api/health',
          status: 'error',
          error: error instanceof Error ? error.message : 'Unknown error'
        })
      }

      // Test /api/auth/jwt/login OPTIONS (preflight)
      try {
        const start = Date.now()
        const response = await fetch('/api/auth/jwt/login', {
          method: 'OPTIONS',
          headers: {
            'Origin': window.location.origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
          },
          credentials: 'include'
        })
        const latency = Date.now() - start
        const headers: Record<string, string> = {}
        
        response.headers.forEach((value, key) => {
          if (key.toLowerCase().includes('access-control') || key === 'x-request-id') {
            headers[key] = value
          }
        })

        diagnostics.push({
          endpoint: '/api/auth/jwt/login (OPTIONS)',
          status: response.ok ? 'success' : 'error',
          statusCode: response.status,
          latency,
          headers
        })
      } catch (error) {
        diagnostics.push({
          endpoint: '/api/auth/jwt/login (OPTIONS)',
          status: 'error',
          error: error instanceof Error ? error.message : 'Unknown error'
        })
      }

      setResults(diagnostics)
      setLoading(false)
    }

    runDiagnostics()
  }, [])

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>🔍 API Diagnostics (Dev/Preview Only)</h1>
      
      {loading ? (
        <p>Running diagnostics...</p>
      ) : (
        <table style={{ borderCollapse: 'collapse', width: '100%' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #ccc' }}>
              <th style={{ textAlign: 'left', padding: '8px' }}>Endpoint</th>
              <th style={{ textAlign: 'left', padding: '8px' }}>Status</th>
              <th style={{ textAlign: 'left', padding: '8px' }}>Code</th>
              <th style={{ textAlign: 'left', padding: '8px' }}>Latency</th>
              <th style={{ textAlign: 'left', padding: '8px' }}>CORS Headers</th>
            </tr>
          </thead>
          <tbody>
            {results.map((result, i) => (
              <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '8px' }}>{result.endpoint}</td>
                <td style={{ 
                  padding: '8px',
                  color: result.status === 'success' ? 'green' : 'red'
                }}>
                  {result.status === 'success' ? '✅' : '❌'} {result.status}
                </td>
                <td style={{ padding: '8px' }}>{result.statusCode || 'N/A'}</td>
                <td style={{ padding: '8px' }}>{result.latency ? `${result.latency}ms` : 'N/A'}</td>
                <td style={{ padding: '8px' }}>
                  {result.headers ? (
                    <details>
                      <summary>Headers ({Object.keys(result.headers).length})</summary>
                      <pre style={{ fontSize: '12px', margin: '4px 0' }}>
                        {JSON.stringify(result.headers, null, 2)}
                      </pre>
                    </details>
                  ) : (
                    result.error || 'None'
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      
      <hr style={{ margin: '20px 0' }} />
      
      <h3>Expected Values:</h3>
      <ul>
        <li><code>Access-Control-Allow-Origin</code>: {window.location.origin}</li>
        <li><code>Access-Control-Allow-Credentials</code>: true</li>
        <li><code>X-Request-ID</code>: Should be present</li>
      </ul>
    </div>
  )
}