import React from 'react';
import { Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import Home from './screens/Home';
import PackageTracking from './screens/PackageTracking';


import PetList from './screens/PetList';
import AddPet from './screens/AddPet';
import Questionnaire from "./screens/Questionnaire";
import Register from './screens/Register';
import Login from './screens/Login';
import AdminRegister from './screens/AdminRegister';
import AdminQuestionnaires from './screens/AdminQuestionnaires';
import MyApplications from './screens/MyApplications';

export default function App() {
  return (
    <>
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/tracking" element={<PackageTracking />} />
        <Route path="/add-pet" element={<AddPet />} />
        <Route path="/questionnaire" element={<Questionnaire />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
	<Route path="/admin-register" element={<AdminRegister />} />
	<Route path="/admin-questionnaires" element={<AdminQuestionnaires />} />
        <Route path="/my-applications" element={<MyApplications />} />
      </Routes>
    </>
  );
}
