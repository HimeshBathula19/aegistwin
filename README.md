# AegisTwin

> **Test emergencies before they happen.**

AegisTwin is a global emergency intelligence platform for exploring real places, testing hypothetical emergency situations, and understanding simulated response outcomes.

Users can search real-world places such as schools, hospitals, airports, railway stations, malls, public facilities and other locations, inspect their geographic context, choose an experiment, and run it through an AWS-powered simulation pipeline.

---

## Live Demo

**Web App**

https://aegistwin-olive.vercel.app

**GitHub Repository**

https://github.com/HimeshBathula19/aegistwin

---

# The Problem

Emergency planning is often difficult to understand as a static document.

AegisTwin turns emergency planning into an experiment.

Instead of only looking at a static plan, a user can select a real location, introduce a hypothetical emergency situation, run a simulation, and inspect measurable outcomes.

```text
Choose a real place
        ↓
Explore geographic context
        ↓
Choose an emergency situation
        ↓
Submit the experiment
        ↓
AWS simulation pipeline
        ↓
Measure the outcome
        ↓
Understand what happened

The goal is to make emergency-response experimentation easier to explore, explain and communicate.

What AegisTwin Does

AegisTwin combines three layers:

REAL WORLD CONTEXT
        +
EMERGENCY EXPERIMENT
        +
SIMULATION
        =
UNDERSTANDABLE RESULT

The platform allows users to:

Search real places
Explore real geographic context
Inspect surrounding mapped roads and nearby points
Select place-specific emergency experiments
Submit experiments to an AWS backend
Run an agent-based simulation
Retrieve persisted simulation results
Understand the returned metrics
Test another situation
How AegisTwin Works
1. Choose a Place

Users can search for real-world locations using Amazon Location Service.

Examples include:

Schools
Colleges
Universities
Hospitals
Clinics
Airports
Railway stations
Metro and transit locations
Shopping malls
Markets
Public facilities
Government buildings
Entertainment venues
Sports complexes
Hotels
Residential areas
Community spaces
Parks
Museums
Tourist locations

The goal is to let the user begin with a place that already exists in the real world.

2. Explore Geographic Context

After selecting a place, AegisTwin shows its geographic context using a real interactive map.

The current application combines:

Amazon Location Service for place search
OpenStreetMap map tiles
OpenStreetMap / Overpass mapped roads
Nearby mapped points and facilities

Users can inspect the surrounding area and select a mapped road.

The geographic layer provides context for the experiment.

3. Choose an Emergency Experiment

AegisTwin changes the available experiments depending on the selected place category.

Examples include:

People need to leave
An entrance becomes unavailable
A road becomes unavailable
More people arrive
Emergency access changes

Examples of place-aware categories include:

Healthcare
Education
Transport
Commerce
Entertainment
Public & Government
Hospitality
Residential
Infrastructure
Tourism & Public Spaces
Sports
Community
4. Run the Experiment

When the user selects an emergency situation, the frontend submits the experiment to the AegisTwin API.

The request contains information such as:

Selected place
Address
Coordinates
Selected mapped road
Mapped road context
Population size
Emergency scenario
Disruption timing
Simulation intervention

The request is then processed by the AWS backend.

5. AWS Simulation Pipeline

The backend separates the request layer from simulation processing.

React Web App
      ↓
API Gateway
      ↓
AWS Lambda
      ↓
Amazon SQS
      ↓
Simulation Worker
      ↓
Simulation Engine
      ↓
DynamoDB
      ↓
Result returned to frontend

This asynchronous architecture keeps the user-facing API separate from simulation execution.

6. Understand the Result

The result page turns simulation output into understandable information.

The current interface can display metrics such as:

Average movement time
Fastest movement time
Longest movement time
People completed
People failed
Remaining people
Reroutes
Simulation duration
Completion rate

The result page is structured around:

WHAT WAS TESTED
        ↓
SIMULATION OUTCOME
        ↓
MEASURED METRICS
        ↓
WHAT THIS MEANS
        ↓
MODEL SCOPE

This helps users understand what the numbers represent instead of simply showing raw simulation values.

AWS Architecture
                         AegisTwin
                             │
                             ▼
                    React Web Application
                          on Vercel
                             │
                             ▼
                 Amazon Location Service
                 Real place / map context
                             │
                             ▼
                       API Gateway
                             │
                             ▼
                        AWS Lambda
                     API / request layer
                             │
                             ▼
                         Amazon SQS
                   asynchronous simulation jobs
                             │
                             ▼
                    Simulation Worker
                             │
                         AegisTwin
                     Simulation Engine
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
               DynamoDB          CloudWatch
              Run results           Logs
AWS Services Used
Amazon Location Service

Used for real-world place search and geographic context.

AegisTwin uses the Places capability to search for locations by name and return information such as:

Place name
Address
Coordinates
Location categories
Additional place information
Amazon API Gateway

Provides the public API entry point between the React application and the AWS backend.

Example routes include:

/health
/places/search
/simulate
/runs
AWS Lambda

AWS Lambda handles the application API and processing workflow.

The API Lambda handles requests such as:

Health checks
Place search
Simulation submission
Run retrieval

The simulation worker processes queued simulation jobs.

Amazon SQS

Amazon SQS is used to queue simulation jobs asynchronously.

The simplified flow is:

User submits experiment
        ↓
API accepts request
        ↓
SQS receives simulation job
        ↓
Simulation worker receives job
        ↓
Simulation runs

This separates the public API from the simulation worker.

Amazon DynamoDB

DynamoDB stores simulation run information and completed results.

The frontend can then retrieve persisted runs through the API.

Amazon CloudWatch

CloudWatch provides operational logs that help inspect the AWS workflow.

It is especially useful for verifying:

API Lambda execution
SQS delivery
Worker execution
Backend errors
Simulation processing
Simulation Model

The current AegisTwin prototype uses an agent-based network simulation model to represent movement through a simplified environment.

The system can model:

Population size
Locations
Connections
Node capacity
Disruption timing
Blocked nodes
Routing
Rerouting
Movement time
Completion
Failure
Remaining agents
Intervention effects

The simulation engine is separate from the geographic-context layer.

This separation is intentional.

Real geographic context
            │
            │
            ▼
     User understands
     where the place is
            │
            ▼
Emergency experiment
            │
            ▼
   Simulation prototype
            │
            ▼
     Measurable output
Important Model Scope

The selected real place provides geographic context.

The current emergency behavior is produced by the AegisTwin simulation prototype.

AegisTwin does not claim that the current prototype:

Reconstructs the exact interior layout of every real location
Reproduces real-time traffic conditions
Predicts actual human behavior
Predicts real casualties
Provides validated evacuation forecasts
Reproduces the complete physical environment of a selected location

The current system is a hackathon prototype designed for experimentation and understanding simulation outcomes.

Product Flow
GLOBAL DISCOVERY
        ↓
CATEGORY SELECTION
        ↓
REAL PLACE SEARCH
        ↓
PLACE + MAP CONTEXT
        ↓
EMERGENCY EXPERIMENT
        ↓
AWS PROCESSING
        ↓
SIMULATION
        ↓
RESULT
        ↓
INTERPRETATION
Example User Journey
Search:
Naagarjuna Model School
            ↓
Select the real place
            ↓
See the mapped area
            ↓
Inspect surrounding roads
            ↓
Choose an experiment
            ↓
"People need to leave"
            ↓
Test this situation
            ↓
AWS processing
            ↓
Simulation result
            ↓
Average movement
Completion
Longest movement
Reroutes
            ↓
Understand the outcome
Global Place Categories

AegisTwin is designed around the idea that different types of places can produce different emergency questions.

Healthcare

Hospitals, clinics and medical centers.

Example experiments:

Emergency access changes
People need to leave
More people arrive
An access road closes
Education

Schools, colleges, universities and campuses.

Example experiments:

People need to leave
An entrance becomes unavailable
A crowd suddenly grows
A road becomes unavailable
Transport

Airports, railway stations, metro systems and transit hubs.

Example experiments:

An access route closes
Passenger numbers increase
People need to leave
Emergency access changes
Commerce

Shopping malls, markets and business areas.

Example experiments:

People need to leave
An entrance becomes unavailable
Visitor numbers increase
A surrounding road closes
Entertainment

Theatres, cinemas, stadiums and venues.

Example experiments:

Everyone needs to leave
An entrance becomes unavailable
The crowd grows
An access road closes

Other categories provide the same experimentation model through the platform.

Real Geographic Context

The current application uses real mapping information to help the user understand the selected location.

The map can provide:

Selected location
Surrounding roads
Nearby mapped facilities
Mapped route selection
Geographic orientation
Location address

The selected road can be visually highlighted on the map.

However, the map layer should be understood as geographic context, not as proof that the internal simulation fully reproduces that exact real-world road network or building.

Frontend

The frontend is built with:

React
Vite
React Leaflet
Leaflet
Lucide React

The interface uses a clean, light visual language focused on:

Clarity
Large readable typography
Minimal controls
Clear experiment selection
Explainable results
Real geographic context
Frontend Experience

The main experience contains:

Introduction

A cinematic introduction where geographic points assemble into the AegisTwin globe concept.

Global Search

Users can search for real-world places.

Category Explorer

Users can choose categories such as:

Healthcare
Education
Transport
Commerce
Entertainment
Public & Government
Hospitality
Residential
Infrastructure
Tourism & Public Spaces
Sports
Community
Place View

The selected place contains:

Place name
Address
Geographic context
Mapped roads
Nearby mapped points
Category
Experiment selection
Running View

The interface communicates the experiment pipeline while AWS processing takes place.

Result View

The result page presents:

Response Tested
Simulation Outcome
Average Movement
Completion
Longest
Fastest
Reroutes
Simulation Duration
What This Means
Model Scope
Project Structure
aegistwin/
│
├── backend/
│   ├── lambda/
│   │   └── API and AWS Lambda handlers
│   │
│   ├── models/
│   │   └── Request/result contracts
│   │
│   └── worker/
│       └── Simulation worker
│
├── docs/
│   └── Supporting documentation
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── infrastructure/
│   └── AWS deployment/configuration assets
│
└── simulation/
    └── AegisTwin simulation engine
Backend Architecture

The backend follows a layered architecture.

API Request
    ↓
API Gateway
    ↓
Lambda
    ↓
SQS Job
    ↓
Simulation Worker
    ↓
Simulation Engine
    ↓
Result
    ↓
DynamoDB

The frontend does not directly execute the simulation engine.

Simulation Architecture

The simulation layer contains components for:

Environment/network modeling
Population generation
Agent movement
Occupancy
Congestion
Dynamic routing
Scenario execution
Scenario comparison
Bottleneck detection
Diagnosis
Intervention evaluation
Solution experimentation

The simulation engine can be executed independently from the React interface.

Scenario Concept

The AegisTwin scenario pipeline can be understood as:

BASE ENVIRONMENT
       ↓
DISRUPTION
       ↓
AGENT MOVEMENT
       ↓
ROUTING / REROUTING
       ↓
INTERVENTION
       ↓
SIMULATION
       ↓
METRICS
       ↓
EXPLANATION
Example Simulation Metrics

A simulation run can expose values such as:

Population
Completed
Failed
Remaining
Completion Rate
Failure Rate
Minimum Movement Time
Average Movement Time
Maximum Movement Time
Reroutes
Simulation Duration

These metrics allow users to understand the result of an experiment.

Why the Result Is Important

A simulation result should not only display numbers.

The product separates:

WHAT WAS TESTED
        ↓
WHAT HAPPENED
        ↓
WHAT THE NUMBERS MEAN
        ↓
WHAT THE MODEL DOES NOT CLAIM

This is intended to make the system easier to interpret and avoid confusing prototype simulation output with validated real-world prediction.

Why AWS Is Central

AegisTwin does not use AWS only as a hosting layer.

Each AWS service has a distinct responsibility:

Amazon Location Service
        ↓
Real place discovery

API Gateway
        ↓
Public API entry

AWS Lambda
        ↓
Application processing

Amazon SQS
        ↓
Async simulation jobs

Simulation Worker
        ↓
Emergency simulation

DynamoDB
        ↓
Persist results

CloudWatch
        ↓
Logs and observability

The result is a complete cloud workflow from a user interaction to an asynchronous simulation and persisted result.

Deployment
Frontend

The React application is deployed publicly and accessible through:

https://aegistwin-olive.vercel.app

Backend

The AWS backend is deployed in the ap-south-1 region.

The public API provides endpoints for:

Health
Place Search
Simulation Submission
Run Retrieval
Local Development
Clone
git clone https://github.com/HimeshBathula19/aegistwin.git
cd aegistwin
Frontend
cd frontend
npm install
npm run dev
Production build
npm run build

The production build is generated in:

frontend/dist
Example API Flow

A simplified request flow is:

POST /simulate
       ↓
API Gateway
       ↓
AWS Lambda
       ↓
Amazon SQS
       ↓
Simulation Worker
       ↓
AegisTwin Simulation Engine
       ↓
DynamoDB
       ↓
GET /runs
       ↓
React Result Page
Example Health Check

The deployed API provides a health endpoint.

GET /health

The API identifies the service and AWS region when healthy.

Observability

CloudWatch logs are used to inspect the asynchronous backend flow.

The development workflow uses logging to verify:

API request
    ↓
SQS message
    ↓
Lambda consumer
    ↓
Simulation worker
    ↓
Result persistence
Data and Mapping

The project uses a combination of location and mapping data sources.

Amazon Location Service

Used for place discovery and place information.

OpenStreetMap

Used for interactive map tiles.

Overpass API

Used to retrieve mapped nearby roads and relevant mapped points around the selected location.

These sources provide geographic context for the user experience.

Design Philosophy

AegisTwin follows a simple product principle:

Make a complex system understandable through experimentation.

The interface intentionally avoids presenting the simulation as a black box.

The user sees:

Place
   ↓
Situation
   ↓
Experiment
   ↓
Simulation
   ↓
Measurement
   ↓
Explanation
Scope and Limitations

This project is a hackathon prototype.

The current simulation is designed for experimentation within the AegisTwin prototype model.

It should not be interpreted as:

A certified emergency-management platform
A validated evacuation model
A real-time emergency response system
A casualty prediction system
A traffic prediction system
A complete digital reconstruction of every selected location
A replacement for professional emergency planning

Real-world geographic information and simulated emergency behavior are intentionally presented as separate layers.

Future Direction

Potential future improvements include:

Building-specific digital twins
Floor-plan ingestion
Real-time occupancy feeds
More detailed agent behavior
Better road and routing models
Weather and environmental conditions
Historical incident analysis
More advanced optimization
AI-generated scenario explanations
Cloud-scale simulation
Multi-scenario comparison
More detailed intervention testing
Real-time monitoring integrations

These are future directions rather than claims about the current prototype.

Demo

The live application can be accessed here:

https://aegistwin-olive.vercel.app

The demonstration flow is:

AegisTwin introduction
        ↓
Search a real place
        ↓
Select place
        ↓
Explore map
        ↓
Choose category/experiment
        ↓
Run experiment
        ↓
AWS processing
        ↓
Simulation result
        ↓
Understand the outcome
Hackathon Architecture Summary
                         USER
                          │
                          ▼
                    React Frontend
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
   Amazon Location Service      Map / Geographic Context
             │
             ▼
       API Gateway
             │
             ▼
        AWS Lambda
             │
             ▼
        Amazon SQS
             │
             ▼
    Simulation Worker
             │
             ▼
     AegisTwin Engine
             │
             ├──────────────► CloudWatch
             │
             ▼
         DynamoDB
             │
             ▼
       Result Endpoint
             │
             ▼
       React Result UI
Team / Contribution

AegisTwin was developed end-to-end as a solo project.

The project lead handled:

Problem definition
Product concept
UX and interface design
React development
Geographic search integration
Mapping integration
Simulation engine development
AWS architecture
API Gateway integration
Lambda development
SQS workflow
DynamoDB persistence
CloudWatch debugging
Deployment
Testing
Documentation
Demo preparation
Learning

The project provided practical experience across:

React
        +
Mapping
        +
Geospatial search
        +
Agent-based simulation
        +
AWS Lambda
        +
API Gateway
        +
Amazon SQS
        +
DynamoDB
        +
CloudWatch
        +
Deployment

A major architectural lesson was separating:

REAL-WORLD CONTEXT

from:

SIMULATED EMERGENCY BEHAVIOR

This makes the system easier to reason about and communicate honestly.

Built for WeMakeDevs AWS First Commit Hackathon

AegisTwin was built around the idea of solving a real problem with AWS through a focused, working prototype.

The project emphasizes:

A clear user journey
Real geographic context
An asynchronous AWS architecture
A working simulation pipeline
Understandable results
Explainable metrics
Practical cloud integration
Honest model scope
Final Summary

AegisTwin asks:

What could happen here?

The platform lets a user:

Choose a real place
        ↓
Understand the context
        ↓
Introduce a hypothetical emergency
        ↓
Run an AWS-powered simulation
        ↓
Measure the outcome
        ↓
Understand what happened

The long-term vision is to make emergency planning more experimental, visual, measurable and understandable.

The current implementation is a hackathon prototype that demonstrates that workflow end-to-end.


After pasting, save with **Ctrl+S**, then run:

```powershell
cd "C:\Users\Himesh Bathula\Desktop\aegistwin\aegistwin"
git add README.md
git commit -m "Expand complete AegisTwin README"
git push
