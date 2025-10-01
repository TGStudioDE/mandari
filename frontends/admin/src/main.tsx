import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'
import { useBrandingStore } from './stores/branding'
import { useAuthStore } from './stores/auth'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Initializer>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </Initializer>
  </React.StrictMode>
)

function Initializer({ children }: { children: React.ReactNode }) {
  const load = useBrandingStore(s => s.loadBranding)
  const fetchMe = useAuthStore(s => s.fetchMe)
  React.useEffect(() => { load(); fetchMe() }, [load, fetchMe])
  return <>{children}</>
}


