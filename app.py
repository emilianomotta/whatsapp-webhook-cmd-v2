
import { useState, useEffect } from "react";
import backgroundImage from "./assets/background.jpg";
import "./index.css";

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [user, setUser] = useState("");
  const [pass, setPass] = useState("");
  const [messages, setMessages] = useState([]);

  const mensajesUnicos = {};
  messages.forEach((msg) => {
    if (msg && msg.numero) {
      mensajesUnicos[msg.numero] = msg; // sobreescribe y deja el último
    }
  });
  const mensajesFiltrados = Object.values(mensajesUnicos);

  const [agenda, setAgenda] = useState({});
  const [showAgenda, setShowAgenda] = useState(false);
  const [showHistorial, setShowHistorial] = useState(false);
  const [editingName, setEditingName] = useState("");
  const [editingPhone, setEditingPhone] = useState("");

  const API_URL = "https://whatsapp-webhook-cmd-v2.onrender.com"; // Cambiar en producción

  useEffect(() => {
    const stored = localStorage.getItem("cmd-login");
    if (stored === "true") setLoggedIn(true);
  }, []);


  useEffect(() => {
    if (!loggedIn) return;
    fetchMessages();
    fetchAgenda();
    const interval = setInterval(() => {
      fetchMessages();
    }, 1000);
    return () => clearInterval(interval);
  }, [loggedIn]);


  const fetchMessages = async () => {
    try {
      const res = await fetch(API_URL + "/mensajes");
      const data = await res.json();
      setMessages(data);
    } catch (err) {
      console.error("Error al cargar mensajes:", err);
    }
  };

  const fetchAgenda = async () => {
    try {
      const res = await fetch(API_URL + "/agenda");
      const data = await res.json();
      setAgenda(data);
    } catch (err) {
      console.error("Error al cargar agenda:", err);
    }
  };

  const handleLogin = () => {
    if (user === "admin" && pass === "cmd2025") {
      localStorage.setItem("cmd-login", "true");
      setLoggedIn(true);
    } else {
      alert("Credenciales incorrectas");
    }
  };

  const handleSaveAgenda = async () => {
    try {
      await fetch(API_URL + "/agenda", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(agenda),
      });
      alert("Agenda guardada correctamente.");
    } catch (err) {
      alert("Error al guardar agenda.");
    }
  };

  return (
    <div
      className="w-screen h-screen bg-cover bg-center flex flex-col items-center"
      style={{ backgroundImage: `url(${backgroundImage})` }}
    >
      <div className="absolute top-5 left-5 flex gap-2">
        <button className="bg-white px-4 py-2 rounded font-bold" onClick={() => {setShowAgenda(true); setShowHistorial(false);}}>Agenda</button>
        <button className="bg-white px-4 py-2 rounded font-bold" onClick={() => {setShowHistorial(true); setShowAgenda(false);}}>Historial</button>
      </div>

      <h1 className="text-white text-3xl font-bold mt-10">CMD Montevideo</h1>

      {!showAgenda && !showHistorial && (
        <div className="flex flex-wrap justify-center items-start gap-4 p-4 max-w-screen-xl overflow-y-auto">


          {mensajesFiltrados.map((msg) => (
            msg && (
              <div
                key={msg.numero}
                className="bg-white bg-opacity-80 rounded-2xl shadow-md p-4 w-[300px] cursor-pointer"
                onClick={() => {
                  const nuevos = messages.filter(m => m.numero !== msg.numero);
                  setMessages(nuevos);
                }}
              >
                <div className="font-bold text-blue-800">{msg.contacto || msg.numero}</div>
                <div className="text-sm text-gray-800">{msg.texto}</div>
                <div className="text-xs text-gray-500 text-right mt-1">{msg.fecha || msg.hora}</div>
              </div>
            )
          ))}


        </div>
      )}


      {showHistorial && (
        <div className="bg-white p-4 mt-6 rounded max-h-[70vh] overflow-y-auto w-[90%] max-w-3xl">
          <h2 className="font-bold mb-2">Historial de Mensajes</h2>
          {mensajesFiltrados.map((msg, index) => (
            <div key={index} className="border-b py-1 text-sm">
              <b>{msg.fecha || msg.hora}</b> - <b>{msg.contacto || msg.numero}</b>: {msg.texto}
            </div>
          ))}
        </div>
      )}

      {showAgenda && (
        <div className="bg-white p-4 mt-6 rounded w-[90%] max-w-2xl">
          <h2 className="font-bold mb-2">Agenda de Contactos</h2>
          {Object.entries(agenda).map(([numero, nombre]) => (
            <div key={numero} className="flex items-center gap-2 mb-1">
              <input value={nombre} onChange={e => {
                setAgenda(prev => ({...prev, [numero]: e.target.value}));
              }} className="border px-2 py-1 w-full" />
              <span className="text-xs text-gray-500">{numero}</span>
              <button className="text-red-500" onClick={() => {
                const copy = {...agenda}; delete copy[numero]; setAgenda(copy);
              }}>X</button>
            </div>
          ))}
          <div className="flex gap-2 mt-4">
            <input value={editingPhone} onChange={e => setEditingPhone(e.target.value)} placeholder="Nuevo número" className="border px-2 py-1 w-1/3" />
            <input value={editingName} onChange={e => setEditingName(e.target.value)} placeholder="Nuevo nombre" className="border px-2 py-1 w-1/2" />
            <button className="bg-green-500 text-white px-3 rounded" onClick={() => {
              if (!editingPhone || !editingName) return;
              setAgenda(prev => ({...prev, [editingPhone]: editingName}));
              setEditingPhone(""); setEditingName("");
            }}>➕</button>
          </div>
          <button className="mt-4 bg-blue-500 text-white px-4 py-2 rounded" onClick={handleSaveAgenda}>Guardar</button>
        </div>
      )}

      <p className="absolute bottom-4 right-4 text-white text-sm">By Motta de Souza</p>
      {!loggedIn && (
        <div className="absolute top-24 bg-white p-4 rounded shadow">
          <h2 className="font-bold mb-2">Ingresar</h2>
          <input placeholder="Usuario" value={user} onChange={e => setUser(e.target.value)} className="border px-2 py-1 w-full mb-2" />
          <input placeholder="Contraseña" type="password" value={pass} onChange={e => setPass(e.target.value)} className="border px-2 py-1 w-full mb-2" />
          <button onClick={handleLogin} className="bg-blue-600 text-white px-4 py-1 rounded">Entrar</button>
        </div>
      )}
    </div>
  );
}

export default App;


@app.route("/mensajes/<numero>", methods=["DELETE"])
def eliminar_mensajes_por_numero(numero):
    global mensajes_en_memoria
    mensajes_en_memoria = [m for m in mensajes_en_memoria if m["numero"] != numero]
    return jsonify({"status": "eliminado", "numero": numero}), 200
