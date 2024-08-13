import { BrowserRouter, Route, Routes, Redirect } from "react-router-dom";
import { lazy, Suspense } from "react";

//Import page components
//Lazy loading is not necessary
const Home = lazy(() => import("./pages/Home"));
const Fahfon = lazy(() => import("./pages/Fahfon"));
const About = lazy(() => import("./pages/About"));
const HandySense = lazy(() => import("./pages/HandySense"));
const History = lazy(() => import("./pages/History"))
const Specificaiton = lazy(() => import("./pages/Specification"));


function App() {
  return (
    <BrowserRouter basename="/">
        {/* Suspense: when the page is being load */}
        <Suspense fallback={<div>Loading...</div>}>
          <Routes>
            {/* add new routes here */}
            <Route
              path="/"
              element = {
                <Home />
              }
            ></Route>
            <Route
              path = "/fahfon"
              element = {
                <Fahfon />
              }
            ></Route>
            <Route
              path = "/about"
              element = {
                <About />
              }
            ></Route>
            <Route
              path = "/handysense"
              element = {
                <HandySense />
              }
            ></Route>
            <Route
              path = "/historical-data"
              element = {
                <History />
              }
            ></Route>
            <Route
              path="/specification"
              element = {
                <Specificaiton />
              }
            ></Route>
          </Routes>
        </Suspense>
    </BrowserRouter>
  );
}

export default App;
