import React from 'react'
import ReactDOM from 'react-dom/client'
import { SovereignCouncilDashboard } from '../components/SovereignCouncilDashboard'
import './index.css' // Import the high-contrast color scheme

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <SovereignCouncilDashboard />
  </React.StrictMode>,
)
