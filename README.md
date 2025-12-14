# Project README

## 1. Team Members
- **Pranay Raj Kapoor** – NetID: `prk25`  
- **Tina Li** – NetID: `tl853`  
- **Teresa Nguyen** - NetID: `ttn23`
- **Emmett Seto** - NetID: `exs4`

## 2. How to run the Flask Application

Once you have downloaded the repository and installed all libraries in `requirements.txt`, you can run the server for the application using:

``python runserver.py 80``

After running the server and loading the webpage, you have the option to either login using already registered username and password or sign up for a new faculty or student account. You can sign up for a student or faculty account by selecting "I'm a student" or "I'm a lab member". You can login using the "Login" tab. You also without having logged in have the opportunity to view fellowships, labs, and faculty on the webpage. 

![Login Page](/readme/LoginPage.png)

Once logged in as a `student`, you have the option to view and apply for fellowships of interest. You can also save any fellowships to apply for later. Applying for a fellowship requires submission of a resume and has a section to include a personal statement. 

![Fellowship Page Student](/readme/StudentFellowshipApply.png)

![Application Page Student](/readme/StudentFellowshipApplication.png)

Once you have applied as a `student` for fellowships, you can view your submitted applications in the Applications tab. There is an option to withdraw from any fellowship and also rank your fellowship choices for the matching process. 

![Submitted Applications Student](/readme/SubmittedApplicationsStudent.png)

![Rank Fellowship Choices Student](/readme/RankFellowships.png)

## 3. The Faculty Account and Matching Process

For faculty, there exists an option to add fellowships using the "Add a Fellowship tab" shown below 

![Add Fellowship Faculty](/readme/AddFellowship.png)

Once a faculty has added a fellowship and students have submitted the applications, faculty can view the submitted resumes using the Applicants tab as shown below.

![View Applicants Faculty](/readme/ResumeApplicants.png)

Furthermore, once all students have ranked their fellowships, faculty can save their ranking of students to match students to fellowships using the "Match Now" function. 

![Matching Process](/readme/MatchingProcess.png)

## 4. Profile Page for faculty and students

Students and faculty also have a Profile page to update their information including add a resume, change password. Students have the option to subscribe to new opportunities using the Profile page, receiving an email every time a new opportunity is added.

![Profile Page](/readme/ProfilePage.png)

## 5. Users in the Database and their password

The following are the users in the Database and their login credentials. Changing a password using "Forgot My Password" on the login page sends the user an email to reset their password.

|             Name |  Net ID |    Role | Password |
|-----------------:|--------:|--------:|---------:|
|    Pranay Kapoor |   prk25 | Student |   123456 |
| Tesca Fitzgerald |  tsc123 | Faculty |   123456 |
|       Alan Weide |  adw123 | Faculty |   123456 |
|     Theodore Kim | tkim123 | Faculty |   123456 |
|  Marynel Vazquez |  mvz123 | Faculty |   123456 |
|        Alex Wong |  alx123 | Faculty |   123456 |
|         Rex Ying | ryin123 | Faculty |   123456 |
|      Arman Cohan |  aco123 | Faculty |   123456 |
|   Yongshang Ding |  ydi123 | Faculty |   123456 |
|    Teresa Nguyen |  ter123 | Student |   123456 |


