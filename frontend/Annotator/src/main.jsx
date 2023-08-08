import * as React from "react";
import * as ReactDOM from "react-dom/client";
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import 'bootstrap/dist/css/bootstrap.css'; 

import Root from "./routes/root";
import ErrorPage from "./error-page";
import CreateAccount from "./routes/createAccount";
import Login from "./routes/login"
import ContributedAnnotations from "./routes/Contributions"
import StartAnnotation from "./routes/StartAnnotation"
import CreateAnnotation from "./routes/CreateAnnotation"
import EditItem from "./routes/EditItem"
import Index from "./routes/Index"
import ShowAllObservations from "./routes/allObservations";
import Models from "./routes/Models"
import Model from "./routes/Model"

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    errorElement: <ErrorPage />,
    children: [
      { index: true, element: <Index /> },
      {
        path: "login",
        element: <Login/>
      },
      {
        path: "createAccount",
        element: <CreateAccount />
      },
      {
        path: "allObservations",
        element: <ShowAllObservations />
        },
        {
        path: "Contributions",
        element: <ContributedAnnotations />
        },
        {
        path: "StartAnnotation",
        element: <StartAnnotation />
        },
        {
        path: "CreateAnnotation",
        element: <CreateAnnotation />
        },
        {
        path: "EditItem",
        element: <EditItem />
        },
        {
        path: "Models",
        element: <Models />
        }, 
        {
        path: "Model",
        element: <Model/>
        },        
    ]
  },
]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);