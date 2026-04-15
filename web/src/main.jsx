import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import CssBaseline from "@mui/material/CssBaseline";
import { ApolloClient, InMemoryCache, ApolloLink } from "@apollo/client";
import { ApolloProvider } from "@apollo/client/react";

import { GraphQLWsLink } from "@apollo/client/link/subscriptions";
import UploadHttpLink from "apollo-upload-client/UploadHttpLink.mjs";
import { createClient } from "graphql-ws";
import { getMainDefinition } from "@apollo/client/utilities";

const host = window.location.host;
const protocol = window.location.protocol === "https:" ? "wss" : "ws";

const wsLink = new GraphQLWsLink(
  createClient({
    url: `${protocol}://${host}/api/v1/workflow`,
  }),
);

const httpLink = new UploadHttpLink({
  uri: `${window.location.protocol}//${host}/api/v1/workflow`,
});

const splitLink = ApolloLink.split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === "OperationDefinition" &&
      definition.operation === "subscription"
    );
  },
  wsLink,
  httpLink,
);

const client = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache(),
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <CssBaseline />
    <ApolloProvider client={client}>
      <App />
    </ApolloProvider>
  </StrictMode>,
);
