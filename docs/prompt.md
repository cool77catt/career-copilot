# prompt.md

## Overview
I want to build a web full stack application that will automate the process of finding jobs for a user and providing an optimized resume and cover letter they can use in their application.

The main flow consists of:
* Building the user profile through linkedin pdf, current resume, and other information about 
    * Should also prompt the user with quetsions about other experience that may not be reflected in the resume but could actually be very useful when it comes to job hunting and finding jobs that do align even if the current resume is missing some information.
* User inputs job preferences. Application/LLM should ask the user 

* Tips on how to optimize their linkedin profile based on the type of jobs/work they are looking for.

* Job s

## Specifications
- Tech Stack: Next.JS, FastAPI/Python, Postgres, uv for python management, pnpm for typescript
- Deployment: Backend services should be containerized, with scripts to spin the service up and docker on a mac or linux machine.
- Testing: All backend services/apis/db fucntions should have unit tests that utilize pytest. Tests should be concise and use your judgement on which tests should be necessary vs. ones that will take too long to generate and are not worth the time/effort.
- Stages the User will follow
    - User Profile: 
        - ingest pdfs (for example LinkedIn profile pdf, current resume pdf). 
        - Provide a space where the LLM can ask follow up questions to better refine the profile. 
        - provide a chat area where the user can provide additional information about themselves or work they have done that may not be accounted for to build up a profile
        - Whenever they provide more information, the agent should refine the profile and immediately update
        - should be stored as profile.md file (stored as a flat file) with the file location stored in the DB
    - LinkedIn profile optimizer
        - A section that will guide the user on how to best tailer their LinkedIn profile for recruiters
    - Job Search
        - GUI button that user can press to do a search for new jobs. The search should return 3 new jobs that have not previously been recommended.  A "job" is determined to be new if the JD is different or its a different company or job title.
        - Present the user with 3 different jobs that you have found.
        - Search linkedin, indeed, and any other sites you are aware of.  Can tailor based on the preferences of the user, for example if they are looking for startups, can search sites that focus on startup companies.  For the initial phase, lets focus on linkedin and indeed.
    - Job Selection
        - Each job that gets returned from the search should provide the JD, the link, and why the algorithm thinks it would be a good fit.
        - The user can decide whether to persue the job, reject it with a reason so the algorithm can tailer its search, or skip
        - User can go back and look at jobs that they ahve previously accepted, rejected, or skipped.  For each one they can change the status.
        - When a job is "accepted" it will generate a resume and cover letter. The agent can decide to ask the user for more details before tailoring them.  The user shoudl also have the ability to provide feedback to retool the application
        - Track the job description in markdown plus a link to the actual JD
        - Generate a resume.md for the, a cover-letter.md file for the cover letter, and a job-fit.md file that will describe why its a good fit.  These should be versioned so the user can generate new versions based off of profile updates and/or view previous versions.
        - For each job, they can revisit and regenerate a new version of the meterials
    
## Plan of Attack
- I want to first generate the AGENTS.md along with a docs/spec.md and docs/plan.md.
- Next get the project infrastructure in place.  For this, I want the ability to
- After the initial shell is built, lets start going 1 by 1 through the user workflow stages.

## Deliverables
- Deliverable 1: I want to first generate the AGENTS.md along with a docs/spec.md and docs/plan.md
- Deliverable 2: build the project infrastructure
    - FastAPI with a login auth
    - Dockerize the API and create a script to deploy the service
    - create the initial db model for a user.  Track users and add 1 user to start - Name: Chris Carl, email: chris77carl@gmail.com, password: "default"
    - Frontend app that will show the UI features (but just the UI skeleton, dont implement any logic behind them yet.  I just want to get a feel for the flow of the app first)
    - The frontend/backend should use JWT.  
    - Skip the login screen for now, just bypass it and have the app start by calling the backend API to login with my provided credentials.
    - update the README.md file that will explain the rough overview of the project and architecture and setup along with steps on how to run the app
- Remaining delvierables will be laid out later.

    