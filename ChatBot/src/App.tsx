
import './App.css'
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom'
import Login from './Pages/login'
import Home from './Pages/Home'

function App() {

  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/home" element={<Home />} />
          {/* Add other routes as needed */}
        </Routes>
      </Router>
    </>
  )
}

export default App
