import React from "react";
import logo from "./logo.svg";
import "./App.css";
import axios from "axios";

//get transactions
//store id which will be part of axios call

function App() {
  const [ID, setID] = React.useState("1");
  const [transactions, setTranscations] = React.useState([]);

  function handleChange(e) {
    setID(e.target.value);
  }

  axios
    .get(`http://localhost:5000/transactions/${ID}`)
    .then(res => console.log(res))
    .catch(err => console.log(err));

  console.log(transactions);

  return (
    <div className="wallet">
      <form>
        <input
          placeholder="Put your id here"
          value={ID}
          onChange={handleChange}
          type="text"
        />
      </form>

      <h6>Amount: {}</h6>
      <section className="transactions"></section>
    </div>
  );
}

export default App;
