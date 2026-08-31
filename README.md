# Project README

## 1. Team Members
- **Pranay Raj Kapoor** – NetID: `prk25`  
- **Tina Li** – NetID: `tl853`  
- **Teresa Nguyen** - NetID: `ttn23`
- **Emmett Seto** - NetID: `exs4`

## 2. Architecture

The backend is split into two services (see `Milestones.md`):

| Folder | Service | Port |
| ------ | ------- | ---- |
| `web/` | Main Flask application | 8080 |
| `analytics/` | A/B assignment + event store + metrics API | 8000 |

The web app talks to the analytics service only over HTTP (`web/analytics_client.py`).

## 3. How to run

### With Docker (both services)

```
docker compose up --build
```

Web app on http://localhost:8080, analytics dashboard on http://localhost:8000.
`APP_SECRET_KEY` and the `SMTP_*` values are read from a local `.env` file
(copy `.env.example`).

### Without Docker

```
pip install -r web/requirements.txt -r analytics/requirements.txt
python -m analytics.app                                 # from the repo root, :8000
ANALYTICS_URL=http://localhost:8000 python web/runserver.py 80   # from the repo root
```

After running the server and loading the webpage, you have the option to either login using already registered username and password or sign up for a new faculty or student account. You can sign up for a student or faculty account by selecting "I'm a student" or "I'm a lab member". You can login using the "Login" tab. You also without having logged in have the opportunity to view fellowships, labs, and faculty on the webpage. 

![Login Page](/readme/LoginPage.png)

Once logged in as a `student`, you have the option to view and apply for fellowships of interest. You can also save any fellowships to apply for later. Applying for a fellowship requires submission of a resume and has a section to include a personal statement. 

![Fellowship Page Student](/readme/StudentFellowshipApply.png)

![Application Page Student](/readme/StudentFellowshipApplication.png)

Once you have applied as a `student` for fellowships, you can view your submitted applications in the Applications tab. There is an option to withdraw from any fellowship and also rank your fellowship choices for the matching process. 

![Submitted Applications Student](/readme/SubmittedApplicationsStudent.png)

![Rank Fellowship Choices Student](/readme/RankFellowships.png)

## 4. The Faculty Account and Matching Process

For faculty, there exists an option to add fellowships using the "Add a Fellowship tab" shown below 

![Add Fellowship Faculty](/readme/AddFellowship.png)

Once a faculty has added a fellowship and students have submitted the applications, faculty can view the submitted resumes using the Applicants tab as shown below.

![View Applicants Faculty](/readme/ResumeApplicants.png)

Furthermore, once all students have ranked their fellowships, faculty can save their ranking of students to match students to fellowships using the "Match Now" function. 

![Matching Process](/readme/MatchingProcess.png)

## 5. Profile Page for faculty and students

Students and faculty also have a Profile page to update their information including add a resume, change password. Students have the option to subscribe to new opportunities using the Profile page, receiving an email every time a new opportunity is added.

![Profile Page](/readme/ProfilePage.png)


