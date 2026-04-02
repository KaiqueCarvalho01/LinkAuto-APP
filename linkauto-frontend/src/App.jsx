import React, { useState } from "react";
import Header from "./components/Header";
import Home from "./pages/Home";
import InstructorProfile from "./pages/InstructorProfile";
import MyLessons from "./pages/MyLessons";
import InstructorDashboard from "./pages/InstructorDashboard";
import Login from "./pages/Login";
import { Search, Clock, LayoutDashboard } from "lucide-react";

const MOCK_INSTRUCTORS = [
  {
    id: 1,
    name: "Ricardo Silva",
    neighborhood: "Centro",
    rating: 4.8,
    price: 70,
    photo: "https://i.pravatar.cc/150?u=1",
  },
  {
    id: 2,
    name: "Ana Paula",
    neighborhood: "Parque do Estado",
    rating: 4.9,
    price: 85,
    photo: "https://i.pravatar.cc/150?u=2",
  },
];

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState("student");
  const [activeTab, setActiveTab] = useState("search");
  const [selectedInstructor, setSelectedInstructor] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [showResults, setShowResults] = useState(false);

  // Lista unificada de aulas (RF07)
  const [myLessons, setMyLessons] = useState([
    {
      id: 99,
      instructorName: "Ana Paula",
      date: "30 MAR 2026",
      time: "14:00",
      neighborhood: "Parque do Estado",
      status: "completed",
    },
  ]);

  const handleLogin = (role) => {
    setUserRole(role);
    setIsAuthenticated(true);
    setActiveTab(role === "instructor" ? "dashboard" : "search");
  };

  const handleConfirmBooking = (instructor, time) => {
    const newLesson = {
      id: Date.now(),
      instructorName: instructor.name,
      date: "02 ABR 2026",
      time: time,
      neighborhood: instructor.neighborhood,
      status: "scheduled",
    };
    setMyLessons([...myLessons, newLesson]);
    alert("Solicitação enviada ao instrutor!"); // RF04
    setSelectedInstructor(null);
    setActiveTab("lessons");
  };

  if (!isAuthenticated) return <Login onLogin={handleLogin} />;

  return (
    <div className="flex flex-col min-h-screen bg-gray-100 font-sans pb-20">
      {!selectedInstructor && (
        <Header onLogout={() => setIsAuthenticated(false)} />
      )}

      <div className="flex-grow">
        {selectedInstructor ? (
          <InstructorProfile
            instructor={selectedInstructor}
            onBack={() => setSelectedInstructor(null)}
            onConfirm={(time) => handleConfirmBooking(selectedInstructor, time)}
          />
        ) : activeTab === "search" ? (
          <Home
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            showResults={showResults}
            setShowResults={setShowResults}
            instructors={MOCK_INSTRUCTORS}
            onSelectInstructor={setSelectedInstructor}
          />
        ) : activeTab === "dashboard" ? (
          <InstructorDashboard
            instructorData={{ name: "Ricardo Silva", rating: 4.8 }}
          />
        ) : (
          <MyLessons lessons={myLessons} />
        )}
      </div>

      {/* Nav Bar adaptativa conforme o papel do usuario (RF01) */}
      {!selectedInstructor && (
        <nav className="fixed bottom-0 w-full bg-white border-t border-gray-200 flex justify-around py-4 shadow-lg z-20">
          {userRole === "student" ? (
            <>
              <button
                onClick={() => setActiveTab("search")}
                className={`flex flex-col items-center ${activeTab === "search" ? "text-blue-600" : "text-gray-400"}`}
              >
                <Search size={22} />
                <span className="text-[10px] mt-1 font-bold">Buscar</span>
              </button>
              <button
                onClick={() => setActiveTab("lessons")}
                className={`flex flex-col items-center ${activeTab === "lessons" ? "text-blue-600" : "text-gray-400"}`}
              >
                <Clock size={22} />
                <span className="text-[10px] mt-1 font-bold">Minhas Aulas</span>
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setActiveTab("dashboard")}
                className={`flex flex-col items-center ${activeTab === "dashboard" ? "text-blue-600" : "text-gray-400"}`}
              >
                <LayoutDashboard size={22} />
                <span className="text-[10px] mt-1 font-bold">Dashboard</span>
              </button>
              <button
                onClick={() => setActiveTab("lessons")}
                className={`flex flex-col items-center ${activeTab === "lessons" ? "text-blue-600" : "text-gray-400"}`}
              >
                <Clock size={22} />
                <span className="text-[10px] mt-1 font-bold">Agenda</span>
              </button>
            </>
          )}
        </nav>
      )}
    </div>
  );
}

export default App;
