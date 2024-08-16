import React, { useEffect } from "react";
import { useLocation } from 'react-router-dom';
const About = () => {
  useEffect(() => {
    document.title = "About";
  }, []);

  return (
    <div>
      <p>Credit to</p>
      <p>Icons</p>
      <p>https://www.flaticon.com/authors/freepik</p>
      <p>https://www.flaticon.com/authors/vectors-market</p>
      <p>https://www.flaticon.com/authors/smashicons</p>
      <p>https://www.flaticon.com/authors/hqrloveq</p>
      <p>https://www.flaticon.com/authors/those-icons</p>
      <p>https://www.flaticon.com/authors/justicon</p>
      <p>https://www.flaticon.com/authors/flat-icons</p>
      <p>https://www.flaticon.com/authors/pongsakornred</p>

      <p>Data</p>
      <p>NETPIE</p>
      <p>Fahfon by cps agri</p>
    </div>
  );
};

export default About;
