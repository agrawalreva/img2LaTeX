import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Dataset from './pages/Dataset'
import Train from './pages/Train'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dataset" element={<Dataset />} />
        <Route path="/train" element={<Train />} />
      </Routes>
    </Layout>
  )
}

export default App 