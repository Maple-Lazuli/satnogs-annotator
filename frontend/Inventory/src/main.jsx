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
import ShowAllItems from "./routes/allItems"
import OwnedItems from "./routes/OwnedItems"
import CreateItem from "./routes/CreateItem"
import EditItem from "./routes/EditItem"
import Index from "./routes/Index"

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
        path: "allItems",
        element: <ShowAllItems />
        },
        {
        path: "yourItems",
        element: <OwnedItems />
        },
        {
          path: "CreateItem",
          element: <CreateItem />
          },
          {
          path: "EditItem",
          element: <EditItem />
          },
    ]
  },
]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);