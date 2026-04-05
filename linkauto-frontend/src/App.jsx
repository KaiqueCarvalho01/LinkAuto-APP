import React, { useState } from "react";
import Header from "./components/Header";
import Home from "./pages/Home";
import SearchPage from "./pages/SearchPage";
import InstructorProfile from "./pages/InstructorProfile";
import MyLessons from "./pages/MyLessons";
import LessonDetails from "./pages/LessonDetails";
import InstructorDashboard from "./pages/InstructorDashboard";
import MyStudents from "./pages/MyStudents";
import Profile from "./pages/Profile";
import Vehicles from "./pages/Vehicles";
import Login from "./pages/Login";
import { Search, Clock, LayoutDashboard, User } from "lucide-react";

const MOCK_INSTRUCTORS = [
  { id: 1, name: "Ricardo Silva", neighborhood: "Centro", rating: 4.8, price: 70, photo: "https://i.pravatar.cc/150?u=1" },
  { id: 2, name: "Ana Paula", neighborhood: "Parque do Estado", rating: 4.9, price: 85, photo: "https://i.pravatar.cc/150?u=2" },
  { id: 3, name: "Marcos Souza", neighborhood: "Mogi Mirim II", rating: 4.7, price: 65, photo: "https://i.pravatar.cc/150?u=3" },
  { id: 4, name: "Beatriz Lopes", neighborhood: "Centro", rating: 4.5, price: 60, photo: "https://i.pravatar.cc/150?u=4" },
  { id: 5, name: "Carlos Eduardo", neighborhood: "Parque do Estado", rating: 4.2, price: 55, photo: "https://i.pravatar.cc/150?u=5" },
  { id: 6, name: "Fernanda Costa", neighborhood: "Mogi Mirim II", rating: 5.0, price: 90, photo: "https://i.pravatar.cc/150?u=6" }
];

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState("student"); 
  const [activeTab, setActiveTab] = useState("search");
  const [isSearchingPage, setIsSearchingPage] = useState(false);
  const [isViewingStudents, setIsViewingStudents] = useState(false);
  const [isViewingVehicles, setIsViewingVehicles] = useState(false);
  const [selectedInstructor, setSelectedInstructor] = useState(null);
  const [selectedLesson, setSelectedLesson] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  
  const [myLessons, setMyLessons] = useState([
    { id: 99, instructorName: "Marcos Silva", date: "30 MAR 2026", time: "14:00", neighborhood: "Centro", status: "completed" }
  ]);

  const [pendingRequests, setPendingRequests] = useState([
    { id: 101, studentName: "João Silva", date: "02 ABR", time: "08:00", neighborhood: "Centro" },
    { id: 102, studentName: "Maria Souza", date: "03 ABR", time: "10:00", neighborhood: "Pq. Estado" }
  ]);

  const [instructorLessons, setInstructorLessons] = useState([]);
  
  const [myStudents] = useState([
    { id: 1, name: "João Silva", totalLessons: 5 },
    { id: 2, name: "Maria Souza", totalLessons: 3 },
    { id: 3, name: "Pedro Alvares", totalLessons: 12 }
  ]);

  const handleLogin = (role) => {
    setUserRole(role);
    setIsAuthenticated(true);
    setActiveTab(role === "instructor" ? "dashboard" : "search");
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUserRole("student");
    setActiveTab("search");
    setIsSearchingPage(false);
    setIsViewingStudents(false);
    setIsViewingVehicles(false);
    setSelectedInstructor(null);
    setSelectedLesson(null);
  };

  const handleConfirmBooking = (instructor, slots) => {
    const newLesson = {
      id: Date.now(),
      instructorName: instructor.name,
      date: "02 ABR 2026",
      time: slots[0],
      neighborhood: instructor.neighborhood,
      status: "scheduled"
    };
    setMyLessons([newLesson, ...myLessons]);
    alert("Solicitação enviada!");
    setSelectedInstructor(null);
    setIsSearchingPage(false);
    setActiveTab("lessons");
  };

  const handleAcceptLesson = (id) => {
    const request = pendingRequests.find(r => r.id === id);
    const confirmedLesson = {
      id: request.id,
      instructorName: "Você",
      studentName: request.studentName,
      date: request.date,
      time: request.time,
      neighborhood: request.neighborhood,
      status: "confirmed"
    };
    setInstructorLessons([confirmedLesson, ...instructorLessons]);
    setPendingRequests(pendingRequests.filter(r => r.id !== id));
    alert(`Aula com ${request.studentName} confirmada!`);
  };

  if (!isAuthenticated) return <Login onLogin={handleLogin} />;

  return (
    <div className="flex flex-col min-h-screen bg-[#F8F9FC] font-sans pb-20">
      
      {!selectedInstructor && !isSearchingPage && !selectedLesson && !isViewingStudents && !isViewingVehicles && activeTab !== 'profile' && (
        <Header onLogout={handleLogout} />
      )}

      <div className="flex-grow">
        {activeTab === 'profile' ? (
          isViewingVehicles ? (
            <Vehicles onBack={() => setIsViewingVehicles(false)} />
          ) : (
            <Profile 
              userData={{ name: userRole === 'instructor' ? 'Ricardo Silva' : 'Aluno LinkAuto', email: 'contato@linkauto.com', role: userRole }} 
              onLogout={handleLogout} 
              onNavigateToVehicles={() => setIsViewingVehicles(true)}
            />
          )
        ) : userRole === "instructor" ? (
          <div className="h-full">
            {isViewingStudents ? (
              <MyStudents students={myStudents} onBack={() => setIsViewingStudents(false)} onSelectStudent={(s) => alert(`Detalhes de ${s.name}`)} />
            ) : activeTab === "dashboard" ? (
              <InstructorDashboard instructorData={{ name: "Ricardo Silva", rating: 4.8 }} requests={pendingRequests} onAccept={handleAcceptLesson} onReject={(id) => setPendingRequests(pendingRequests.filter(r => r.id !== id))} onViewStudents={() => setIsViewingStudents(true)} />
            ) : selectedLesson ? (
              <LessonDetails lesson={selectedLesson} onBack={() => setSelectedLesson(null)} />
            ) : (
              <MyLessons lessons={instructorLessons} isInstructor={true} onSelectLesson={setSelectedLesson} />
            )}
          </div>
        ) : (
          <div className="h-full">
            {selectedInstructor ? (
              <InstructorProfile instructor={selectedInstructor} onBack={() => setSelectedInstructor(null)} onConfirm={handleConfirmBooking} />
            ) : selectedLesson ? (
              <LessonDetails lesson={selectedLesson} onBack={() => setSelectedLesson(null)} />
            ) : isSearchingPage ? (
              <SearchPage searchTerm={searchTerm} setSearchTerm={setSearchTerm} instructors={MOCK_INSTRUCTORS} onSelectInstructor={setSelectedInstructor} onBack={() => setIsSearchingPage(false)} />
            ) : activeTab === "search" ? (
              <Home onStartSearch={() => setIsSearchingPage(true)} />
            ) : (
              <MyLessons lessons={myLessons} onSelectLesson={setSelectedLesson} />
            )}
          </div>
        )}
      </div>

      {!selectedInstructor && !isSearchingPage && !selectedLesson && !isViewingStudents && (
        <nav className="fixed bottom-0 w-full bg-white border-t border-gray-100 flex justify-around py-4 shadow-lg z-20">
          <button onClick={() => {setActiveTab(userRole === 'instructor' ? 'dashboard' : 'search'); setIsViewingStudents(false);}} className={`flex flex-col items-center ${activeTab === (userRole === 'instructor' ? 'dashboard' : 'search') ? "text-blue-600" : "text-gray-300"}`}>
            {userRole === 'instructor' ? <LayoutDashboard size={22} /> : <Search size={22} />}
            <span className="text-[10px] mt-1 font-bold">{userRole === 'instructor' ? 'Painel' : 'Início'}</span>
          </button>
          
          <button onClick={() => {setActiveTab("lessons"); setIsViewingStudents(false);}} className={`flex flex-col items-center ${activeTab === "lessons" ? "text-blue-600" : "text-gray-300"}`}>
            <Clock size={22} /><span className="text-[10px] mt-1 font-bold">{userRole === 'instructor' ? 'Agenda' : 'Aulas'}</span>
          </button>

          <button onClick={() => {setActiveTab("profile"); setIsViewingStudents(false);}} className={`flex flex-col items-center ${activeTab === "profile" ? "text-blue-600" : "text-gray-300"}`}>
            <User size={22} /><span className="text-[10px] mt-1 font-bold">Perfil</span>
          </button>
        </nav>
      )}
    </div>
  );
}

export default App;