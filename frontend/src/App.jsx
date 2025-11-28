import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Signin from './pages/Signin';
import Signup from './pages/Signup';
import Jobs from './pages/Jobs';
import Forum from './pages/Forum';
import Applications from './pages/Applications';
import Notifications from './pages/Notifications';
import MyProfile from './pages/MyProfile';
import Settings from './pages/Settings';
import SearchResults from './pages/SearchResults';
import UserProfile from './pages/UserProfile';
import Messages from './pages/Messages';

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/signin" element={<Signin />} />
        <Route path="/signup" element={<Signup />} />
        
        {/* Protected Routes */}
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/forum" element={<Forum />} />
        <Route path="/applications" element={<Applications />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/myprofile" element={<MyProfile />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/search" element={<SearchResults />} />
        <Route path="/user/:id" element={<UserProfile />} />
        <Route path="/messages" element={<Messages />} />
        {/* Default Redirect */}
        <Route path="/" element={<Signin />} />
      </Routes>
    </Router>
  );
}

export default App;