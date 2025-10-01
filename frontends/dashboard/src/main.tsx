import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'
import { useBrandingStore } from './stores/branding'

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
  React.useEffect(() => { load() }, [load])
  return <>{children}</>
}


