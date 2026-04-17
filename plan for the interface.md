# React Web Interface implementation Plan

This document outlines the architecture and step-by-step approach to seamlessly fuse a premium ReactJS interface with your existing Java RMI backend.

## The Bridging Concept
Web browsers running React **cannot** communicate using the Java RMI protocol natively. Therefore, we will adapt our `client` module to act as a lightweight **Java API Gateway**. 

The React browser will send a standard web request to the API Gateway. The API Gateway will natively lookup the Server via RMI, get the answer from the LLM/Database, and send it back to the React UI as JSON. This perfectly mimics how enterprise systems operate and smoothly paves the path for your future Spring Boot migration!

## User Review Required

> [!IMPORTANT]  
> Before I start coding, please confirm you are okay with using Java's built-in lightweight HTTP server (`com.sun.net.httpserver.HttpServer`) for the gateway. It adds **no heavy frameworks** and operates cleanly, satisfying your "zero extra dependencies" aesthetic before you transition to Spring Boot later.

> [!TIP]
> Per system instructions, I will design a spectacular, dynamic interface utilizing **Vanilla CSS** instead of Tailwind, applying premium gradients, glassmorphism, and micro-animations to wow the users.

---

## Proposed Changes

### 1. Java API Gateway (Refactoring the Client)

We will transform our terminal client into an automated web server that listens for interface questions.

#### [MODIFY] [HRClient.java](file:///c:/Users/juba839/OneDrive/1-%20isamm%202eme/sem2/1-%20subjects/Architectures%20logicielles/project/smart-hr-assistant/client/src/main/java/com/smarthr/client/HRClient.java)
- Remove the CLI terminal loop.
- Spin up `com.sun.net.httpserver.HttpServer` listening on port `8080`.
- Create a handler for `POST /api/chat` which parses the browser's JSON, triggers `smartHR.askQuestion()`, and returns the LLM's response.
- Implement strict CORS filters so React doesn't get blocked by browser security.

#### [MODIFY] [pom.xml (client)](file:///c:/Users/juba839/OneDrive/1-%20isamm%202eme/sem2/1-%20subjects/Architectures%20logicielles/project/smart-hr-assistant/client/pom.xml)
- Add the `gson` dependency (the identical one the server uses) so the API Gateway can serialize Java into JSON for your web browser.

---

### 2. React Web Frontend (The Fancy Visuals)

We will initialize a completely new microservice folder dedicated exclusively to the web interface.

#### [NEW] `react-ui/` Directory
- Create a modern Vite + React project.
- **`App.jsx`**: Build a conversational "chat" interface (a scrolling list of User messages and AI responses).
- **`App.css`**: Infuse dynamic design rules. Beautiful dark themes, animated typing bubbles, and sleek typography. 
- Implement asynchronous `fetch()` API calls to `http://localhost:8080/api/chat`.

---

### 3. Docker Integration

We will upgrade the orchestrator to spin everything up at once.

#### [MODIFY] [docker-compose.yml](file:///c:/Users/juba839/OneDrive/1-%20isamm%202eme/sem2/1-%20subjects/Architectures%20logicielles/project/smart-hr-assistant/docker-compose.yml)
- Update `hr_client` container to expose port `8080:8080` (so your browser can hit the API). Remove the terminal `tty` instructions.
- Add a new `hr_frontend` container based on Node to serve the React application on port `3000:3000`.

## Open Questions

- We will be utilizing ports `8080` (for the Java Gateway) and `3000` (for the React site) on your machine. **Please confirm these ports are free on your PC!**

## Verification Plan

### Automated/Manual Tests
1. I will execute `npx create-vite` to bootstrap the React UI automatically.
2. Once my coding is complete, you will run `docker-compose up --build -d`.
3. You will open `http://localhost:3000` in your web browser.
4. You will type a question into the beautiful new interface, and verify that the LLM response is fetched gracefully from the Java backend and rendered into a chat bubble!
